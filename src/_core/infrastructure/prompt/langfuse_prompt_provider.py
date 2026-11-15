from __future__ import annotations

import asyncio
import logging
import threading
from concurrent.futures import Future
from typing import Any, Protocol

import structlog

from src._core.domain.value_objects.prompt_snapshot import PromptSnapshot
from src._core.infrastructure.prompt.inline_prompt_provider import inline_snapshot

_logger = structlog.stdlib.get_logger(__name__)

# How long a request waits for a prompt before it is served the code text.
# This is the only bound that holds: the SDK's own knobs do not. `max_retries`
# limits the SDK's outer retry loop only — its generated HTTP client retries
# each attempt twice more and honours `Retry-After` up to 60 s per sleep, and
# `get_prompt` exposes no way to turn that off (#447 review R1: four minutes
# measured against a 503 with `Retry-After: 60`).
#
# So the request path never waits on the SDK call itself. The fetch runs on a
# dedicated executor; the request waits at most this long, then degrades. The
# fetch keeps going in the background and, when it lands, fills the SDK cache
# for the calls after it. A warm cache returns well inside the deadline.
_REQUEST_DEADLINE_SECONDS = 3.0
# Per HTTP attempt, and the SDK's outer retries are turned off: the background
# fetch is single-flight per prompt name (see `get_active`), so retrying sooner
# from the next request is cheaper than stacking retries inside one thread.
_FETCH_TIMEOUT_SECONDS = 3
_MAX_RETRIES = 0
# Each fetch runs on its own *daemon* thread rather than a ThreadPoolExecutor
# or `asyncio.to_thread`. Pool workers are joined at interpreter exit, so a
# fetch sleeping on `Retry-After` would hold a server or worker shutdown for
# minutes; and the default executor is shared app-wide, so a stuck Langfuse
# could starve unrelated `to_thread` callers. Single-flight per prompt name
# bounds the thread count to the number of prompt names.

# The SDK logs fetch failures itself, before our code sees them, with the
# exception text interpolated — and that text includes the HTTP response body
# (#447 review R2). Three records do this in 4.18.0: two on the request path,
# and one from the warm-cache background refresh thread, which no request ever
# observes. All three are dropped. The request-path failures are replaced by
# `get_active`'s sanitised events (`prompt_fetch_failed` /
# `prompt_fallback_served`); a failed background refresh leaves the previous
# version in the cache, which is what keeps being served.
_SDK_RAW_ERROR_PREFIXES = (
    "Error while fetching prompt",
    "Returning fallback prompt",
    "PromptCacheRefreshConsumer encountered an error",
)


