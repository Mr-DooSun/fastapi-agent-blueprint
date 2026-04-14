from __future__ import annotations

from typing import Any, ClassVar, Literal, Self

from pydantic import BaseModel, Field

from src._core.common.uuid_utils import generate_vector_id


class S3VectorModelMeta(BaseModel):
    """S3 Vectors index schema metadata.

    ``DynamoModelMeta`` counterpart — declares index configuration
    that the migration CLI reads to create/compare indexes.
    """

    index_name: str
    data_type: Literal["float32"] = "float32"
    dimension: int = 1536
    distance_metric: Literal["cosine", "euclidean"] = "cosine"
    filter_fields: list[str] = []
    non_filter_fields: list[str] = []


class S3VectorData(BaseModel):
    """S3 Vectors embedding data format."""

    float32: list[float]


class S3VectorModel(BaseModel):
    """Base class for S3 Vectors index models.

    ``DynamoModel`` counterpart — subclasses define index schema via
    ``__s3vector_meta__`` and declare metadata as Pydantic fields.

    Example::

        class DocumentS3VectorModel(S3VectorModel):
            __s3vector_meta__: ClassVar[S3VectorModelMeta] = S3VectorModelMeta(
                index_name="document-search",
                dimension=1536,
                distance_metric="cosine",
                filter_fields=["category", "author_id"],
                non_filter_fields=["content_preview"],
            )

            category: str
            author_id: str
            content_preview: str
    """

    __s3vector_meta__: ClassVar[S3VectorModelMeta]

    key: str = Field(default_factory=generate_vector_id)
    data: S3VectorData

    # ------------------------------------------------------------------
    # Serialization (model -> S3 Vectors API format)
    # ------------------------------------------------------------------

    def to_s3vector(self) -> dict[str, Any]:
        """Serialize to S3 Vectors ``put_vectors`` API format.

        ``DynamoModel.to_dynamodb()`` counterpart.
        All fields except ``key`` and ``data`` are extracted as metadata.
        """
        metadata = self.model_dump(exclude={"key", "data"}, exclude_none=True)
        return {
            "key": self.key,
            "data": self.data.model_dump(),
            "metadata": metadata,
        }

    # ------------------------------------------------------------------
    # Deserialization (S3 Vectors API response -> model)
    # ------------------------------------------------------------------

    @classmethod
    def from_s3vector(cls, raw: dict[str, Any]) -> Self:
        """Deserialize from S3 Vectors ``get_vectors``/``query_vectors`` response.

        ``DynamoModel.from_dynamodb()`` counterpart.
        """
        return cls(
            key=raw.get("key", ""),
            data=S3VectorData(**raw.get("data", {"float32": []})),
            **raw.get("metadata", {}),
        )
