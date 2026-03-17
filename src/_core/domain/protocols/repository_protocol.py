from typing import Generic, TypeVar

from pydantic import BaseModel

CreateDTO = TypeVar("CreateDTO", bound=BaseModel)
ReturnDTO = TypeVar("ReturnDTO", bound=BaseModel)
UpdateDTO = TypeVar("UpdateDTO", bound=BaseModel)


class BaseRepositoryProtocol(Generic[CreateDTO, ReturnDTO, UpdateDTO]):
    async def insert_data(self, entity: CreateDTO) -> ReturnDTO: ...

    async def insert_datas(self, entities: list[CreateDTO]) -> list[ReturnDTO]: ...

    async def select_datas(self, page: int, page_size: int) -> list[ReturnDTO]: ...

    async def select_data_by_id(self, data_id: int) -> ReturnDTO: ...

    async def select_datas_by_ids(self, data_ids: list[int]) -> list[ReturnDTO]: ...

    async def select_datas_with_count(
        self, page: int, page_size: int
    ) -> tuple[list[ReturnDTO], int]: ...

    async def update_data_by_data_id(
        self, data_id: int, entity: UpdateDTO
    ) -> ReturnDTO: ...

    async def delete_data_by_data_id(self, data_id: int) -> bool: ...

    async def count_datas(self) -> int: ...
