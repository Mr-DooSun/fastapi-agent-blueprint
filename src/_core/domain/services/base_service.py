from abc import ABC
from typing import Generic, TypeVar

from pydantic import BaseModel

from src._core.domain.protocols.repository_protocol import BaseRepositoryProtocol

CreateDTO = TypeVar("CreateDTO", bound=BaseModel)
ReturnDTO = TypeVar("ReturnDTO", bound=BaseModel)
UpdateDTO = TypeVar("UpdateDTO", bound=BaseModel)


class BaseService(Generic[CreateDTO, ReturnDTO, UpdateDTO], ABC):
    def __init__(
        self,
        base_repository: BaseRepositoryProtocol,
        *,
        create_entity: type[CreateDTO],
        return_entity: type[ReturnDTO],
        update_entity: type[UpdateDTO],
    ) -> None:
        self.base_repository = base_repository
        self.create_entity = create_entity
        self.return_entity = return_entity
        self.update_entity = update_entity

    async def create_data(self, entity: CreateDTO) -> ReturnDTO:
        return await self.base_repository.insert_data(entity=entity)

    async def create_datas(self, entities: list[CreateDTO]) -> list[ReturnDTO]:
        return await self.base_repository.insert_datas(entities=entities)

    async def get_datas(self, page: int, page_size: int) -> list[ReturnDTO]:
        return await self.base_repository.select_datas(page=page, page_size=page_size)

    async def get_data_by_data_id(self, data_id: int) -> ReturnDTO:
        return await self.base_repository.select_data_by_id(data_id=data_id)

    async def get_datas_by_data_ids(self, data_ids: list[int]) -> list[ReturnDTO]:
        return await self.base_repository.select_datas_by_ids(data_ids=data_ids)

    async def count_datas(self) -> int:
        return await self.base_repository.count_datas()

    async def get_datas_with_count(
        self, page: int, page_size: int
    ) -> tuple[list[ReturnDTO], int]:
        return await self.base_repository.select_datas_with_count(
            page=page, page_size=page_size
        )

    async def update_data_by_data_id(
        self, data_id: int, entity: UpdateDTO
    ) -> ReturnDTO:
        return await self.base_repository.update_data_by_data_id(
            data_id=data_id, entity=entity
        )

    async def delete_data_by_data_id(self, data_id: int) -> bool:
        return await self.base_repository.delete_data_by_data_id(data_id=data_id)
