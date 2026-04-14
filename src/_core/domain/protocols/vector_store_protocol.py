from __future__ import annotations

from collections.abc import Sequence
from typing import TYPE_CHECKING, Generic, TypeVar

from pydantic import BaseModel

if TYPE_CHECKING:
    from src._core.domain.value_objects.vector_query import VectorQuery
    from src._core.domain.value_objects.vector_search_result import VectorSearchResult

ReturnDTO = TypeVar("ReturnDTO", bound=BaseModel)


class BaseVectorStoreProtocol(Generic[ReturnDTO]):
    """Backend-agnostic vector store protocol.

    Abstraction boundary for vector storage implementations.
    Both S3 Vectors and future pgvector implement this protocol.
    Domain services inject this protocol directly.
    """

    async def upsert(self, entities: Sequence[BaseModel]) -> int: ...

    async def search(self, query: VectorQuery) -> VectorSearchResult[ReturnDTO]: ...

    async def get(self, keys: list[str]) -> list[ReturnDTO]: ...

    async def delete(self, keys: list[str]) -> bool: ...
