from abc import ABC
from typing import Generic, TypeVar

from pydantic import BaseModel

from src._core.application.dtos.base_response import PaginationInfo
from src._core.common.pagination import make_pagination
from src._core.domain.services.base_service import BaseService

CreateDTO = TypeVar("CreateDTO", bound=BaseModel)
ReturnDTO = TypeVar("ReturnDTO", bound=BaseModel)
UpdateDTO = TypeVar("UpdateDTO", bound=BaseModel)


class BaseUseCase(Generic[CreateDTO, ReturnDTO, UpdateDTO], ABC):
    def __init__(
        self,
        base_service: BaseService,
        *,
        create_entity: type[CreateDTO],
        return_entity: type[ReturnDTO],
        update_entity: type[UpdateDTO],
    ) -> None:
        self.base_service = base_service
        self.create_entity = create_entity
        self.return_entity = return_entity
        self.update_entity = update_entity

    async def create_data(self, entity: CreateDTO) -> ReturnDTO:
        return await self.base_service.create_data(entity=entity)

    async def create_datas(self, entities: list[CreateDTO]) -> list[ReturnDTO]:
        return await self.base_service.create_datas(entities=entities)

    async def get_datas(
        self, page: int, page_size: int
    ) -> tuple[list[ReturnDTO], PaginationInfo]:
        datas, total_items = await self.base_service.get_datas_with_count(
            page=page, page_size=page_size
        )
        pagination = make_pagination(
            total_items=total_items, page=page, page_size=page_size
        )
        return datas, pagination

    async def get_data_by_data_id(self, data_id: int) -> ReturnDTO:
        return await self.base_service.get_data_by_data_id(data_id=data_id)

    async def get_datas_by_data_ids(self, data_ids: list[int]) -> list[ReturnDTO]:
        return await self.base_service.get_datas_by_data_ids(data_ids=data_ids)

    async def update_data_by_data_id(
        self, data_id: int, entity: UpdateDTO
    ) -> ReturnDTO:
        return await self.base_service.update_data_by_data_id(
            data_id=data_id, entity=entity
        )

    async def delete_data_by_data_id(self, data_id: int) -> bool:
        return await self.base_service.delete_data_by_data_id(data_id=data_id)
