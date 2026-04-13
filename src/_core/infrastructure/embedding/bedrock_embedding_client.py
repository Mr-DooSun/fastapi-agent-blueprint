from __future__ import annotations

import json
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

import aioboto3
from aiobotocore.client import AioBaseClient
from botocore.exceptions import ClientError

from src._core.infrastructure.embedding.exceptions import (
    EmbeddingAuthenticationException,
    EmbeddingException,
    EmbeddingInputTooLongException,
    EmbeddingModelNotFoundException,
    EmbeddingRateLimitException,
)

_THROTTLE_CODES = frozenset({"ThrottlingException", "TooManyRequestsException"})
_MAX_CHARS_PER_TEXT = 50_000  # Bedrock Titan per-text character limit

_MODEL_DIMENSIONS: dict[str, int] = {
    "amazon.titan-embed-text-v2:0": 1024,
    "amazon.titan-embed-text-v1": 1536,
}
_DEFAULT_DIMENSION = 1024


class BedrockEmbeddingClient:
    """Async Bedrock Titan embedding client using aioboto3.

    Implements ``BaseEmbeddingProtocol``.
    Pattern identical to ``S3VectorClient``:
    - Session held as instance attribute (Singleton in DI)
    - Client created per operation via async context manager
    - ``ClientError`` wrapped into domain exceptions at client level
    - Errors only occur when ``_bedrock_client()`` is actually called,
      not at init (allows Singleton creation with ``None`` config)

    Dimension is derived automatically from ``model_id``
    via ``_MODEL_DIMENSIONS``. Not user-configurable.
    """

    def __init__(
        self,
        access_key: str,
        secret_access_key: str,
        region_name: str = "us-east-1",
        model_id: str = "amazon.titan-embed-text-v2:0",
    ) -> None:
        self.session = aioboto3.Session(
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_access_key,
            region_name=region_name,
        )
        self.model_id = model_id
        self._dimension = _MODEL_DIMENSIONS.get(model_id, _DEFAULT_DIMENSION)

    @property
    def dimension(self) -> int:
        return self._dimension

    @asynccontextmanager
    async def _bedrock_client(self) -> AsyncGenerator[AioBaseClient, None]:
        try:
            async with self.session.client("bedrock-runtime") as client:
                yield client
        except ClientError as e:
            error_code = e.response.get("Error", {}).get("Code", "Unknown")
            error_message = e.response.get("Error", {}).get("Message", str(e))

            if error_code in _THROTTLE_CODES:
                raise EmbeddingRateLimitException() from e
            if error_code == "AccessDeniedException":
                raise EmbeddingAuthenticationException() from e
            if error_code in ("ModelNotReadyException", "ValidationException"):
                raise EmbeddingModelNotFoundException(self.model_id) from e

            raise EmbeddingException(
                status_code=500,
                message="Bedrock embedding failed ["
                + error_code
                + "]: "
                + error_message,
                error_code="EMBEDDING_OPERATION_FAILED",
            ) from e

    async def embed_text(self, text: str) -> list[float]:
        if len(text) > _MAX_CHARS_PER_TEXT:
            raise EmbeddingInputTooLongException(
                len(text), _MAX_CHARS_PER_TEXT, "characters"
            )
        async with self._bedrock_client() as client:
            response = await client.invoke_model(
                modelId=self.model_id,
                contentType="application/json",
                accept="application/json",
                body=json.dumps(
                    {
                        "inputText": text,
                        "dimensions": self._dimension,
                    }
                ),
            )
            body = json.loads(await response["body"].read())
            return body["embedding"]

    async def embed_batch(self, texts: list[str]) -> list[list[float]]:
        results: list[list[float]] = []
        for text in texts:
            embedding = await self.embed_text(text)
            results.append(embedding)
        return results
