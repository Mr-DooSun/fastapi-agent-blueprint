"""Unit tests for OpenAIEmbeddingClient using a mock AsyncOpenAI client."""

from __future__ import annotations

from typing import Any
from unittest.mock import AsyncMock, MagicMock

import pytest

openai = pytest.importorskip("openai")
pytest.importorskip("tiktoken")

from src._core.infrastructure.embedding.exceptions import (
    EmbeddingAuthenticationException,
    EmbeddingException,
    EmbeddingInputTooLongException,
    EmbeddingRateLimitException,
)
from src._core.infrastructure.embedding.openai_embedding_client import (
    OpenAIEmbeddingClient,
)

# -- Helpers ---------------------------------------------------------------


def _make_embedding_response(
    vectors: list[list[float]],
) -> Any:
    """Build a mock OpenAI embedding response."""
    data = []
    for i, vec in enumerate(vectors):
        item = MagicMock()
        item.embedding = vec
        item.index = i
        data.append(item)
    response = MagicMock()
    response.data = data
    return response


def _make_client(
    model: str = "text-embedding-3-small",
    tokens_per_text: int = 10,
) -> tuple[OpenAIEmbeddingClient, AsyncMock]:
    client = OpenAIEmbeddingClient(
        api_key="test-key",
        model=model,
    )
    mock_create = AsyncMock()
    client._client = MagicMock()  # type: ignore[assignment]
    client._client.embeddings = MagicMock()
    client._client.embeddings.create = mock_create
    # Mock tiktoken encoding for predictable token counts
    mock_encoding = MagicMock()
    mock_encoding.encode = MagicMock(
        side_effect=lambda text: (
            [0] * (len(text) if tokens_per_text == -1 else tokens_per_text)
        )
    )
    client._encoding = mock_encoding
    return client, mock_create


# -- Tests -----------------------------------------------------------------


class TestEmbedText:
    @pytest.mark.asyncio
    async def test_embed_text_returns_vector(self) -> None:
        client, mock_create = _make_client()
        mock_create.return_value = _make_embedding_response([[0.1, 0.2, 0.3, 0.4]])

        result = await client.embed_text("hello")
        assert result == [0.1, 0.2, 0.3, 0.4]

    @pytest.mark.asyncio
    async def test_embed_text_delegates_to_embed_batch(self) -> None:
        client, mock_create = _make_client()
        mock_create.return_value = _make_embedding_response([[0.1, 0.2, 0.3, 0.4]])

        await client.embed_text("hello")
        mock_create.assert_called_once()
        call_kwargs = mock_create.call_args
        assert call_kwargs.kwargs["input"] == ["hello"]


class TestEmbedBatch:
    @pytest.mark.asyncio
    async def test_embed_batch_returns_ordered_results(self) -> None:
        client, mock_create = _make_client()
        mock_create.return_value = _make_embedding_response(
            [
                [0.1, 0.2, 0.3, 0.4],
                [0.5, 0.6, 0.7, 0.8],
            ]
        )

        results = await client.embed_batch(["a", "b"])
        assert len(results) == 2
        assert results[0] == [0.1, 0.2, 0.3, 0.4]
        assert results[1] == [0.5, 0.6, 0.7, 0.8]

    @pytest.mark.asyncio
    async def test_embed_batch_empty_list(self) -> None:
        client, mock_create = _make_client()
        results = await client.embed_batch([])
        assert results == []
        mock_create.assert_not_called()

    @pytest.mark.asyncio
    async def test_embed_batch_passes_dimension(self) -> None:
        client, mock_create = _make_client()
        mock_create.return_value = _make_embedding_response([[0.1] * 1536])

        await client.embed_batch(["test"])
        call_kwargs = mock_create.call_args
        assert call_kwargs.kwargs["dimensions"] == 1536


class TestTokenBasedBatching:
    @pytest.mark.asyncio
    async def test_splits_by_item_count(self) -> None:
        """2049 texts should split into 2 batches (2048 + 1)."""
        client, mock_create = _make_client(tokens_per_text=10)
        mock_create.side_effect = [
            _make_embedding_response([[0.1] * 4] * 2048),
            _make_embedding_response([[0.1] * 4]),
        ]

        results = await client.embed_batch(["text"] * 2049)
        assert len(results) == 2049
        assert mock_create.call_count == 2

    @pytest.mark.asyncio
    async def test_splits_by_token_count(self) -> None:
        """Texts with high token count should split before reaching 300K."""
        # Each text = 1000 tokens, so 300 texts = 300K tokens → needs 2 batches
        client, mock_create = _make_client(tokens_per_text=1000)
        mock_create.side_effect = [
            _make_embedding_response([[0.1] * 4] * 300),
            _make_embedding_response([[0.1] * 4] * 10),
        ]

        results = await client.embed_batch(["text"] * 310)
        assert len(results) == 310
        assert mock_create.call_count == 2

    @pytest.mark.asyncio
    async def test_text_exceeding_max_tokens_raises_exception(self) -> None:
        """A single text with > 8192 tokens should raise immediately."""
        client, mock_create = _make_client(tokens_per_text=9000)
        with pytest.raises(EmbeddingInputTooLongException):
            await client.embed_batch(["very long text"])

    def test_count_tokens_uses_encoding(self) -> None:
        client, _ = _make_client()
        result = client._count_tokens("hello")
        client._encoding.encode.assert_called_with("hello")
        assert isinstance(result, int)


class TestDimensionProperty:
    def test_dimension_derived_from_model_small(self) -> None:
        client, _ = _make_client(model="text-embedding-3-small")
        assert client.dimension == 1536

    def test_dimension_derived_from_model_large(self) -> None:
        client, _ = _make_client(model="text-embedding-3-large")
        assert client.dimension == 3072

    def test_dimension_default(self) -> None:
        client = OpenAIEmbeddingClient(api_key="test-key")
        assert client.dimension == 1536


class TestErrorMapping:
    @pytest.mark.asyncio
    async def test_auth_error_raises_embedding_auth(self) -> None:
        client, mock_create = _make_client()
        mock_create.side_effect = openai.AuthenticationError(
            message="invalid key",
            response=MagicMock(status_code=401),
            body=None,
        )
        with pytest.raises(EmbeddingAuthenticationException):
            await client.embed_batch(["test"])

    @pytest.mark.asyncio
    async def test_rate_limit_raises_embedding_rate_limit(self) -> None:
        client, mock_create = _make_client()
        mock_create.side_effect = openai.RateLimitError(
            message="rate limited",
            response=MagicMock(status_code=429),
            body=None,
        )
        with pytest.raises(EmbeddingRateLimitException):
            await client.embed_batch(["test"])

    @pytest.mark.asyncio
    async def test_api_error_raises_embedding_exception(self) -> None:
        client, mock_create = _make_client()
        mock_create.side_effect = openai.APIError(
            message="server error",
            request=MagicMock(),
            body=None,
        )
        with pytest.raises(EmbeddingException):
            await client.embed_batch(["test"])
