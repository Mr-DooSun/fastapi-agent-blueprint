import pytest
from pydantic import BaseModel

from src._core.application.dtos.base_response import PaginationInfo
from src.user.application.use_cases.user_use_case import UserUseCase
from src.user.domain.dtos.user_dto import UserDTO
from tests.factories.user_factory import make_create_user_request, make_user_dto


class MockUserService:
    """Service Mock — DB 없이 UseCase 로직만 테스트"""

    def __init__(self):
        self._store: dict[int, UserDTO] = {}
        self._next_id = 1

    async def create_data(self, entity: BaseModel) -> UserDTO:
        dto = make_user_dto(id=self._next_id, **entity.model_dump())
        self._store[self._next_id] = dto
        self._next_id += 1
        return dto

    async def create_datas(self, entities: list[BaseModel]) -> list[UserDTO]:
        return [await self.create_data(e) for e in entities]

    async def get_datas_with_count(
        self, page: int, page_size: int
    ) -> tuple[list[UserDTO], int]:
        items = list(self._store.values())
        start = (page - 1) * page_size
        return items[start : start + page_size], len(self._store)

    async def get_data_by_data_id(self, data_id: int) -> UserDTO:
        return self._store[data_id]

    async def get_datas_by_data_ids(self, data_ids: list[int]) -> list[UserDTO]:
        return [self._store[i] for i in data_ids if i in self._store]

    async def update_data_by_data_id(self, data_id: int, entity: BaseModel) -> UserDTO:
        dto = self._store[data_id]
        updated = dto.model_copy(
            update={k: v for k, v in entity.model_dump().items() if v is not None}
        )
        self._store[data_id] = updated
        return updated

    async def delete_data_by_data_id(self, data_id: int) -> bool:
        self._store.pop(data_id, None)
        return True


@pytest.fixture
def user_use_case():
    return UserUseCase(user_service=MockUserService())


@pytest.mark.asyncio
async def test_create_user(user_use_case):
    request = make_create_user_request()
    result = await user_use_case.create_data(entity=request)

    assert result.id == 1
    assert result.username == request.username


@pytest.mark.asyncio
async def test_get_datas_returns_pagination(user_use_case):
    for i in range(3):
        await user_use_case.create_data(
            entity=make_create_user_request(username=f"user{i}")
        )

    datas, pagination = await user_use_case.get_datas(page=1, page_size=2)

    assert len(datas) == 2
    assert isinstance(pagination, PaginationInfo)
    assert pagination.total_items == 3
    assert pagination.total_pages == 2
    assert pagination.has_next is True
    assert pagination.has_previous is False
