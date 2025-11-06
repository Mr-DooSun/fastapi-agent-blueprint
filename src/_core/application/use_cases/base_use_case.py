from abc import ABC
from typing import Generic, TypeVar

from src._core.application.dtos.base_response import PaginationInfo
from src._core.common.pagination import make_pagination
from src._core.domain.entities.entity import Entity
from src._core.domain.services.base_service import BaseService

CreateEntity = TypeVar("CreateEntity", bound=Entity)
ReturnEntity = TypeVar("ReturnEntity", bound=Entity)
UpdateEntity = TypeVar("UpdateEntity", bound=Entity)


class BaseUseCase(Generic[CreateEntity, ReturnEntity, UpdateEntity], ABC):
    def __init__(
        self,
        base_service: BaseService,
        *,
        create_entity: type[CreateEntity],
        return_entity: type[ReturnEntity],
        update_entity: type[UpdateEntity],
    ) -> None:
        self.base_service = base_service
        self.create_entity = create_entity
        self.return_entity = return_entity
        self.update_entity = update_entity

    async def create_data(self, entity: CreateEntity) -> ReturnEntity:
        return await self.base_service.create_data(entity=entity)

    async def create_datas(self, entities: list[CreateEntity]) -> list[ReturnEntity]:
        return await self.base_service.create_datas(entities=entities)

    async def get_datas(
        self, page: int, page_size: int
    ) -> tuple[list[ReturnEntity], PaginationInfo]:
        datas, total_items = await self.base_service.get_datas_with_count(
            page=page, page_size=page_size
        )

        pagination = make_pagination(
            total_items=total_items, page=page, page_size=page_size
        )

        return datas, pagination

    async def get_data_by_data_id(self, data_id: int) -> ReturnEntity:
        return await self.base_service.get_data_by_data_id(data_id=data_id)

    async def get_datas_by_data_ids(self, data_ids: list[int]) -> list[ReturnEntity]:
        return await self.base_service.get_datas_by_data_ids(data_ids=data_ids)

    async def update_data_by_data_id(
        self, data_id: int, entity: UpdateEntity
    ) -> ReturnEntity:
        return await self.base_service.update_data_by_data_id(
            data_id=data_id, entity=entity
        )

    async def delete_data_by_data_id(self, data_id: int) -> bool:
        return await self.base_service.delete_data_by_data_id(data_id=data_id)
