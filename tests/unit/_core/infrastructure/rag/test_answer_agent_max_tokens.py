"""max_tokens wiring into the RAG agent (#197 Phase 4 / #210)."""

from __future__ import annotations

import pytest

from src._core.infrastructure.rag.pydantic_ai_answer_agent import (
    PydanticAIAnswerAgent,
    _model_settings,
)

pytest.importorskip("pydantic_ai")
from pydantic_ai.models.test import TestModel  # noqa: E402


def test_model_settings_omitted_when_uncapped():
    assert _model_settings(None) is None
    assert _model_settings(0) is None  # falsy → omit


def test_model_settings_set_when_capped():
    assert _model_settings(2048) == {"max_tokens": 2048}


def test_agent_carries_max_tokens_in_model_settings():
    agent = PydanticAIAnswerAgent(llm_model=TestModel(), max_tokens=1234)
    # PydanticAI stores constructor model_settings on the Agent.
    settings = getattr(agent._agent, "model_settings", None)  # noqa: SLF001
    assert settings == {"max_tokens": 1234}


def test_agent_omits_model_settings_when_uncapped():
    agent = PydanticAIAnswerAgent(llm_model=TestModel(), max_tokens=None)
    settings = getattr(agent._agent, "model_settings", None)  # noqa: SLF001
    assert settings is None
