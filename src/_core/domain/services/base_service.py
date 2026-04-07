from __future__ import annotations

from typing import TYPE_CHECKING, Generic, TypeVar

from pydantic import BaseModel

from src._core.application.dtos.base_response import PaginationInfo
from src._core.common.pagination import make_pagination
from src._core.domain.protocols.repository_protocol import BaseRepositoryProtocol

if TYPE_CHECKING:
    from src._core.domain.value_objects.query_filter import QueryFilter

ReturnDTO = TypeVar("ReturnDTO", bound=BaseModel)


class BaseService(Generic[ReturnDTO]):
    def __init__(self, repository: BaseRepositoryProtocol[ReturnDTO]) -> None:
        self.repository = repository

    async def create_data(self, entity: BaseModel) -> ReturnDTO:
        return await self.repository.insert_data(entity=entity)

    async def create_datas(self, entities: list[BaseModel]) -> list[ReturnDTO]:
        return await self.repository.insert_datas(entities=entities)

    async def get_datas(
        self,
        page: int,
        page_size: int,
        query_filter: QueryFilter | None = None,
    ) -> tuple[list[ReturnDTO], PaginationInfo]:
        datas, total_items = await self.repository.select_datas_with_count(
            page=page,
            page_size=page_size,
            query_filter=query_filter,
        )
        pagination = make_pagination(
            total_items=total_items, page=page, page_size=page_size
        )
        return datas, pagination

    async def get_data_by_data_id(self, data_id: int) -> ReturnDTO:
        return await self.repository.select_data_by_id(data_id=data_id)

    async def get_datas_by_data_ids(self, data_ids: list[int]) -> list[ReturnDTO]:
        return await self.repository.select_datas_by_ids(data_ids=data_ids)

    async def update_data_by_data_id(
        self, data_id: int, entity: BaseModel
    ) -> ReturnDTO:
        return await self.repository.update_data_by_data_id(
            data_id=data_id, entity=entity
        )

    async def delete_data_by_data_id(self, data_id: int) -> bool:
        return await self.repository.delete_data_by_data_id(data_id=data_id)

    async def count_datas(self) -> int:
        return await self.repository.count_datas()
