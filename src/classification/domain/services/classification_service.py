from __future__ import annotations

import logging

from src._core.domain.value_objects.llm_config import LLMConfig
from src.classification.domain.dtos.classification_dto import ClassificationDTO
from src.classification.domain.exceptions.classification_exceptions import (
    ClassificationFailedException,
)

logger = logging.getLogger(__name__)


class ClassificationService:
    """Text classification service powered by PydanticAI.

    The Agent instance is created once in ``__init__`` (PydanticAI agents are
    designed to be reused across requests) and shared across all calls.
    """

    def __init__(self, llm_config: LLMConfig) -> None:
        try:
            from pydantic_ai import Agent
        except ImportError:
            raise ImportError(
                "pydantic-ai is required for classification. "
                "Install it with: uv sync --extra pydantic-ai"
            )

        self._agent: Agent[None, ClassificationDTO] = Agent(
            model=llm_config.model_name,
            output_type=ClassificationDTO,
            system_prompt=(
                "You are a precise text classifier. "
                "Classify the given text into one of the provided categories. "
                "Return your confidence score (0 to 1) and a brief reasoning."
            ),
        )
        self._model_name = llm_config.model_name

    async def classify(
        self,
        text: str,
        categories: list[str] | None = None,
    ) -> ClassificationDTO:
        """Classify text into a category.

        Args:
            text: The text to classify.
            categories: Optional list of allowed categories.
                        When provided, the agent is instructed to choose from them.

        Returns:
            ClassificationDTO with category, confidence, and reasoning.
        """
        prompt = text
        if categories:
            cats = ", ".join(categories)
            prompt = f"Categories: {cats}\n\nText: {text}"

        try:
            result = await self._agent.run(prompt)
            return result.output
        except Exception as exc:
            logger.exception("Classification failed for text: %s...", text[:80])
            raise ClassificationFailedException(str(exc)) from exc
