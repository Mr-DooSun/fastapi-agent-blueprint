from pydantic import BaseModel

from src.user.domain.dtos.user_dto import UserDTO
from src.user.domain.protocols.user_repository_protocol import UserRepositoryProtocol


class UserService:
    def __init__(self, user_repository: UserRepositoryProtocol) -> None:
        self.user_repository = user_repository

    async def create_data(self, entity: BaseModel) -> UserDTO:
        return await self.user_repository.insert_data(entity=entity)

    async def create_datas(self, entities: list[BaseModel]) -> list[UserDTO]:
        return await self.user_repository.insert_datas(entities=entities)

    async def get_datas_with_count(
        self, page: int, page_size: int
    ) -> tuple[list[UserDTO], int]:
        return await self.user_repository.select_datas_with_count(
            page=page, page_size=page_size
        )

    async def get_data_by_data_id(self, data_id: int) -> UserDTO:
        return await self.user_repository.select_data_by_id(data_id=data_id)

    async def get_datas_by_data_ids(self, data_ids: list[int]) -> list[UserDTO]:
        return await self.user_repository.select_datas_by_ids(data_ids=data_ids)

    async def update_data_by_data_id(self, data_id: int, entity: BaseModel) -> UserDTO:
        return await self.user_repository.update_data_by_data_id(
            data_id=data_id, entity=entity
        )

    async def delete_data_by_data_id(self, data_id: int) -> bool:
        return await self.user_repository.delete_data_by_data_id(data_id=data_id)

    async def count_datas(self) -> int:
        return await self.user_repository.count_datas()
