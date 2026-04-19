import os

import pytest
import pytest_asyncio

from src._core.infrastructure.database.config import DatabaseConfig
from src._core.infrastructure.database.database import Base, Database


def _build_test_database() -> Database:
    """Construct the test Database based on ``TEST_DB_ENGINE``.

    Default: SQLite in-memory — no external infra, fast, CI-friendly.
    ``TEST_DB_ENGINE=postgresql``: connect to the local docker PostgreSQL
    (see ``docker-compose.local.yml``). Use ``make test-pg`` for this path.
    """
    engine = os.environ.get("TEST_DB_ENGINE", "sqlite").lower()
    config = DatabaseConfig(echo=False)

    if engine == "postgresql":
        return Database(
            database_engine="postgresql",
            database_user=os.environ.get("TEST_DB_USER", "postgres"),
            database_password=os.environ.get("TEST_DB_PASSWORD", "postgres"),
            database_host=os.environ.get("TEST_DB_HOST", "localhost"),
            database_port=int(os.environ.get("TEST_DB_PORT", "5432")),
            database_name=os.environ.get("TEST_DB_NAME", "postgres"),
            config=config,
        )

    return Database(
        database_engine="sqlite",
        database_user="",
        database_password="",
        database_host="",
        database_port=0,
        database_name=":memory:",
        config=config,
    )


@pytest_asyncio.fixture(scope="session")
async def test_db():
    db = _build_test_database()
    async with db.async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield db
    async with db.async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await db.dispose()


@pytest_asyncio.fixture(autouse=True, scope="session")
async def _override_app_database(test_db):
    """Swap the app's PostgreSQL Database for the active ``test_db``.

    The FastAPI app boots a real PostgreSQL Singleton at import time
    (`src._apps.server.app.app`). E2E tests must run without external infra,
    so we override the running container instance attached to ``app.state``.
    """
    from src._apps.server.app import app

    container = app.state.container
    core = container.core_container()
    core.database.override(test_db)
    yield
    core.database.reset_override()


@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"
