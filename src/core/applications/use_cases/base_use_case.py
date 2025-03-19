# -*- coding: utf-8 -*-
from abc import ABC, abstractmethod
from typing import List, Type, TypeVar

from pydantic import BaseModel

from src.core.applications.responses.base_response import BaseResponse, PaginationInfo
from src.core.domain.services.base_service import BaseService

CreateDTO = TypeVar("CreateDTO", bound=BaseModel)
UpdateDTO = TypeVar("UpdateDTO", bound=BaseModel)
ResponseDto = TypeVar("ResponseDto", bound=BaseResponse)


class BaseUseCase(ABC):
    def __init__(
        self,
        base_service: BaseService,
    ) -> None:
        self.base_service = base_service

    @property
    @abstractmethod
    def create_dto(self) -> Type[CreateDTO]:
        pass

    @property
    @abstractmethod
    def response_dto(self) -> Type[ResponseDto]:
        pass

    @property
    @abstractmethod
    def update_dto(self) -> Type[UpdateDTO]:
        pass

    async def create_data(self, create_data: CreateDTO) -> ResponseDto:
        return await self.base_service.create_data(create_data=create_data)

    async def create_datas(self, create_datas: List[CreateDTO]) -> List[ResponseDto]:
        return await self.base_service.create_datas(create_datas=create_datas)

    async def get_datas(self, page: int, page_size: int) -> List[ResponseDto]:
        datas = await self.base_service.get_datas(page=page, page_size=page_size)

        total_items = await self.base_service.count_datas()
        total_pages = (total_items + page_size - 1) // page_size

        pagination = PaginationInfo(
            current_page=page,
            page_size=page_size,
            total_items=total_items,
            total_pages=total_pages,
            has_previous=page > 1,
            has_next=page < total_pages,
            next_page=page + 1 if page < total_pages else None,
            previous_page=page - 1 if page > 1 else None,
        )

        return datas, pagination

    async def get_data_by_data_id(self, data_id: int) -> ResponseDto:
        return await self.base_service.get_data_by_data_id(data_id=data_id)

    async def update_data_by_data_id(
        self, data_id: int, update_data: UpdateDTO
    ) -> ResponseDto:
        return await self.base_service.update_data_by_data_id(
            data_id=data_id, update_data=update_data
        )

    async def delete_data_by_data_id(self, data_id: int):
        await self.base_service.delete_data_by_data_id(data_id=data_id)
