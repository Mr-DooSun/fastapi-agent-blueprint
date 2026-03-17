from pydantic import BaseModel

from src._core.application.dtos.base_response import PaginationInfo
from src._core.common.pagination import make_pagination
from src.user.domain.dtos.user_dto import UserDTO
from src.user.domain.services.user_service import UserService


class UserUseCase:
    def __init__(self, user_service: UserService) -> None:
        self.user_service = user_service

    async def create_data(self, entity: BaseModel) -> UserDTO:
        return await self.user_service.create_data(entity=entity)

    async def create_datas(self, entities: list[BaseModel]) -> list[UserDTO]:
        return await self.user_service.create_datas(entities=entities)

    async def get_datas(
        self, page: int, page_size: int
    ) -> tuple[list[UserDTO], PaginationInfo]:
        datas, total_items = await self.user_service.get_datas_with_count(
            page=page, page_size=page_size
        )
        pagination = make_pagination(
            total_items=total_items, page=page, page_size=page_size
        )
        return datas, pagination

    async def get_data_by_data_id(self, data_id: int) -> UserDTO:
        return await self.user_service.get_data_by_data_id(data_id=data_id)

    async def get_datas_by_data_ids(self, data_ids: list[int]) -> list[UserDTO]:
        return await self.user_service.get_datas_by_data_ids(data_ids=data_ids)

    async def update_data_by_data_id(self, data_id: int, entity: BaseModel) -> UserDTO:
        return await self.user_service.update_data_by_data_id(
            data_id=data_id, entity=entity
        )

    async def delete_data_by_data_id(self, data_id: int) -> bool:
        return await self.user_service.delete_data_by_data_id(data_id=data_id)
