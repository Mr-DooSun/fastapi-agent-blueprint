"""Unit tests for BedrockEmbeddingClient using a fake Bedrock runtime client.

This test file also serves as the usage reference for the Bedrock
embedding integration (no real AWS credentials needed).
"""

from __future__ import annotations

import json
from contextlib import asynccontextmanager
from typing import Any

import pytest
from botocore.exceptions import ClientError

from src._core.infrastructure.embedding.bedrock_embedding_client import (
    BedrockEmbeddingClient,
)
from src._core.infrastructure.embedding.exceptions import (
    EmbeddingAuthenticationException,
    EmbeddingInputTooLongException,
    EmbeddingModelNotFoundException,
    EmbeddingRateLimitException,
)

# -- Fake Bedrock Runtime Client -------------------------------------------


class FakeBodyStream:
    """Simulates the async-readable body stream from Bedrock response."""

    def __init__(self, data: dict[str, Any]) -> None:
        self._data = json.dumps(data).encode()

    async def read(self) -> bytes:
        return self._data


class FakeBedrockRuntimeClient:
    """In-memory Bedrock runtime mock that returns deterministic embeddings."""

    def __init__(self, dimension: int = 4, error: ClientError | None = None) -> None:
        self._dimension = dimension
        self._error = error
        self.calls: list[dict[str, Any]] = []

    async def invoke_model(self, **kwargs: Any) -> dict[str, Any]:
        if self._error:
            raise self._error
        body = json.loads(kwargs["body"])
        self.calls.append(body)
        text = body.get("inputText", "")
        dim = body.get("dimensions", self._dimension)
        embedding = [float(i + len(text)) * 0.01 for i in range(dim)]
        return {"body": FakeBodyStream({"embedding": embedding})}


class FakeBedrockSession:
    """Wraps the fake client in the aioboto3 context-manager pattern."""

    def __init__(self, fake_client: FakeBedrockRuntimeClient) -> None:
        self._client = fake_client

    @asynccontextmanager
    async def client(self, service_name: str):  # noqa: ANN201
        yield self._client


def _make_client(
    model_id: str = "amazon.titan-embed-text-v2:0",
    error: ClientError | None = None,
) -> tuple[BedrockEmbeddingClient, FakeBedrockRuntimeClient]:
    fake = FakeBedrockRuntimeClient(error=error)
    client = BedrockEmbeddingClient(
        access_key="test",
        secret_access_key="test",
        region_name="us-east-1",
        model_id=model_id,
    )
    client.session = FakeBedrockSession(fake)  # type: ignore[assignment]
    return client, fake


def _make_client_error(code: str, message: str = "error") -> ClientError:
    return ClientError(
        {"Error": {"Code": code, "Message": message}},
        "InvokeModel",
    )


# -- Tests -----------------------------------------------------------------


class TestEmbedText:
    @pytest.mark.asyncio
    async def test_embed_text_returns_vector(self) -> None:
        client, _ = _make_client()
        result = await client.embed_text("hello")
        assert isinstance(result, list)
        assert len(result) == client.dimension
        assert all(isinstance(v, float) for v in result)

    @pytest.mark.asyncio
    async def test_embed_text_passes_dimension_in_body(self) -> None:
        client, fake = _make_client()
        await client.embed_text("test")
        assert fake.calls[0]["dimensions"] == client.dimension

    @pytest.mark.asyncio
    async def test_dimension_derived_from_model_titan_v2(self) -> None:
        client, _ = _make_client(model_id="amazon.titan-embed-text-v2:0")
        assert client.dimension == 1024

    @pytest.mark.asyncio
    async def test_dimension_derived_from_model_titan_v1(self) -> None:
        client, _ = _make_client(model_id="amazon.titan-embed-text-v1")
        assert client.dimension == 1536


class TestEmbedBatch:
    @pytest.mark.asyncio
    async def test_embed_batch_returns_ordered_results(self) -> None:
        client, _ = _make_client()
        results = await client.embed_batch(["a", "bb", "ccc"])
        assert len(results) == 3
        assert all(len(v) == client.dimension for v in results)
        # Each text has different length, so embeddings should differ
        assert results[0] != results[1]

    @pytest.mark.asyncio
    async def test_embed_batch_empty_list(self) -> None:
        client, _ = _make_client()
        results = await client.embed_batch([])
        assert results == []


class TestErrorMapping:
    @pytest.mark.asyncio
    async def test_throttling_raises_rate_limit(self) -> None:
        client, _ = _make_client(error=_make_client_error("ThrottlingException"))
        with pytest.raises(EmbeddingRateLimitException):
            await client.embed_text("test")

    @pytest.mark.asyncio
    async def test_too_many_requests_raises_rate_limit(self) -> None:
        client, _ = _make_client(error=_make_client_error("TooManyRequestsException"))
        with pytest.raises(EmbeddingRateLimitException):
            await client.embed_text("test")

    @pytest.mark.asyncio
    async def test_access_denied_raises_auth(self) -> None:
        client, _ = _make_client(error=_make_client_error("AccessDeniedException"))
        with pytest.raises(EmbeddingAuthenticationException):
            await client.embed_text("test")

    @pytest.mark.asyncio
    async def test_validation_raises_model_not_found(self) -> None:
        client, _ = _make_client(error=_make_client_error("ValidationException"))
        with pytest.raises(EmbeddingModelNotFoundException):
            await client.embed_text("test")


class TestInputValidation:
    @pytest.mark.asyncio
    async def test_text_exceeding_max_chars_raises_exception(self) -> None:
        client, _ = _make_client()
        long_text = "a" * 50_001
        with pytest.raises(EmbeddingInputTooLongException):
            await client.embed_text(long_text)

    @pytest.mark.asyncio
    async def test_text_at_exactly_max_chars_succeeds(self) -> None:
        client, _ = _make_client()
        text = "a" * 50_000
        result = await client.embed_text(text)
        assert isinstance(result, list)

    @pytest.mark.asyncio
    async def test_embed_batch_validates_each_text(self) -> None:
        client, _ = _make_client()
        texts = ["short", "a" * 50_001]
        with pytest.raises(EmbeddingInputTooLongException):
            await client.embed_batch(texts)
