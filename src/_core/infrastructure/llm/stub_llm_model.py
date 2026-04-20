"""Stub LLM model used when ``LLM_PROVIDER`` + ``LLM_MODEL`` are unset.

Wraps PydanticAI's ``TestModel`` so any domain that builds an
``Agent(model=llm_model, output_type=...)`` still round-trips in
``make quickstart`` without real LLM credentials. The canned response
shape follows whatever ``output_type`` the consumer declares — it is
not meaningful content, just a valid structured payload.

Matches the ``StubEmbedder`` / ``StubAnswerAgent`` contract: logs a
warning at construction so quickstart users notice that responses are
templated, not generated.
"""

from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger(__name__)


def build_stub_llm_model() -> Any:
    """Build a PydanticAI-compatible stub model.

    Lazy-imports ``pydantic_ai`` so removing the optional extra does not
    break module import — the stub is only instantiated when the
    CoreContainer's ``llm_model`` selector resolves to the disabled
    branch, at which point ``pydantic_ai`` must be available because
    any LLM-consuming domain already requires it.
    """
    try:
        from pydantic_ai.models.test import TestModel
    except ImportError as exc:
        raise ImportError(
            "pydantic-ai is required for the LLM stub model. "
            "Install it with: uv sync --extra pydantic-ai"
        ) from exc

    logger.warning(
        "LLM stub model active — responses are templated, not generated. "
        "Set LLM_PROVIDER + LLM_MODEL for real answers."
    )
    return TestModel()
