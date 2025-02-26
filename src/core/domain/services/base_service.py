# -*- coding: utf-8 -*-
import logging
from abc import ABC, abstractmethod
from typing import List, Type, TypeVar

from pydantic import BaseModel

from src.core.infrastructure.repositories.base_repository import BaseRepository

CreateDTO = TypeVar("CreateDTO", bound=BaseModel)
UpdateDTO = TypeVar("UpdateDTO", bound=BaseModel)
ResponseDTO = TypeVar("ResponseDTO", bound=BaseModel)


class BaseService(ABC):
    def __init__(
        self,
        base_repository: BaseRepository,
    ) -> None:
        self.base_repository = base_repository
        self.logger = logging.getLogger(__name__)

    @property
    @abstractmethod
    def create_dto(self) -> Type[CreateDTO]:
        pass

    @property
    @abstractmethod
    def response_dto(self) -> Type[ResponseDTO]:
        pass

    @property
    @abstractmethod
    def update_dto(self) -> Type[UpdateDTO]:
        pass

    async def create_data(self, create_data: CreateDTO) -> ResponseDTO:
        return await self.base_repository.create_data(create_data=create_data)

    async def create_datas(self, create_datas: List[CreateDTO]) -> List[ResponseDTO]:
        return await self.base_repository.create_datas(create_datas=create_datas)

    async def get_datas(self, page: int, page_size: int) -> List[ResponseDTO]:
        return await self.base_repository.get_datas(page=page, page_size=page_size)

    async def get_data_by_data_id(self, data_id: int) -> ResponseDTO:
        return await self.base_repository.get_data_by_data_id(data_id=data_id)

    async def update_data_by_data_id(
        self, data_id: int, update_data: UpdateDTO
    ) -> ResponseDTO:
        return await self.base_repository.update_data_by_data_id(
            data_id=data_id, update_data=update_data
        )

    async def delete_data_by_data_id(self, data_id: int):
        await self.base_repository.delete_data_by_data_id(data_id=data_id)
