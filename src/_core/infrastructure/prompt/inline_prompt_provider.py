from __future__ import annotations

from src._core.domain.value_objects.prompt_snapshot import PromptSnapshot


def inline_snapshot(name: str, default: str) -> PromptSnapshot:
    """The snapshot for a prompt served from code.

    Shared with ``LangfusePromptProvider`` so its degraded path records the
    same shape as the default provider: the ledger must not claim a Langfuse
    version for a call that ran on the code text.
    """
    return PromptSnapshot(name=name, content=default, source="inline")


class InlinePromptProvider:
    """Default provider: the prompt is the text shipped in code.

    Selected when ``PROMPT_PROVIDER`` is unset, so quickstart and every
    environment that never opted in behave exactly as before #447 — except
    that usage rows now name the prompt that served the call.
    """

    async def get_active(self, name: str, *, default: str) -> PromptSnapshot:
        return inline_snapshot(name, default)
