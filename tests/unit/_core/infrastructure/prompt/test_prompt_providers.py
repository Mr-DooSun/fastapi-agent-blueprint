"""Prompt providers (#447, ADR 066).

The Langfuse provider is exercised against a fake client, so these tests run
without the ``langfuse`` extra. What they pin is the degrade contract: the
provider never raises into a request, never blocks on the caller's thread,
and never attributes a code-text call to a Langfuse version.
"""

from __future__ import annotations

import asyncio
import logging
import threading
from collections.abc import Mapping, Sequence
from types import SimpleNamespace
from typing import Any

import pytest
from structlog.testing import capture_logs

from src._core.domain.protocols.prompt_provider_protocol import (
    PromptProviderProtocol,
)
from src._core.infrastructure.prompt.inline_prompt_provider import (
    InlinePromptProvider,
)
from src._core.infrastructure.prompt.langfuse_prompt_provider import (
    LangfusePromptProvider,
)

_DEFAULT = "You are the code persona."


class _FakeClient:
    def __init__(self, result: Any = None, error: Exception | None = None) -> None:
        self.result = result
        self.error = error
        self.calls: list[dict[str, Any]] = []
        self.thread_names: list[str] = []

    def get_prompt(self, name: str, **kwargs: Any) -> Any:
        self.calls.append({"name": name, **kwargs})
        self.thread_names.append(threading.current_thread().name)
        if self.error is not None:
            raise self.error
        return self.result


def _text_prompt(prompt: Any, version: int = 4, is_fallback: bool = False) -> Any:
    return SimpleNamespace(prompt=prompt, version=version, is_fallback=is_fallback)


def _provider(client: _FakeClient) -> LangfusePromptProvider:
    return LangfusePromptProvider(client, label="staging", cache_ttl_seconds=30)


def _event(logs: Sequence[Mapping[str, Any]], name: str) -> Mapping[str, Any]:
    matches = [e for e in logs if e.get("event") == name]
    assert matches, f"expected a {name} log event, got {logs}"
    return matches[0]


def test_both_providers_satisfy_the_protocol() -> None:
    assert isinstance(InlinePromptProvider(), PromptProviderProtocol)
    assert isinstance(_provider(_FakeClient()), PromptProviderProtocol)


async def test_inline_returns_the_code_text() -> None:
    snapshot = await InlinePromptProvider().get_active("docs_answer", default=_DEFAULT)
    assert snapshot.name == "docs_answer"
    assert snapshot.content == _DEFAULT
    assert snapshot.source == "inline"
    assert snapshot.version is None


async def test_langfuse_success_records_version_and_stable_ref() -> None:
    client = _FakeClient(result=_text_prompt("Operator persona.", version=4))
    snapshot = await _provider(client).get_active("docs_answer", default=_DEFAULT)

    assert snapshot.content == "Operator persona."
    assert snapshot.source == "langfuse"
    assert snapshot.version == "4"
    assert snapshot.external_ref == "docs_answer@4"
    assert snapshot.metadata == {"label": "staging"}


async def test_langfuse_passes_label_ttl_fallback_and_runs_off_loop() -> None:
    client = _FakeClient(result=_text_prompt("p"))
    await _provider(client).get_active("classification", default=_DEFAULT)

    call = client.calls[0]
    assert call["name"] == "classification"
    assert call["label"] == "staging"
    assert call["cache_ttl_seconds"] == 30
    assert call["fallback"] == _DEFAULT
    # The SDK call is synchronous network I/O on a cold cache; it must not
    # run on the event loop's thread.
    assert client.thread_names[0] != threading.main_thread().name


async def test_sdk_fallback_is_recorded_as_inline() -> None:
    # Langfuse unreachable / label missing: the SDK hands back our fallback.
    # The ledger must not claim a Langfuse version for code text.
    client = _FakeClient(result=_text_prompt(_DEFAULT, version=0, is_fallback=True))
    with capture_logs() as logs:
        snapshot = await _provider(client).get_active("docs_answer", default=_DEFAULT)

    assert snapshot.source == "inline"
    assert snapshot.content == _DEFAULT
    assert snapshot.version is None
    assert _event(logs, "prompt_fallback_served")["prompt_name"] == "docs_answer"


