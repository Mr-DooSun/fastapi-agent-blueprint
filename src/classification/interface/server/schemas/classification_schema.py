from pydantic import Field

from src._core.application.dtos.base_request import BaseRequest
from src._core.application.dtos.base_response import BaseResponse


class ClassifyRequest(BaseRequest):
    """Request schema for text classification."""

    text: str = Field(..., min_length=1, description="Text to classify")
    categories: list[str] | None = Field(
        default=None, description="Allowed categories (optional)"
    )


class ClassificationResponse(BaseResponse):
    """Response schema for classification result."""

    category: str
    confidence: float
    reasoning: str
