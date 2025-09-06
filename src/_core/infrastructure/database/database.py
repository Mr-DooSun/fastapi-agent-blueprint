# -*- coding: utf-8 -*-
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from urllib.parse import quote_plus

from fastapi import HTTPException
from sqlalchemy import create_engine
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker


def create_async_dsn(
    database_user: str,
    database_password: str,
    database_host: str,
    database_port: int,
    database_name: str,
):
    return f"mysql+aiomysql://{database_user}:{database_password}@{database_host}:{database_port}/{database_name}?charset=utf8mb4"


def create_sync_dsn(
    database_user: str,
    database_password: str,
    database_host: str,
    database_port: int,
    database_name: str,
):
    return f"mysql+pymysql://{database_user}:{database_password}@{database_host}:{database_port}/{database_name}?charset=utf8mb4"


def get_database_config(env: str):
    if env == "prod":
        return {
            "echo": False,
            "pool_size": 10,
            "max_overflow": 20,
            "pool_pre_ping": True,
            "pool_recycle": 3600,
            "connect_args": {
                "timeout": 10,
                "connect_timeout": 10,
                "command_timeout": 30,
                "server_settings": {
                    "statement_timeout": "30000",
                    "idle_in_transaction_session_timeout": "300000",
                    "application_name": "server_api",
                },
            },
        }
    else:
        return {"echo": True, "pool_size": 5, "max_overflow": 10, "pool_pre_ping": True}


class Base(DeclarativeBase):
    pass


class Database:
    def __init__(
        self,
        env: str,
        database_user: str,
        database_password: str,
        database_host: str,
        database_port: int,
        database_name: str,
    ) -> None:
        dsn = create_sync_dsn(
            database_user=quote_plus(database_user),
            database_password=quote_plus(database_password),
            database_host=database_host,
            database_port=database_port,
            database_name=database_name,
        )

        async_dsn = create_async_dsn(
            database_user=quote_plus(database_user),
            database_password=quote_plus(database_password),
            database_host=database_host,
            database_port=database_port,
            database_name=database_name,
        )

        self.engine = create_engine(url=dsn, echo=False)
        self.async_engine = create_async_engine(
            url=async_dsn,
            **get_database_config(env=env),
        )

        self.async_session_factory = sessionmaker(
            bind=self.async_engine,
            class_=AsyncSession,
            expire_on_commit=False,
            autoflush=False,
            autocommit=False,
        )

    @asynccontextmanager
    async def session(self) -> AsyncGenerator[AsyncSession, None]:
        session = None

        try:
            session = self.async_session_factory()
            yield session
        except IntegrityError:
            if session:
                await session.rollback()
            raise HTTPException(status_code=400, detail="Data integrity error")
        except Exception:
            if session:
                await session.rollback()
            raise HTTPException(status_code=500, detail="Internal server error")
        finally:
            if session:
                await session.close()
