from abc import ABC
from typing import Generic, TypeVar

from pydantic import BaseModel
from sqlalchemy import func, select

from src._core.exceptions.base_exception import BaseCustomException
from src._core.infrastructure.database.database import Base, Database

CreateDTO = TypeVar("CreateDTO", bound=BaseModel)
ReturnDTO = TypeVar("ReturnDTO", bound=BaseModel)
UpdateDTO = TypeVar("UpdateDTO", bound=BaseModel)


class BaseRepository(Generic[CreateDTO, ReturnDTO, UpdateDTO], ABC):
    def __init__(
        self,
        database: Database,
        *,
        model: type[Base],
        create_entity: type[CreateDTO],
        return_entity: type[ReturnDTO],
        update_entity: type[UpdateDTO],
    ) -> None:
        self.database = database
        self.model = model
        self.create_entity = create_entity
        self.return_entity = return_entity
        self.update_entity = update_entity

    async def insert_data(self, entity: CreateDTO) -> ReturnDTO:
        async with self.database.session() as session:
            data = self.model(**entity.model_dump(exclude_none=True))
            session.add(data)
            await session.commit()
            await session.refresh(data)
            return self.return_entity.model_validate(data, from_attributes=True)

    async def insert_datas(self, entities: list[CreateDTO]) -> list[ReturnDTO]:
        async with self.database.session() as session:
            datas = [
                self.model(**entity.model_dump(exclude_none=True))
                for entity in entities
            ]
            session.add_all(datas)
            await session.flush()
            await session.commit()
            return [
                self.return_entity.model_validate(data, from_attributes=True)
                for data in datas
            ]

    async def select_datas(self, page: int, page_size: int) -> list[ReturnDTO]:
        async with self.database.session() as session:
            result = await session.execute(
                select(self.model).offset((page - 1) * page_size).limit(page_size)
            )
            datas = result.scalars().all()

            # 필요한 경우에만 관계 로딩
            if hasattr(self.model, "related_entities"):
                await session.refresh(datas, ["related_entities"])

            return [
                self.return_entity.model_validate(data, from_attributes=True)
                for data in datas
            ]

    async def select_data_by_id(self, data_id: int) -> ReturnDTO:
        async with self.database.session() as session:
            result = await session.execute(
                select(self.model).filter(self.model.id == data_id)
            )
            data = result.scalar_one_or_none()
            if not data:
                raise BaseCustomException(
                    status_code=404, message=f"Data with ID [ {data_id} ] not found"
                )
            return self.return_entity.model_validate(data, from_attributes=True)

    async def select_datas_by_ids(self, data_ids: list[int]) -> list[ReturnDTO]:
        if not data_ids:
            return []
        async with self.database.session() as session:
            result = await session.execute(
                select(self.model).where(self.model.id.in_(data_ids))
            )
            datas = result.scalars().all()
            return [
                self.return_entity.model_validate(data, from_attributes=True)
                for data in datas
            ]

    async def select_datas_with_count(
        self, page: int, page_size: int
    ) -> tuple[list[ReturnDTO], int]:
        """데이터 조회와 카운트를 하나의 세션에서 처리하여 연결 풀 사용 최적화"""
        async with self.database.session() as session:
            # 데이터 조회
            result = await session.execute(
                select(self.model).offset((page - 1) * page_size).limit(page_size)
            )
            datas = result.scalars().all()

            # 카운트 조회 (동일 세션)
            count_result = await session.execute(
                select(func.count()).select_from(self.model)
            )
            total_count = count_result.scalar_one()

            # 필요한 경우에만 관계 로딩
            if hasattr(self.model, "related_entities"):
                await session.refresh(datas, ["related_entities"])

            return [
                self.return_entity.model_validate(data, from_attributes=True)
                for data in datas
            ], total_count

    async def update_data_by_data_id(
        self, data_id: int, entity: UpdateDTO
    ) -> ReturnDTO:
        async with self.database.session() as session:
            result = await session.execute(
                select(self.model).filter(self.model.id == data_id)
            )
            data = result.scalar_one_or_none()
            if not data:
                raise BaseCustomException(
                    status_code=404, message=f"Data with ID [ {data_id} ] not found"
                )
            for key, value in entity.model_dump(exclude_none=True).items():
                setattr(data, key, value)
            await session.commit()
            await session.refresh(data)
            return self.return_entity.model_validate(data, from_attributes=True)

    async def delete_data_by_data_id(self, data_id: int) -> bool:
        async with self.database.session() as session:
            result = await session.execute(
                select(self.model).filter(self.model.id == data_id)
            )
            data = result.scalar_one_or_none()
            if not data:
                raise BaseCustomException(
                    status_code=404, message=f"Data with ID [ {data_id} ] not found"
                )
            await session.delete(data)
            await session.commit()
            return True

    async def count_datas(self) -> int:
        async with self.database.session() as session:
            result = await session.execute(select(func.count()).select_from(self.model))
            return result.scalar_one()
