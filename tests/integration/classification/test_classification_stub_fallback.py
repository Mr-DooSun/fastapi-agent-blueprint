"""Classification graceful degradation with CoreContainer's LLM stub (#101 Part B).

When ``LLM_PROVIDER`` / ``LLM_MODEL`` are unset, ``core_container.llm_model``
resolves to ``build_stub_llm_model()`` → a PydanticAI ``TestModel``. Feeding
that into ``ClassificationService`` must:

- not raise at construction time (``Agent(model=TestModel())`` is supported),
- produce a ``ClassificationDTO`` from ``.classify()`` calls (the stub returns
  canned structured output matching the declared ``output_type``),

so the domain survives ``make quickstart`` without real credentials. This is an
integration-level test because it crosses the domain → infrastructure boundary
by design — the point is to verify that CoreContainer's stub actually
propagates through to a concrete domain service without the domain layer
having to know anything about stubbing.
"""

from __future__ import annotations

import importlib.util

import pytest

from src._core.config import settings

_has_pydantic_ai = importlib.util.find_spec("pydantic_ai") is not None


@pytest.mark.skipif(not _has_pydantic_ai, reason="pydantic-ai not installed")
class TestClassificationStubFallback:
    @pytest.fixture
    def llm_disabled(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Force the LLM selector into its ``disabled`` branch."""
        monkeypatch.setattr(settings, "llm_provider", None)
        monkeypatch.setattr(settings, "llm_model", None)

    def test_core_container_llm_model_is_test_model(self, llm_disabled: None):
        from pydantic_ai.models.test import TestModel

        from src._core.infrastructure.di.core_container import CoreContainer

        container = CoreContainer()
        assert isinstance(container.llm_model(), TestModel)

    @pytest.mark.asyncio
    async def test_classification_service_accepts_stub(self, llm_disabled: None):
        from src._core.infrastructure.di.core_container import CoreContainer
        from src.classification.domain.dtos.classification_dto import ClassificationDTO
        from src.classification.domain.services.classification_service import (
            ClassificationService,
        )

        container = CoreContainer()
        service = ClassificationService(llm_model=container.llm_model())

        result = await service.classify(
            text="This is a sample sentence.",
            categories=["positive", "negative"],
        )
        # TestModel's default output is schema-valid placeholder content, not
        # semantically meaningful — this test asserts the *contract* round-trips,
        # not the answer quality.
        assert isinstance(result, ClassificationDTO)
        assert 0.0 <= result.confidence <= 1.0