async def test_client_exception_degrades_without_leaking_the_message() -> None:
    secret_bearing = RuntimeError("401 for https://pk-lf-x:sk-lf-secret@host/api")
    client = _FakeClient(error=secret_bearing)
    with capture_logs() as logs:
        snapshot = await _provider(client).get_active("docs_answer", default=_DEFAULT)

    assert snapshot.source == "inline"
    assert snapshot.content == _DEFAULT
    event = _event(logs, "prompt_fetch_failed")
    assert event["exc_type"] == "RuntimeError"
    assert "sk-lf-secret" not in repr(logs)


@pytest.mark.parametrize(
    "content",
    [
        [{"role": "system", "content": "chat prompt"}],  # chat-type prompt
        "",
        "   ",
        None,
    ],
)
async def test_unusable_content_degrades_to_inline(content: Any) -> None:
    client = _FakeClient(result=_text_prompt(content))
    with capture_logs() as logs:
        snapshot = await _provider(client).get_active("docs_answer", default=_DEFAULT)

    assert snapshot.source == "inline"
    assert snapshot.content == _DEFAULT
    _event(logs, "prompt_unusable_content")


# ── #447 review R1: the request waits a bounded time, whatever the SDK does ──


class _SlowClient(_FakeClient):
    """Blocks until released — a Langfuse that answers slowly or not at all."""

    def __init__(self) -> None:
        super().__init__(result=_text_prompt("Late persona.", version=9))
        self.release = threading.Event()

    def get_prompt(self, name: str, **kwargs: Any) -> Any:
        self.release.wait(timeout=5)
        return super().get_prompt(name, **kwargs)


async def test_slow_fetch_degrades_at_the_deadline_and_keeps_warming() -> None:
    client = _SlowClient()
    provider = LangfusePromptProvider(
        client, label="production", cache_ttl_seconds=60, request_deadline_seconds=0.05
    )
    with capture_logs() as logs:
        snapshot = await provider.get_active("docs_answer", default=_DEFAULT)

    assert snapshot.source == "inline"
    assert _event(logs, "prompt_fetch_timeout")["deadline_seconds"] == 0.05

    # A second request during the outage joins the fetch already running
    # instead of starting another thread (single-flight per prompt name).
    await provider.get_active("docs_answer", default=_DEFAULT)
    client.release.set()
    await asyncio.sleep(0.05)
    assert len(client.calls) == 1

    # The abandoned fetch still completed; the next call starts a fresh one,
    # which on a real SDK is served from the cache that fetch just filled.
    snapshot = await provider.get_active("docs_answer", default=_DEFAULT)
    assert snapshot.source == "langfuse"
    assert snapshot.version == "9"


async def test_fetch_threads_are_daemons() -> None:
    # A pool worker is joined at interpreter exit, so a fetch sleeping on
    # Retry-After would hold a server shutdown. Daemon threads do not.
    seen: list[bool] = []

    class _Probe(_FakeClient):
        def get_prompt(self, name: str, **kwargs: Any) -> Any:
            seen.append(threading.current_thread().daemon)
            return _text_prompt("p")

    await _provider(_Probe()).get_active("docs_answer", default=_DEFAULT)
    assert seen == [True]


def _real_sdk_provider(
    handler: Any, deadline: float, public_key: str
) -> LangfusePromptProvider:
    httpx = pytest.importorskip("httpx")
    langfuse = pytest.importorskip("langfuse")
    from src._core.infrastructure.prompt.langfuse_prompt_provider import (
        install_langfuse_log_filter,
    )

    install_langfuse_log_filter()
    # A distinct public key per test: the SDK keeps one resource manager
    # (HTTP client + prompt cache) per public key, process-wide, so a second
    # client with the same key would silently reuse the first one's transport.
    client = langfuse.Langfuse(
        public_key=public_key,
        secret_key="sk-lf-test",
        base_url="http://langfuse.invalid",
        tracing_enabled=False,
        httpx_client=httpx.Client(transport=httpx.MockTransport(handler)),
    )
    return LangfusePromptProvider(
        client,
        label="production",
        cache_ttl_seconds=60,
        request_deadline_seconds=deadline,
    )


