from dataclasses import dataclass


@dataclass(frozen=True)
class LLMConfig:
    """Immutable LLM configuration for domain services.

    Domain services use this to construct PydanticAI Agents.
    Follows the VectorQuery/DynamoKey pattern (domain-layer value object).

    ``model_name`` is a PydanticAI-compatible string, e.g. ``"openai:gpt-4o"``.
    """

    model_name: str
    api_key: str | None = None
