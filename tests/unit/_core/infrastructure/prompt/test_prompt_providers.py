"""Prompt providers (#447, ADR 066).

The Langfuse provider is exercised against a fake client, so these tests run
without the ``langfuse`` extra. What they pin is the degrade contract: the
provider never raises into a request, never blocks on the caller's thread,
and never attributes a code-text call to a Langfuse version.
"""

from __future__ import annotations

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
