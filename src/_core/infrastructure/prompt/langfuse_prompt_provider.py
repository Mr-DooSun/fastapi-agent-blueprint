from __future__ import annotations

import asyncio
from typing import Any, Protocol

import structlog

from src._core.domain.value_objects.prompt_snapshot import PromptSnapshot
from src._core.infrastructure.prompt.inline_prompt_provider import inline_snapshot

_logger = structlog.stdlib.get_logger(__name__)

# Bounds the cold-cache fetch. A warm cache never waits on these: after the TTL
# the SDK serves the stale prompt and refreshes in the background. They only
# matter on the first call per process (or after an eviction) while Langfuse is
# slow or down — the request then waits at most about
# (_MAX_RETRIES + 1) * _FETCH_TIMEOUT_SECONDS before degrading to the code text.
_MAX_RETRIES = 1
_FETCH_TIMEOUT_SECONDS = 3


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


class LangfusePromptProvider:
    """Resolves prompts from Langfuse by label (``PROMPT_PROVIDER=langfuse``).

    Three properties matter more than the happy path:

    - **Never raises into the request.** A fetch failure, an unknown label
      (Langfuse answers 404 and does not fall back to another label), or a
      non-text prompt all degrade to the code ``default`` and log a warning.
    - **Never blocks the event loop.** ``Langfuse.get_prompt`` is synchronous
      and does network I/O on a cold cache, so it runs in a worker thread.
      A warm cache returns immediately; after ``cache_ttl_seconds`` the SDK
      serves the stale value and refreshes in the background.
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
    ) -> None:
        self._client = client
        self._label = label
        self._cache_ttl_seconds = cache_ttl_seconds

    async def get_active(self, name: str, *, default: str) -> PromptSnapshot:
        try:
            prompt = await asyncio.to_thread(
                self._client.get_prompt,
                name,
                label=self._label,
                cache_ttl_seconds=self._cache_ttl_seconds,
                fallback=default,
                max_retries=_MAX_RETRIES,
                fetch_timeout_seconds=_FETCH_TIMEOUT_SECONDS,
            )
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
