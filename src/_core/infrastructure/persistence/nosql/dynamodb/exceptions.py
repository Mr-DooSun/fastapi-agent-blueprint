from src._core.exceptions.base_exception import BaseCustomException


class DynamoDBException(BaseCustomException):
    """Base exception for DynamoDB operations."""

    pass


class DynamoDBNotFoundException(DynamoDBException):
    def __init__(self) -> None:
        super().__init__(
            status_code=404,
            message="Requested item not found",
            error_code="DYNAMODB_NOT_FOUND",
        )


class DynamoDBConditionFailedException(DynamoDBException):
    def __init__(self, message: str = "Condition check failed") -> None:
        super().__init__(
            status_code=409,
            message=message,
            error_code="DYNAMODB_CONDITION_FAILED",
        )


class DynamoDBThrottlingException(DynamoDBException):
    def __init__(self) -> None:
        super().__init__(
            status_code=429,
            message="DynamoDB throughput exceeded",
            error_code="DYNAMODB_THROTTLED",
        )


class DynamoDBBatchIncompleteException(DynamoDBException):
    """A batch finished with items DynamoDB never accepted (#329 F6).

    Distinct from :class:`DynamoDBThrottlingException` on purpose. Throttling is
    the usual cause of ``UnprocessedItems`` but not the only one, and naming the
    cause would be a guess; what the caller can act on is *how many* items did
    not land. 429 is kept because "retry with backoff" is still the right signal.

    Raised rather than returning a partial result. For writes that is the only
    safe answer — the previous behaviour built a success DTO for every item in
    the chunk, so a caller committed to writes that were not in the table. For
    reads it discards successful work in the same call, which is the accepted
    trade: reads are idempotent and cheap to redo, while a silently short list is
    indistinguishable from "those keys do not exist" and cannot be detected at
    all.
    """

    def __init__(self, operation: str, unprocessed_count: int, table_name: str = ""):
        target = f" on table '{table_name}'" if table_name else ""
        super().__init__(
            status_code=429,
            message=(
                f"DynamoDB {operation} left {unprocessed_count} item(s) "
                f"unprocessed{target} after exhausting retries"
            ),
            error_code="DYNAMODB_BATCH_INCOMPLETE",
        )


class DynamoDBInvalidCursorException(DynamoDBException):
    """A pagination cursor that did not survive decoding (#329).

    The token is client-supplied, so a raw ``binascii.Error`` /
    ``JSONDecodeError`` / ``UnicodeDecodeError`` escaping as a 500 is both the
    wrong status and — since #17 — an operator page for a malformed request.
    """

    def __init__(self) -> None:
        super().__init__(
            status_code=400,
            message="Malformed pagination cursor",
            error_code="DYNAMODB_INVALID_CURSOR",
        )
