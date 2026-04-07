from __future__ import annotations

from typing import TYPE_CHECKING, Generic, TypeVar

from pydantic import BaseModel

if TYPE_CHECKING:
    from src._core.domain.value_objects.query_filter import QueryFilter

ReturnDTO = TypeVar("ReturnDTO", bound=BaseModel)


class BaseRepositoryProtocol(Generic[ReturnDTO]):
    async def insert_data(self, entity: BaseModel) -> ReturnDTO: ...

    async def insert_datas(self, entities: list[BaseModel]) -> list[ReturnDTO]: ...

    async def select_datas(self, page: int, page_size: int) -> list[ReturnDTO]: ...

    async def select_data_by_id(self, data_id: int) -> ReturnDTO: ...

    async def select_datas_by_ids(self, data_ids: list[int]) -> list[ReturnDTO]: ...

    async def select_datas_with_count(
        self,
        page: int,
        page_size: int,
        query_filter: QueryFilter | None = None,
    ) -> tuple[list[ReturnDTO], int]: ...

    async def update_data_by_data_id(
        self, data_id: int, entity: BaseModel
    ) -> ReturnDTO: ...

    async def delete_data_by_data_id(self, data_id: int) -> bool: ...

    async def count_datas(self) -> int: ...