async def test_real_sdk_retry_after_cannot_stall_the_request() -> None:
    """The R1 probe: 503 + Retry-After: 60 made the SDK sleep ~4 minutes."""
    import time

    def unavailable(request: Any) -> Any:
        import httpx

        return httpx.Response(503, headers={"Retry-After": "60"}, json={})

    provider = _real_sdk_provider(unavailable, deadline=0.5, public_key="pk-lf-r1")
    started = time.perf_counter()
    snapshot = await provider.get_active("r1_probe", default=_DEFAULT)

    assert time.perf_counter() - started < 2
    assert snapshot.source == "inline"


async def test_real_sdk_error_body_never_reaches_the_logs(
    caplog: pytest.LogCaptureFixture,
) -> None:
    """The R2 probe: the SDK logged the response body of a failed fetch."""
    secret = "sk-lf-LEAKED-IN-PROXY-ERROR"

    def unauthorised(request: Any) -> Any:
        import httpx

        return httpx.Response(401, json={"message": f"bad credentials {secret}"})

    provider = _real_sdk_provider(unauthorised, deadline=5, public_key="pk-lf-r2")
    with caplog.at_level(logging.DEBUG), capture_logs() as logs:
        snapshot = await provider.get_active("r2_probe", default=_DEFAULT)

    assert snapshot.source == "inline"
    assert secret not in caplog.text
    assert secret not in repr(logs)
    # Our sanitised replacement is still emitted.
    assert any(e.get("event") == "prompt_fallback_served" for e in logs)


async def test_real_sdk_warm_refresh_error_body_never_reaches_the_logs(
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Review round 2: the warm-cache background refresh logged the body too."""
    import time

    secret = "sk-lf-LEAKED-ON-REFRESH"
    state = {"fail": False}

    def flaky(request: Any) -> Any:
        import httpx

        if state["fail"]:
            return httpx.Response(401, json={"message": f"expired {secret}"})
        return httpx.Response(
            200,
            json={
                "name": "r2_refresh",
                "version": 3,
                "prompt": "Cached persona.",
                "type": "text",
                "config": {},
                "labels": ["production"],
                "tags": [],
            },
        )

    provider = _real_sdk_provider(flaky, deadline=5, public_key="pk-lf-r2-refresh")
    provider._cache_ttl_seconds = 1  # noqa: SLF001 - force a quick expiry
    first = await provider.get_active("r2_refresh", default=_DEFAULT)
    assert first.source == "langfuse"

    state["fail"] = True
    time.sleep(2.1)  # the SDK compares whole epoch seconds
    with caplog.at_level(logging.DEBUG):
        stale = await provider.get_active("r2_refresh", default=_DEFAULT)
        await asyncio.sleep(1.0)  # let the SDK's refresh thread fail and log

    # The failed refresh keeps serving the cached Langfuse version...
    assert (stale.source, stale.version) == ("langfuse", "3")
    # ...and its error text, response body included, is not logged.
    assert secret not in caplog.text


async def test_cancelled_request_still_retrieves_a_late_failure() -> None:
    """Review round 2 R3: cancellation skipped the outcome callback."""
    import gc

    unretrieved: list[dict[str, Any]] = []
    loop = asyncio.get_running_loop()
    previous = loop.get_exception_handler()
    loop.set_exception_handler(lambda _loop, ctx: unretrieved.append(ctx))
    try:

        class _FailsLate(_FakeClient):
            def __init__(self) -> None:
                super().__init__()
                self.release = threading.Event()

            def get_prompt(self, name: str, **kwargs: Any) -> Any:
                self.release.wait(timeout=5)
                raise RuntimeError("late failure body")

        client = _FailsLate()
        provider = LangfusePromptProvider(
            client, label="production", cache_ttl_seconds=60, request_deadline_seconds=5
        )
        task = asyncio.create_task(provider.get_active("r3", default=_DEFAULT))
        await asyncio.sleep(0.05)
        task.cancel()
        with pytest.raises(asyncio.CancelledError):
            await task
        client.release.set()
        await asyncio.sleep(0.1)
        # Drop every reference — the provider's in-flight map holds the
        # concurrent future, which holds the asyncio waiter alive.
        del task, provider, client
        gc.collect()
        await asyncio.sleep(0)
    finally:
        loop.set_exception_handler(previous)

    assert not [c for c in unretrieved if "never retrieved" in str(c.get("message"))]
