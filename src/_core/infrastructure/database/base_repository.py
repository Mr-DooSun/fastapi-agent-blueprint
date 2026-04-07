from __future__ import annotations

from abc import ABC
from typing import TYPE_CHECKING, Generic, TypeVar

from pydantic import BaseModel
from sqlalchemy import String, func, or_, select
from sqlalchemy.orm import InstrumentedAttribute

from src._core.exceptions.base_exception import BaseCustomException
from src._core.infrastructure.database.database import Base, Database

if TYPE_CHECKING:
    from src._core.domain.value_objects.query_filter import QueryFilter

ReturnDTO = TypeVar("ReturnDTO", bound=BaseModel)


class BaseRepository(Generic[ReturnDTO], ABC):
    def __init__(
        self,
        database: Database,
        *,
        model: type[Base],
        return_entity: type[ReturnDTO],
    ) -> None:
        self.database = database
        self.model = model
        self.return_entity = return_entity

    async def insert_data(self, entity: BaseModel) -> ReturnDTO:
        async with self.database.session() as session:
            data = self.model(**entity.model_dump(exclude_none=True))
            session.add(data)
            await session.commit()
            await session.refresh(data)
            return self.return_entity.model_validate(data, from_attributes=True)

    async def insert_datas(self, entities: list[BaseModel]) -> list[ReturnDTO]:
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

            # Load relationships only when needed
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
        self,
        page: int,
        page_size: int,
        query_filter: QueryFilter | None = None,
    ) -> tuple[list[ReturnDTO], int]:
        """Fetch data and count in a single session to optimize connection pool usage."""
        async with self.database.session() as session:
            query = select(self.model)
            count_query = select(func.count()).select_from(self.model)

            if query_filter:
                # Apply search filter
                if query_filter.search_query and query_filter.search_fields:
                    conditions = []
                    for field_name in query_filter.search_fields:
                        col = getattr(self.model, field_name, None)
                        if isinstance(col, InstrumentedAttribute) and isinstance(
                            col.type, String
                        ):
                            conditions.append(
                                col.ilike(f"%{query_filter.search_query}%")
                            )
                    if conditions:
                        query = query.where(or_(*conditions))
                        count_query = count_query.where(or_(*conditions))

                # Apply sorting
                if query_filter.sort_field and hasattr(
                    self.model, query_filter.sort_field
                ):
                    column = getattr(self.model, query_filter.sort_field)
                    query = query.order_by(
                        column.asc()
                        if query_filter.sort_order == "asc"
                        else column.desc()
                    )

            result = await session.execute(
                query.offset((page - 1) * page_size).limit(page_size)
            )
            datas = result.scalars().all()

            count_result = await session.execute(count_query)
            total_count = count_result.scalar_one()

            # Load relationships only when needed
            if hasattr(self.model, "related_entities"):
                await session.refresh(datas, ["related_entities"])

            return [
                self.return_entity.model_validate(data, from_attributes=True)
                for data in datas
            ], total_count

    async def update_data_by_data_id(
        self, data_id: int, entity: BaseModel
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
