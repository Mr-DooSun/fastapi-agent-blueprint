"""max_tokens wiring into the classifier agent (#197 Phase 4 / #210)."""

from __future__ import annotations

import pytest

from src.classification.infrastructure.classifier.pydantic_ai_classifier import (
    PydanticAIClassifier,
    _model_settings,
)

pytest.importorskip("pydantic_ai")
from pydantic_ai.models.test import TestModel  # noqa: E402


def test_model_settings_omitted_when_uncapped():
    assert _model_settings(None) is None
    assert _model_settings(0) is None


def test_model_settings_set_when_capped():
    assert _model_settings(512) == {"max_tokens": 512}


def test_agent_carries_max_tokens():
    clf = PydanticAIClassifier(llm_model=TestModel(), max_tokens=777)
    assert getattr(clf._agent, "model_settings", None) == {"max_tokens": 777}  # noqa: SLF001


def test_agent_omits_when_uncapped():
    clf = PydanticAIClassifier(llm_model=TestModel(), max_tokens=None)
    assert getattr(clf._agent, "model_settings", None) is None  # noqa: SLF001