class _DropRawPromptErrors(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        return not (
            isinstance(record.msg, str)
            and record.msg.startswith(_SDK_RAW_ERROR_PREFIXES)
        )


def install_langfuse_log_filter() -> None:
    """Attach the filter to the SDK's ``langfuse`` logger, once per process."""
    sdk_logger = logging.getLogger("langfuse")
    if not any(isinstance(f, _DropRawPromptErrors) for f in sdk_logger.filters):
        sdk_logger.addFilter(_DropRawPromptErrors())


class _SupportsGetPrompt(Protocol):
    """The one ``langfuse.Langfuse`` method this provider uses.

    Typed as a consumer-local protocol so the unit tests can pass a fake
    without the ``langfuse`` extra installed.
    """

    def get_prompt(
        self,
        name: str,
        *,
        label: str | None = ...,
        cache_ttl_seconds: int | None = ...,
        fallback: Any = ...,
        max_retries: int | None = ...,
        fetch_timeout_seconds: int | None = ...,
    ) -> Any: ...


def _consume_outcome(waiter: asyncio.Future[Any]) -> None:
    if not waiter.cancelled():
        waiter.exception()


class LangfusePromptProvider:
    """Resolves prompts from Langfuse by label (``PROMPT_PROVIDER=langfuse``).

    Three properties matter more than the happy path:

    - **Never raises into the request.** A fetch failure, an unknown label
      (Langfuse answers 404 and does not fall back to another label), or a
      non-text prompt all degrade to the code ``default`` and log a warning.
    - **Never makes a request wait long.** ``Langfuse.get_prompt`` is
      synchronous and does network I/O on a cold cache, so it runs on a
      dedicated executor and the request waits at most
      ``_REQUEST_DEADLINE_SECONDS``. Fetches are single-flight per prompt
      name, so an outage cannot pile up threads. A warm cache returns
      immediately; after ``cache_ttl_seconds`` the SDK serves the stale value
      and refreshes in its own background thread.
    - **Never misreports the source.** When Langfuse hands back the fallback
      (``is_fallback``), the snapshot says ``inline`` — the ledger must not
      attribute a code-text call to a Langfuse version.
    """

    def __init__(
        self,
        client: _SupportsGetPrompt,
        *,
        label: str,
        cache_ttl_seconds: int,
        request_deadline_seconds: float = _REQUEST_DEADLINE_SECONDS,
    ) -> None:
        self._client = client
        self._label = label
        self._cache_ttl_seconds = cache_ttl_seconds
        self._deadline = request_deadline_seconds
        self._in_flight: dict[str, Future[Any]] = {}
        self._lock = threading.Lock()

    def _fetch(self, name: str, default: str) -> Future[Any]:
        """Start a fetch for ``name`` unless one is already running."""
        with self._lock:
            running = self._in_flight.get(name)
            if running is not None and not running.done():
                return running
            future: Future[Any] = Future()
            self._in_flight[name] = future

        def run() -> None:
            try:
                future.set_result(
                    self._client.get_prompt(
                        name,
                        label=self._label,
                        cache_ttl_seconds=self._cache_ttl_seconds,
                        fallback=default,
                        max_retries=_MAX_RETRIES,
                        fetch_timeout_seconds=_FETCH_TIMEOUT_SECONDS,
                    )
                )
            except BaseException as exc:
                future.set_exception(exc)

        threading.Thread(target=run, name=f"prompt-fetch-{name}", daemon=True).start()
        return future

    async def get_active(self, name: str, *, default: str) -> PromptSnapshot:
        waiter = asyncio.wrap_future(self._fetch(name, default))
        # Registered before awaiting, so the outcome is retrieved on every
        # path — including this task being cancelled mid-wait, which never
        # reaches the timeout branch (#447 review R3). Without it a late
        # failure surfaces as "Future exception was never retrieved", with the
        # exception text, through the loop's default handler.
        waiter.add_done_callback(_consume_outcome)
        # asyncio.wait, not wait_for: a deadline must abandon the wait, not the
        # fetch — the fetch finishing later is what warms the cache.
        done, _ = await asyncio.wait({waiter}, timeout=self._deadline)
        if not done:
            _logger.warning(
                "prompt_fetch_timeout",
                prompt_name=name,
                label=self._label,
                deadline_seconds=self._deadline,
            )
            return inline_snapshot(name, default)
        try:
            prompt = waiter.result()
        except Exception as exc:
            # exc_type only: an SDK error message can carry the request URL,
            # and the keys are credentials.
            _logger.warning(
                "prompt_fetch_failed",
                prompt_name=name,
                label=self._label,
                exc_type=type(exc).__name__,
            )
            return inline_snapshot(name, default)

        if getattr(prompt, "is_fallback", False):
            _logger.warning(
                "prompt_fallback_served", prompt_name=name, label=self._label
            )
            return inline_snapshot(name, default)

        content = getattr(prompt, "prompt", None)
        if not isinstance(content, str) or not content.strip():
            # A chat-type prompt (list of messages) or an empty text prompt
            # cannot fill a persona slot.
            _logger.warning(
                "prompt_unusable_content",
                prompt_name=name,
                label=self._label,
                content_type=type(content).__name__,
            )
            return inline_snapshot(name, default)

        version = getattr(prompt, "version", None)
        version_str = str(version) if version is not None else None
        return PromptSnapshot(
            name=name,
            content=content,
            version=version_str,
            source="langfuse",
            # Langfuse versions are immutable, so name@version identifies the
            # exact text — unlike the label, which moves (ADR 046 §3).
            external_ref=f"{name}@{version_str}" if version_str else None,
            metadata={"label": self._label},
        )


def build_langfuse_prompt_provider(
    *,
    public_key: str,
    secret_key: str,
    base_url: str,
    label: str,
    cache_ttl_seconds: int,
) -> LangfusePromptProvider:
    """Construct the provider with a real client. Lazy-imports ``langfuse``."""
    try:
        from langfuse import Langfuse
    except ImportError as exc:
        raise ImportError(
            "langfuse is required for PROMPT_PROVIDER=langfuse. "
            "Install it with: uv sync --extra langfuse"
        ) from exc

    install_langfuse_log_filter()
    # tracing_enabled=False: this client exists for prompt management only.
    # Trace export stays on the OTEL path (ADR 046), and a second, implicit
    # trace pipeline would duplicate it.
    client = Langfuse(
        public_key=public_key,
        secret_key=secret_key,
        base_url=base_url,
        tracing_enabled=False,
    )
    return LangfusePromptProvider(
        client, label=label, cache_ttl_seconds=cache_ttl_seconds
    )
