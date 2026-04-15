import importlib.util
from unittest.mock import MagicMock, patch

import pytest

from src._core.domain.value_objects.llm_config import LLMConfig

_has_pydantic_ai = importlib.util.find_spec("pydantic_ai") is not None


class TestClassificationServiceImportError:
    """pydantic-ai 미설치 시 ImportError 발생 확인."""

    def test_raises_import_error_without_pydantic_ai(self):
        if _has_pydantic_ai:
            pytest.skip("pydantic-ai is installed; cannot test ImportError path")

        with pytest.raises(ImportError, match="pydantic-ai is required"):
            from src.classification.domain.services.classification_service import (
                ClassificationService,
            )

            ClassificationService(llm_config=LLMConfig(model_name="openai:gpt-4o"))


@pytest.mark.skipif(not _has_pydantic_ai, reason="pydantic-ai not installed")
class TestClassificationServiceWithPydanticAI:
    """pydantic-ai 설치 시 서비스 동작 테스트."""

    def test_agent_created_on_init(self):
        from src.classification.domain.services.classification_service import (
            ClassificationService,
        )

        config = LLMConfig(model_name="test:model-name", api_key="test-key")
        service = ClassificationService(llm_config=config)
        assert service._model_name == "test:model-name"

    @pytest.mark.asyncio
    async def test_classify_returns_dto(self):
        from src.classification.domain.dtos.classification_dto import (
            ClassificationDTO,
        )
        from src.classification.domain.services.classification_service import (
            ClassificationService,
        )

        config = LLMConfig(model_name="test:model-name")
        service = ClassificationService(llm_config=config)

        mock_result = MagicMock()
        mock_result.output = ClassificationDTO(
            category="positive",
            confidence=0.95,
            reasoning="The text expresses positive sentiment.",
        )

        with patch.object(service._agent, "run", return_value=mock_result) as mock_run:
            result = await service.classify(
                text="This is great!", categories=["positive", "negative"]
            )

            assert result.category == "positive"
            assert result.confidence == 0.95
            mock_run.assert_called_once()
            call_args = mock_run.call_args
            assert "Categories: positive, negative" in call_args[0][0]
            assert "This is great!" in call_args[0][0]

    @pytest.mark.asyncio
    async def test_classify_without_categories(self):
        from src.classification.domain.dtos.classification_dto import (
            ClassificationDTO,
        )
        from src.classification.domain.services.classification_service import (
            ClassificationService,
        )

        config = LLMConfig(model_name="test:model-name")
        service = ClassificationService(llm_config=config)

        mock_result = MagicMock()
        mock_result.output = ClassificationDTO(
            category="tech",
            confidence=0.8,
            reasoning="Technical topic.",
        )

        with patch.object(service._agent, "run", return_value=mock_result) as mock_run:
            result = await service.classify(text="Python is a programming language")

            assert result.category == "tech"
            mock_run.assert_called_once_with("Python is a programming language")

    @pytest.mark.asyncio
    async def test_classify_wraps_exception(self):
        from src.classification.domain.exceptions.classification_exceptions import (
            ClassificationFailedException,
        )
        from src.classification.domain.services.classification_service import (
            ClassificationService,
        )

        config = LLMConfig(model_name="test:model-name")
        service = ClassificationService(llm_config=config)

        with patch.object(
            service._agent, "run", side_effect=RuntimeError("API timeout")
        ):
            with pytest.raises(ClassificationFailedException, match="API timeout"):
                await service.classify(text="test input")


class TestLLMConfig:
    def test_frozen_dataclass(self):
        config = LLMConfig(model_name="openai:gpt-4o", api_key="sk-test")
        assert config.model_name == "openai:gpt-4o"
        assert config.api_key == "sk-test"

        with pytest.raises(AttributeError):
            config.model_name = "changed"  # type: ignore[misc]

    def test_api_key_defaults_to_none(self):
        config = LLMConfig(model_name="anthropic:claude-sonnet-4-20250514")
        assert config.api_key is None
