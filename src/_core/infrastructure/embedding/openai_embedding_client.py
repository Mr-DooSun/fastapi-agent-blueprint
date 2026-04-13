from __future__ import annotations

from src._core.infrastructure.embedding.exceptions import (
    EmbeddingAuthenticationException,
    EmbeddingException,
    EmbeddingInputTooLongException,
    EmbeddingRateLimitException,
)

_BATCH_SIZE = 2048  # OpenAI max texts per request
_MAX_TOKENS_PER_BATCH = 300_000  # OpenAI total token limit per request
_MAX_TOKENS_PER_TEXT = 8192  # OpenAI per-text token limit

_MODEL_DIMENSIONS: dict[str, int] = {
    "text-embedding-3-small": 1536,
    "text-embedding-3-large": 3072,
    "text-embedding-ada-002": 1536,
}
_DEFAULT_DIMENSION = 1536


class OpenAIEmbeddingClient:
    """Async OpenAI embedding client.

    Implements ``BaseEmbeddingProtocol``.
    Uses ``AsyncOpenAI`` from the ``openai`` package (optional dependency).

    Pattern follows the broker lazy-import convention:
    ``openai`` and ``tiktoken`` are imported at init time; if missing,
    a clear ``ImportError`` with install instructions is raised.

    Dimension is derived automatically from ``model``
    via ``_MODEL_DIMENSIONS``. Not user-configurable.

    Batching respects both item count (2,048) and total token count
    (300,000) per request — the binding constraint for OpenAI.
    """

    def __init__(
        self,
        api_key: str,
        model: str = "text-embedding-3-small",
    ) -> None:
        try:
            from openai import AsyncOpenAI
        except ImportError:
            raise ImportError(
                "openai is required for OpenAI embeddings. "
                "Install it with: uv sync --extra openai"
            )
        try:
            import tiktoken
        except ImportError:
            raise ImportError(
                "tiktoken is required for OpenAI embeddings. "
                "Install it with: uv sync --extra openai"
            )
        self._client = AsyncOpenAI(api_key=api_key)
        self.model = model
        self._dimension = _MODEL_DIMENSIONS.get(model, _DEFAULT_DIMENSION)
        self._encoding = tiktoken.encoding_for_model(model)

    @property
    def dimension(self) -> int:
        return self._dimension

    def _count_tokens(self, text: str) -> int:
        """Count tokens in text using tiktoken."""
        return len(self._encoding.encode(text))

    def _split_into_batches(self, texts: list[str]) -> list[list[str]]:
        """Split texts into batches respecting both item count and token limits.

        Each batch satisfies:
        - At most ``_BATCH_SIZE`` texts (2,048)
        - Total tokens across all texts at most ``_MAX_TOKENS_PER_BATCH`` (300,000)

        Raises ``EmbeddingInputTooLongException`` if any individual text
        exceeds ``_MAX_TOKENS_PER_TEXT`` (8,192 tokens).
        """
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

    async def embed_text(self, text: str) -> list[float]:
        return (await self.embed_batch([text]))[0]

    async def embed_batch(self, texts: list[str]) -> list[list[float]]:
        try:
            from openai import APIError, AuthenticationError, RateLimitError
        except ImportError:
            raise ImportError(
                "openai is required for OpenAI embeddings. "
                "Install it with: uv sync --extra openai"
            )

        if not texts:
            return []

        batches = self._split_into_batches(texts)
        results: list[list[float]] = []
        try:
            for batch in batches:
                response = await self._client.embeddings.create(
                    model=self.model,
                    input=batch,
                    dimensions=self._dimension,
                )
                results.extend(item.embedding for item in response.data)
        except AuthenticationError as e:
            raise EmbeddingAuthenticationException() from e
        except RateLimitError as e:
            raise EmbeddingRateLimitException() from e
        except APIError as e:
            raise EmbeddingException(
                status_code=502,
                message="OpenAI embedding failed: " + e.message,
                error_code="EMBEDDING_OPERATION_FAILED",
            ) from e

        return results
