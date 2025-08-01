# -*- coding: utf-8 -*-
from abc import ABC
from typing import Generic, List, Type, TypeVar

from sqlalchemy import func, select
from sqlalchemy.orm import selectinload

from src.core.domain.entities.entity import Entity
from src.core.exceptions.base_exception import BaseCustomException
from src.core.infrastructure.database.database import Base, Database

CreateEntity = TypeVar("CreateEntity", bound=Entity)
ReturnEntity = TypeVar("ReturnEntity", bound=Entity)
UpdateEntity = TypeVar("UpdateEntity", bound=Entity)


class BaseRepository(Generic[CreateEntity, ReturnEntity, UpdateEntity], ABC):
    def __init__(
        self,
        database: Database,
        *,
        model: Type[Base],
        create_entity: Type[CreateEntity],
        return_entity: Type[ReturnEntity],
        update_entity: Type[UpdateEntity],
    ) -> None:
        self.database = database
        self.model = model
        self.create_entity = create_entity
        self.return_entity = return_entity
        self.update_entity = update_entity

    async def create_data(self, create_data: CreateEntity) -> ReturnEntity:
        async with self.database.session() as session:
            data = self.model(**create_data.model_dump(exclude_none=True))
            session.add(data)
            await session.commit()
            await session.refresh(data)
            return self.return_entity.model_validate(data, from_attributes=True)

    async def create_datas(
        self, create_datas: List[CreateEntity]
    ) -> List[ReturnEntity]:
        async with self.database.session() as session:
            datas = [
                self.model(**create_data.model_dump(exclude_none=True))
                for create_data in create_datas
            ]
            session.add_all(datas)
            await session.flush()
            await session.commit()
            return [
                self.return_entity.model_validate(data, from_attributes=True)
                for data in datas
            ]

    async def get_datas(self, page: int, page_size: int) -> List[ReturnEntity]:
        async with self.database.session() as session:
            result = await session.execute(
                select(self.model)
                .options(selectinload(self.model.related_entities))
                .offset((page - 1) * page_size)
                .limit(page_size)
            )
            datas = result.scalars().all()

            return [
                self.return_entity.model_validate(data, from_attributes=True)
                for data in datas
            ]

    async def get_data_by_data_id(self, data_id: int) -> ReturnEntity:
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

    async def get_datas_by_data_ids(self, data_ids: List[int]) -> List[ReturnEntity]:
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

    async def count_datas(self) -> int:
        async with self.database.session() as session:
            result = await session.execute(select(func.count()).select_from(self.model))
            return result.scalar_one()

    async def update_data_by_data_id(
        self, data_id: int, update_data: UpdateEntity
    ) -> ReturnEntity:
        async with self.database.session() as session:
            result = await session.execute(
                select(self.model).filter(self.model.id == data_id)
            )
            data = result.scalar_one_or_none()
            if not data:
                raise BaseCustomException(
                    status_code=404, message=f"Data with ID [ {data_id} ] not found"
                )
            for key, value in update_data.model_dump(exclude_none=True).items():
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
            if data:
                await session.delete(data)
                await session.commit()
                return True
            return False
