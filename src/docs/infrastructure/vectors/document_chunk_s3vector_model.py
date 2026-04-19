from __future__ import annotations

from typing import ClassVar

from src._core.infrastructure.s3vectors.s3vector_model import (
    S3VectorModel,
    S3VectorModelMeta,
)


class DocumentChunkS3VectorModel(S3VectorModel):
    """S3 Vectors model for a single docs-domain chunk.

    Mirrors ``BaseChunkDTO`` fields so both the InMemory and S3 backends
    share one serialization contract. ``dimension`` is inherited from
    ``settings.embedding_dimension`` via ``S3VectorModelMeta`` default.
    """

    __s3vector_meta__: ClassVar[S3VectorModelMeta] = S3VectorModelMeta(
        index_name="docs-document-chunks",
        filter_fields=["source_id"],
        non_filter_fields=["content", "source_title", "chunk_index"],
    )

    source_id: str
    source_title: str
    content: str
    chunk_index: int
