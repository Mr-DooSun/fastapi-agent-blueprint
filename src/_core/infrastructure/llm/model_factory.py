from __future__ import annotations

from src._core.domain.value_objects.llm_config import LLMConfig


def build_llm_model(llm_config: LLMConfig):  # noqa: ANN201
    """Build a PydanticAI Model object or return a model string.

    Same pattern as ``PydanticAIEmbeddingAdapter._build_model()``:
    - Explicit credentials → construct Provider for precise auth control.
    - No credentials → return plain model string (env var fallback).

    Domain services call this to get a model suitable for ``Agent(model=...)``.
    """
    provider = (
        llm_config.model_name.split(":")[0] if ":" in llm_config.model_name else ""
    )
    raw_model = (
        llm_config.model_name.split(":", 1)[1]
        if ":" in llm_config.model_name
        else llm_config.model_name
    )

    if provider == "bedrock" and llm_config.aws_access_key_id:
        from pydantic_ai.models.bedrock import BedrockConverseModel
        from pydantic_ai.providers.bedrock import BedrockProvider

        return BedrockConverseModel(
            raw_model,
            provider=BedrockProvider(
                region_name=llm_config.aws_region or "us-east-1",
                aws_access_key_id=llm_config.aws_access_key_id,
                aws_secret_access_key=llm_config.aws_secret_access_key,
            ),
        )

    if provider == "openai" and llm_config.api_key:
        from pydantic_ai.models.openai import OpenAIChatModel
        from pydantic_ai.providers.openai import OpenAIProvider

        return OpenAIChatModel(
            raw_model,
            provider=OpenAIProvider(api_key=llm_config.api_key),
        )

    if provider == "anthropic" and llm_config.api_key:
        from pydantic_ai.models.anthropic import AnthropicModel
        from pydantic_ai.providers.anthropic import AnthropicProvider

        return AnthropicModel(
            raw_model,
            provider=AnthropicProvider(api_key=llm_config.api_key),
        )

    return llm_config.model_name
