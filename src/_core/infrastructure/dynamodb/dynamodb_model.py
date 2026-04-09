from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Any, ClassVar, Literal, Self

from boto3.dynamodb.types import TypeDeserializer, TypeSerializer
from pydantic import BaseModel


class GSIDefinition(BaseModel):
    """Declarative GSI schema definition."""

    index_name: str
    partition_key_name: str
    sort_key_name: str | None = None
    projection_type: Literal["ALL", "KEYS_ONLY", "INCLUDE"] = "ALL"
    non_key_attributes: list[str] | None = None


class DynamoModelMeta(BaseModel):
    """Declarative DynamoDB table schema metadata."""

    tablename: str
    partition_key_name: str
    sort_key_name: str | None = None
    gsi: list[GSIDefinition] = []
    ttl_attribute: str | None = None


class DynamoModel(BaseModel):
    """Base class for DynamoDB models.

    Subclasses define table schema via ``__dynamo_meta__`` and
    override ``get_partition_key`` / ``get_sort_key`` for composite keys.

    Serialization uses boto3 TypeSerializer/TypeDeserializer
    (Client API only — sync Resource API is not supported).
    """

    __dynamo_meta__: ClassVar[DynamoModelMeta]
    _serializer: ClassVar[TypeSerializer] = TypeSerializer()
    _type_deserializer: ClassVar[TypeDeserializer] = TypeDeserializer()

    # ------------------------------------------------------------------
    # Key generation (override in subclasses)
    # ------------------------------------------------------------------

    def get_partition_key(self) -> str:
        """Return the partition key value for this item."""
        raise NotImplementedError(
            f"{type(self).__name__} must override get_partition_key()"
        )

    def get_sort_key(self) -> str | None:
        """Return the sort key value, or None if table has no sort key."""
        return None

    def get_gsi_keys(self) -> dict[str, str]:
        """Return GSI key values derived from model fields.

        Override individual ``get_gsi_{index_name}_pk`` /
        ``get_gsi_{index_name}_sk`` methods for each GSI.
        """
        keys: dict[str, str] = {}
        for gsi in self.__dynamo_meta__.gsi:
            pk_getter = getattr(self, f"get_gsi_{gsi.index_name}_pk", None)
            if pk_getter:
                keys[gsi.partition_key_name] = pk_getter()
            sk_getter = getattr(self, f"get_gsi_{gsi.index_name}_sk", None)
            if sk_getter and gsi.sort_key_name:
                keys[gsi.sort_key_name] = sk_getter()
        return keys

    # ------------------------------------------------------------------
    # Serialization (model → DynamoDB item)
    # ------------------------------------------------------------------

    def to_dynamodb(self) -> dict[str, Any]:
        """Serialize to DynamoDB Client API format using TypeSerializer."""
        data = self.model_dump()
        meta = self.__dynamo_meta__

        # Build the raw item with Python-native types converted
        raw: dict[str, Any] = {}
        for key, value in data.items():
            converted = self._convert_value(value)
            if converted is not None:
                raw[key] = converted

        # Inject PK / SK
        raw[meta.partition_key_name] = self.get_partition_key()
        sk = self.get_sort_key()
        if meta.sort_key_name and sk is not None:
            raw[meta.sort_key_name] = sk

        # Inject GSI keys
        raw.update(self.get_gsi_keys())

        # Serialize every value with TypeSerializer
        return {k: self._serializer.serialize(v) for k, v in raw.items()}

    # ------------------------------------------------------------------
    # Deserialization (DynamoDB item → model)
    # ------------------------------------------------------------------

    @classmethod
    def from_dynamodb(cls, item: dict[str, Any]) -> Self:
        """Deserialize from DynamoDB Client API format using TypeDeserializer."""
        deserialized = {
            k: cls._type_deserializer.deserialize(v) for k, v in item.items()
        }

        # Convert Decimal back to int/float for Pydantic compatibility
        cleaned = {k: cls._clean_value(v) for k, v in deserialized.items()}
        return cls.model_validate(cleaned)

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _convert_value(value: Any) -> Any:
        """Convert Python types to DynamoDB-compatible types."""
        if value is None:
            return None
        if isinstance(value, float):
            return Decimal(str(value))
        if isinstance(value, datetime):
            return value.isoformat()
        if isinstance(value, set):
            return list(value)
        if isinstance(value, list):
            return [DynamoModel._convert_value(v) for v in value]
        if isinstance(value, dict):
            return {k: DynamoModel._convert_value(v) for k, v in value.items()}
        return value

    @staticmethod
    def _clean_value(value: Any) -> Any:
        """Convert DynamoDB types back to Python-native types."""
        if isinstance(value, Decimal):
            return int(value) if value == int(value) else float(value)
        if isinstance(value, dict):
            return {k: DynamoModel._clean_value(v) for k, v in value.items()}
        if isinstance(value, list):
            return [DynamoModel._clean_value(v) for v in value]
        return value
