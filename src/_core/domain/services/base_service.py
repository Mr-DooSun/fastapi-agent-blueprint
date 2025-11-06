from abc import ABC
from typing import Generic, TypeVar

from src._core.domain.entities.entity import Entity
from src._core.infrastructure.database.base_repository import BaseRepository

CreateEntity = TypeVar("CreateEntity", bound=Entity)
ReturnEntity = TypeVar("ReturnEntity", bound=Entity)
UpdateEntity = TypeVar("UpdateEntity", bound=Entity)


class BaseService(Generic[CreateEntity, ReturnEntity, UpdateEntity], ABC):
    def __init__(
        self,
        base_repository: BaseRepository,
        *,
        create_entity: type[CreateEntity],
        return_entity: type[ReturnEntity],
        update_entity: type[UpdateEntity],
    ) -> None:
        self.base_repository = base_repository
        self.create_entity = create_entity
        self.return_entity = return_entity
        self.update_entity = update_entity

    async def create_data(self, entity: CreateEntity) -> ReturnEntity:
        return await self.base_repository.insert_data(entity=entity)

    async def create_datas(self, entities: list[CreateEntity]) -> list[ReturnEntity]:
        return await self.base_repository.insert_datas(entities=entities)

    async def get_datas(self, page: int, page_size: int) -> list[ReturnEntity]:
        return await self.base_repository.select_datas(page=page, page_size=page_size)

    async def get_data_by_data_id(self, data_id: int) -> ReturnEntity:
        return await self.base_repository.select_data_by_id(data_id=data_id)

    async def get_datas_by_data_ids(self, data_ids: list[int]) -> list[ReturnEntity]:
        return await self.base_repository.select_datas_by_ids(data_ids=data_ids)

    async def count_datas(self) -> int:
        return await self.base_repository.count_datas()

    async def get_datas_with_count(
        self, page: int, page_size: int
    ) -> tuple[list[ReturnEntity], int]:
        return await self.base_repository.select_datas_with_count(
            page=page, page_size=page_size
        )

    async def update_data_by_data_id(
        self, data_id: int, entity: UpdateEntity
    ) -> ReturnEntity:
        return await self.base_repository.update_data_by_data_id(
            data_id=data_id, entity=entity
        )

    async def delete_data_by_data_id(self, data_id: int) -> bool:
        return await self.base_repository.delete_data_by_data_id(data_id=data_id)
