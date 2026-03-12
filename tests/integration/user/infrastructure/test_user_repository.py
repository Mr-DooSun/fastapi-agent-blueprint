import pytest

from src.user.domain.dtos.user_dto import UpdateUserDTO
from src.user.infrastructure.repositories.user_repository import UserRepository
from tests.factories.user_factory import make_create_user_dto


@pytest.mark.asyncio
async def test_insert_and_select(test_db):
    repo = UserRepository(database=test_db)
    dto = make_create_user_dto()

    created = await repo.insert_data(entity=dto)
    assert created.id is not None
    assert created.username == dto.username

    fetched = await repo.select_data_by_id(data_id=created.id)
    assert fetched.id == created.id
    assert fetched.email == dto.email


@pytest.mark.asyncio
async def test_update(test_db):
    repo = UserRepository(database=test_db)
    created = await repo.insert_data(entity=make_create_user_dto())

    updated = await repo.update_data_by_data_id(
        data_id=created.id,
        entity=UpdateUserDTO(full_name="New Name"),
    )
    assert updated.full_name == "New Name"
    assert updated.username == created.username


@pytest.mark.asyncio
async def test_delete(test_db):
    repo = UserRepository(database=test_db)
    created = await repo.insert_data(entity=make_create_user_dto())

    result = await repo.delete_data_by_data_id(data_id=created.id)
    assert result is True


@pytest.mark.asyncio
async def test_count(test_db):
    repo = UserRepository(database=test_db)
    for i in range(3):
        await repo.insert_data(entity=make_create_user_dto(username=f"countuser{i}"))

    count = await repo.count_datas()
    assert count >= 3
