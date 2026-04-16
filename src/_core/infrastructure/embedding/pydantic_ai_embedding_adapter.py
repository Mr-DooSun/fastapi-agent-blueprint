from __future__ import annotations

from typing import NoReturn

from src._core.domain.value_objects.embedding_config import EmbeddingConfig
from src._core.infrastructure.embedding.exceptions import (
    EmbeddingAuthenticationException,
    EmbeddingException,
    EmbeddingInputTooLongException,
    EmbeddingModelNotFoundException,
    EmbeddingRateLimitException,
)

_BATCH_SIZE = 2048  # OpenAI max texts per request
_MAX_TOKENS_PER_BATCH = 300_000  # OpenAI total token limit per request
_MAX_TOKENS_PER_TEXT = 8192  # OpenAI per-text token limit


class PydanticAIEmbeddingAdapter:
    """Adapter bridging PydanticAI Embedder to ``BaseEmbeddingProtocol``.

    Implements the same interface as ``OpenAIEmbeddingClient`` /
    ``BedrockEmbeddingClient`` so it can be a drop-in replacement
    behind ``BaseEmbeddingProtocol``.

    Provider-specific behaviour:
    - **OpenAI**: batch splitting respects 2,048 items / 300K tokens.
    - **Bedrock**: PydanticAI handles concurrent individual requests
      via semaphore (default 5), no splitting needed.
    - **Google / Ollama / SentenceTransformers**: native batch or local,
      no splitting needed.

    Credentials:
    - OpenAI: ``api_key`` passed to ``OpenAIProvider`` explicitly.
    - Bedrock: ``aws_*`` fields passed to ``BedrockProvider`` explicitly
      (project convention: per-service credential injection).
    - Others: PydanticAI auto-detects environment variables.
    """

    def __init__(self, embedding_config: EmbeddingConfig) -> None:
        try:
            from pydantic_ai import Embedder
        except ImportError:
            raise ImportError(
                "pydantic-ai is required for embedding. "
                "Install it with: uv sync --extra pydantic-ai"
            )

        self._dimension = embedding_config.dimension
        self._provider = (
            embedding_config.model_name.split(":")[0]
            if ":" in embedding_config.model_name
            else ""
        )
        self._model_name = embedding_config.model_name
        self._embedder = Embedder(self._build_model(embedding_config))

        if self._provider == "openai":
            self._init_tiktoken(embedding_config.model_name)

    def _build_model(self, config: EmbeddingConfig):  # noqa: ANN206
        """Build a PydanticAI model object or return a model string.

        When explicit credentials are provided, constructs a Provider
        object for precise authentication control. Otherwise returns the
        plain model string and lets PydanticAI auto-detect env vars.
        """
        provider = self._provider
        raw_model = (
            config.model_name.split(":", 1)[1]
            if ":" in config.model_name
            else config.model_name
        )

        if provider == "openai" and config.api_key:
            from pydantic_ai.embeddings.openai import OpenAIEmbeddingModel
            from pydantic_ai.providers.openai import OpenAIProvider

            return OpenAIEmbeddingModel(
                raw_model,
                provider=OpenAIProvider(api_key=config.api_key),
            )

        if provider == "bedrock" and config.aws_access_key_id:
            from pydantic_ai.embeddings.bedrock import BedrockEmbeddingModel
            from pydantic_ai.providers.bedrock import BedrockProvider

            return BedrockEmbeddingModel(
                raw_model,
                provider=BedrockProvider(
                    region_name=config.aws_region or "us-east-1",
                    aws_access_key_id=config.aws_access_key_id,
                    aws_secret_access_key=config.aws_secret_access_key,
                ),
            )

        return config.model_name

    def _init_tiktoken(self, model_name: str) -> None:
        """Initialise tiktoken encoder for OpenAI batch splitting."""
        try:
            import tiktoken
        except ImportError:
            raise ImportError(
                "tiktoken is required for OpenAI embedding batch splitting. "
                "Install it with: uv sync --extra pydantic-ai"
            )
        raw_model = model_name.split(":", 1)[1] if ":" in model_name else model_name
        self._encoding = tiktoken.encoding_for_model(raw_model)

    @property
    def dimension(self) -> int:
        return self._dimension

    async def embed_text(self, text: str) -> list[float]:
        result = await self._call_embed_query(text)
        return list(result.embeddings[0])

    async def embed_batch(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []

        if self._provider == "openai":
            return await self._split_and_embed(texts)

        result = await self._call_embed_documents(texts)
        return [list(e) for e in result.embeddings]

    # ------------------------------------------------------------------
    # OpenAI batch splitting (migrated from OpenAIEmbeddingClient)
    # ------------------------------------------------------------------

    def _count_tokens(self, text: str) -> int:
        return len(self._encoding.encode(text))

    def _split_into_batches(self, texts: list[str]) -> list[list[str]]:
        """Split texts respecting both item count and token limits."""
        batches: list[list[str]] = []
        current_batch: list[str] = []
        current_tokens = 0

        for text in texts:
            text_tokens = self._count_tokens(text)
            if text_tokens > _MAX_TOKENS_PER_TEXT:
                raise EmbeddingInputTooLongException(
                    text_tokens, _MAX_TOKENS_PER_TEXT, "tokens"
                )

            would_exceed_tokens = current_tokens + text_tokens > _MAX_TOKENS_PER_BATCH
            would_exceed_count = len(current_batch) >= _BATCH_SIZE

            if current_batch and (would_exceed_tokens or would_exceed_count):
                batches.append(current_batch)
                current_batch = []
                current_tokens = 0

            current_batch.append(text)
            current_tokens += text_tokens

        if current_batch:
            batches.append(current_batch)

        return batches

    async def _split_and_embed(self, texts: list[str]) -> list[list[float]]:
        """Embed with OpenAI-specific batch splitting."""
        batches = self._split_into_batches(texts)
        results: list[list[float]] = []
        for batch in batches:
            result = await self._call_embed_documents(batch)
            results.extend(list(e) for e in result.embeddings)
        return results

    # ------------------------------------------------------------------
    # PydanticAI calls with error mapping
    # ------------------------------------------------------------------

    async def _call_embed_query(self, text: str):  # noqa: ANN206
        try:
            return await self._embedder.embed_query(text)
        except Exception as exc:
            self._map_error(exc)

    async def _call_embed_documents(self, texts: list[str]):  # noqa: ANN206
        try:
            return await self._embedder.embed_documents(texts)
        except Exception as exc:
            self._map_error(exc)

    def _map_error(self, exc: Exception) -> NoReturn:
        """Map PydanticAI exceptions to domain exceptions."""
        error_str = str(exc).lower()
        if "authentication" in error_str or "unauthorized" in error_str:
            raise EmbeddingAuthenticationException() from exc
        if "rate" in error_str and "limit" in error_str:
            raise EmbeddingRateLimitException() from exc
        if "not found" in error_str:
            raise EmbeddingModelNotFoundException(self._model_name) from exc
        raise EmbeddingException(
            status_code=502,
            message=f"Embedding failed: {exc}",
            error_code="EMBEDDING_OPERATION_FAILED",
        ) from exc
