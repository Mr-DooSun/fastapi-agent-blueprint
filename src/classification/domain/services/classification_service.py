from __future__ import annotations

from typing import Any

from src._core.common.llm_utils import map_llm_error
from src._core.exceptions.base_exception import BaseCustomException
from src.classification.domain.dtos.classification_dto import ClassificationDTO


class ClassificationService:
    """Text classification service powered by PydanticAI.

    The Agent instance is created once in ``__init__`` (PydanticAI agents are
    designed to be reused across requests) and shared across all calls.

    ``llm_model`` is a PydanticAI Model object or model string, built by
    ``build_llm_model()`` in the infrastructure layer and injected via DI.
    """

    def __init__(self, llm_model: Any) -> None:
        try:
            from pydantic_ai import Agent
        except ImportError:
            raise ImportError(
                "pydantic-ai is required for classification. "
                "Install it with: uv sync --extra pydantic-ai"
            )

        self._agent: Agent[None, ClassificationDTO] = Agent(
            model=llm_model,
            output_type=ClassificationDTO,
            system_prompt=(
                "You are a precise text classifier. "
                "Classify the given text into one of the provided categories. "
                "Return your confidence score (0 to 1) and a brief reasoning."
            ),
        )

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
        except BaseCustomException:
            raise
        except Exception as exc:
            map_llm_error(exc)
