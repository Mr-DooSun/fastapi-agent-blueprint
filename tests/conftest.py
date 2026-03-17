import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from src._core.infrastructure.database.database import Base, Database


@pytest_asyncio.fixture(scope="session")
async def test_engine():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    await engine.dispose()


@pytest_asyncio.fixture
async def test_db(test_engine) -> Database:
    db = Database.__new__(Database)
    db.async_engine = test_engine
    db.engine = None
    db.async_session_factory = sessionmaker(
        bind=test_engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autoflush=False,
        autocommit=False,
    )
    return db


@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"
