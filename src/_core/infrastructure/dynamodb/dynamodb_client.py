from __future__ import annotations

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

import aioboto3
from botocore.exceptions import ClientError
from types_aiobotocore_dynamodb.client import DynamoDBClient as BotoDynamoDBClient

from src._core.infrastructure.dynamodb.exceptions import (
    DynamoDBConditionFailedException,
    DynamoDBException,
    DynamoDBThrottlingException,
)

_THROTTLE_CODES = frozenset(
    {"ProvisionedThroughputExceededException", "ThrottlingException"}
)


class DynamoDBClient:
    """Async DynamoDB client wrapper using aioboto3.

    Follows the same pattern as ObjectStorageClient:
    - Session held as instance attribute (Singleton in DI)
    - Client created per operation via async context manager
    """

    def __init__(
        self,
        access_key: str,
        secret_access_key: str,
        region_name: str = "ap-northeast-2",
        endpoint_url: str | None = None,
    ) -> None:
        self.session = aioboto3.Session(
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_access_key,
            region_name=region_name,
        )
        self.endpoint_url = endpoint_url

    @asynccontextmanager
    async def client(self) -> AsyncGenerator[BotoDynamoDBClient, None]:
        try:
            async with self.session.client(
                "dynamodb", endpoint_url=self.endpoint_url
            ) as dynamodb_client:
                yield dynamodb_client
        except ClientError as e:
            error_code = e.response.get("Error", {}).get("Code", "Unknown")
            error_message = e.response.get("Error", {}).get("Message", str(e))

            if error_code == "ConditionalCheckFailedException":
                raise DynamoDBConditionFailedException(error_message)
            if error_code in _THROTTLE_CODES:
                raise DynamoDBThrottlingException()

            raise DynamoDBException(
                status_code=500,
                message=f"DynamoDB operation failed [{error_code}]: {error_message}",
                error_code="DYNAMODB_ERROR",
            )
