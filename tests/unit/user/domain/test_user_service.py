import pytest
from pydantic import BaseModel

from src._core.application.dtos.base_response import PaginationInfo
from src.user.domain.dtos.user_dto import UserDTO
from src.user.domain.services.user_service import UserService
from src.user.interface.server.dtos.user_dto import UpdateUserRequest
from tests.factories.user_factory import make_create_user_request, make_user_dto


class MockUserRepository:
    """Protocol 기반 Mock — UserRepository를 상속하지 않아도 됨"""

    def __init__(self):
        self._store: dict[int, UserDTO] = {}
        self._next_id = 1

    async def insert_data(self, entity: BaseModel) -> UserDTO:
        dto = make_user_dto(id=self._next_id, **entity.model_dump())
        self._store[self._next_id] = dto
        self._next_id += 1
        return dto

    async def insert_datas(self, entities: list[BaseModel]) -> list[UserDTO]:
        return [await self.insert_data(e) for e in entities]

    async def select_datas(self, page: int, page_size: int) -> list[UserDTO]:
        items = list(self._store.values())
        start = (page - 1) * page_size
        return items[start : start + page_size]

    async def select_data_by_id(self, data_id: int) -> UserDTO:
        if data_id not in self._store:
            raise Exception(f"User {data_id} not found")
        return self._store[data_id]

    async def select_datas_by_ids(self, data_ids: list[int]) -> list[UserDTO]:
        return [self._store[i] for i in data_ids if i in self._store]

    async def select_datas_with_count(
        self, page: int, page_size: int
    ) -> tuple[list[UserDTO], int]:
        return await self.select_datas(page, page_size), len(self._store)

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

    async def count_datas(self) -> int:
        return len(self._store)


@pytest.fixture
def user_service():
    return UserService(user_repository=MockUserRepository())


@pytest.mark.asyncio
async def test_create_user(user_service):
    request = make_create_user_request()
    result = await user_service.create_data(entity=request)

    assert result.id == 1
    assert result.username == request.username
    assert result.email == request.email
    assert result.password == request.password


@pytest.mark.asyncio
async def test_get_user_by_id(user_service):
    request = make_create_user_request()
    created = await user_service.create_data(entity=request)

    result = await user_service.get_data_by_data_id(data_id=created.id)
    assert result.id == created.id
    assert result.username == created.username


@pytest.mark.asyncio
async def test_update_user(user_service):
    request = make_create_user_request()
    created = await user_service.create_data(entity=request)

    update_request = UpdateUserRequest(full_name="Updated Name")
    result = await user_service.update_data_by_data_id(
        data_id=created.id, entity=update_request
    )
    assert result.full_name == "Updated Name"
    assert result.username == created.username  # 변경 안 됨


@pytest.mark.asyncio
async def test_delete_user(user_service):
    request = make_create_user_request()
    created = await user_service.create_data(entity=request)

    success = await user_service.delete_data_by_data_id(data_id=created.id)
    assert success is True

    count = await user_service.count_datas()
    assert count == 0


@pytest.mark.asyncio
async def test_get_datas_returns_pagination(user_service):
    for i in range(3):
        await user_service.create_data(
            entity=make_create_user_request(username=f"user{i}")
        )

    datas, pagination = await user_service.get_datas(page=1, page_size=2)

    assert len(datas) == 2
    assert isinstance(pagination, PaginationInfo)
    assert pagination.total_items == 3
    assert pagination.total_pages == 2
    assert pagination.has_next is True
    assert pagination.has_previous is False
