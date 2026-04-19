from __future__ import annotations

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

import aioboto3
from aiobotocore.client import AioBaseClient
from botocore.exceptions import ClientError

from src._core.infrastructure.vectors.exceptions import (
    S3VectorException,
    S3VectorIndexNotFoundException,
    S3VectorThrottlingException,
)


class S3VectorClient:
    """Async S3 Vectors client wrapper using aioboto3.

    Pattern identical to ``DynamoDBClient``:
    - Session held as instance attribute (Singleton in DI)
    - Client created per operation via async context manager
    - ``ClientError`` wrapped into domain exceptions at client level
    - Errors only occur when ``client()`` is actually called, not at init
      (allows Singleton creation with ``None`` config when S3 Vectors not used)
    """

    def __init__(
        self,
        access_key: str,
        secret_access_key: str,
        region_name: str = "us-east-2",
    ) -> None:
        self.session = aioboto3.Session(
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_access_key,
            region_name=region_name,
        )

    @asynccontextmanager
    async def client(self) -> AsyncGenerator[AioBaseClient, None]:
        try:
            async with self.session.client("s3vectors") as s3v_client:
                yield s3v_client
        except ClientError as e:
            error_code = e.response.get("Error", {}).get("Code", "Unknown")
            error_message = e.response.get("Error", {}).get("Message", str(e))

            if error_code == "NotFoundException":
                raise S3VectorIndexNotFoundException() from e
            if error_code == "TooManyRequestsException":
                raise S3VectorThrottlingException() from e

            raise S3VectorException(
                status_code=500,
                message="S3 Vectors operation failed ["
                + error_code
                + "]: "
                + error_message,
                error_code="S3VECTOR_OPERATION_FAILED",
            ) from e
