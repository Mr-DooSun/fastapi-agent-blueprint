from sqlalchemy import text

from src._core.exceptions.base_exception import BaseCustomException
from src._core.infrastructure.database.database import Database


class HealthCheckException(BaseCustomException):
    pass


class HealthService:
    """Infrastructure health check — not a domain service, bypasses Repository by design."""

    def __init__(self, database: Database) -> None:
        self._database = database

    async def check_database(self) -> bool:
        try:
            async with self._database.session() as session:
                await session.execute(text("SELECT 1"))
                return True
        except Exception:
            raise HealthCheckException(
                status_code=503,
                message="Database health check failed",
                error_code="DATABASE_UNHEALTHY",
            )
