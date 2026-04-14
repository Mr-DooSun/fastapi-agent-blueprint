"""Unit tests for S3VectorModel serialization."""

from typing import ClassVar

from src._core.infrastructure.s3vectors.s3vector_model import (
    S3VectorData,
    S3VectorModel,
    S3VectorModelMeta,
)


class SampleS3VectorModel(S3VectorModel):
    """Test vector model -- demonstrates how domains define models."""

    __s3vector_meta__: ClassVar[S3VectorModelMeta] = S3VectorModelMeta(
        index_name="test-documents",
        dimension=4,
        distance_metric="cosine",
        filter_fields=["category", "author_id"],
        non_filter_fields=["content_preview"],
    )

    category: str
    author_id: str
    content_preview: str


class TestS3VectorModelSerialization:
    def test_to_s3vector_structure(self):
        model = SampleS3VectorModel(
            key="vec-001",
            data=S3VectorData(float32=[0.1, 0.2, 0.3, 0.4]),
            category="tech",
            author_id="user-1",
            content_preview="Sample content",
        )
        result = model.to_s3vector()

        assert result["key"] == "vec-001"
        assert result["data"] == {"float32": [0.1, 0.2, 0.3, 0.4]}
        assert result["metadata"] == {
            "category": "tech",
            "author_id": "user-1",
            "content_preview": "Sample content",
        }

    def test_to_s3vector_excludes_key_and_data_from_metadata(self):
        model = SampleS3VectorModel(
            key="vec-001",
            data=S3VectorData(float32=[0.1, 0.2, 0.3, 0.4]),
            category="tech",
            author_id="user-1",
            content_preview="Content",
        )
        result = model.to_s3vector()

        assert "key" not in result["metadata"]
        assert "data" not in result["metadata"]

    def test_from_s3vector_roundtrip(self):
        original = SampleS3VectorModel(
            key="vec-001",
            data=S3VectorData(float32=[0.1, 0.2, 0.3, 0.4]),
            category="tech",
            author_id="user-1",
            content_preview="Content",
        )
        serialized = original.to_s3vector()

        raw = {
            "key": serialized["key"],
            "data": serialized["data"],
            "metadata": serialized["metadata"],
        }
        restored = SampleS3VectorModel.from_s3vector(raw)

        assert restored.key == "vec-001"
        assert restored.category == "tech"
        assert restored.author_id == "user-1"
        assert restored.content_preview == "Content"
        assert restored.data.float32 == [0.1, 0.2, 0.3, 0.4]

    def test_default_key_generated(self):
        model = SampleS3VectorModel(
            data=S3VectorData(float32=[0.1, 0.2, 0.3, 0.4]),
            category="tech",
            author_id="user-1",
            content_preview="Content",
        )
        assert model.key
        assert len(model.key) == 32  # UUID v4 hex

    def test_none_metadata_excluded(self):
        """Optional metadata fields excluded when None."""

        class OptionalMetaModel(S3VectorModel):
            __s3vector_meta__: ClassVar[S3VectorModelMeta] = S3VectorModelMeta(
                index_name="test-optional", dimension=4
            )
            required_field: str
            optional_field: str | None = None

        model = OptionalMetaModel(
            data=S3VectorData(float32=[0.1, 0.2, 0.3, 0.4]),
            required_field="value",
        )
        result = model.to_s3vector()

        assert "optional_field" not in result["metadata"]
        assert result["metadata"]["required_field"] == "value"


class TestS3VectorModelMeta:
    def test_defaults(self):
        meta = S3VectorModelMeta(index_name="test")
        assert meta.data_type == "float32"
        assert meta.dimension == 1536
        assert meta.distance_metric == "cosine"
        assert meta.filter_fields == []
        assert meta.non_filter_fields == []

    def test_custom_values(self):
        meta = S3VectorModelMeta(
            index_name="custom",
            dimension=768,
            distance_metric="euclidean",
            filter_fields=["a", "b"],
            non_filter_fields=["c"],
        )
        assert meta.dimension == 768
        assert meta.distance_metric == "euclidean"
        assert meta.filter_fields == ["a", "b"]
