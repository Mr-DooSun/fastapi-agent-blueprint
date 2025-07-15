# -*- coding: utf-8 -*-
# flake8: noqa: F401, F403

import os
from logging.config import fileConfig
from urllib.parse import quote_plus

from alembic import context
from dotenv import load_dotenv
from sqlalchemy import create_engine

from migrations.env_utils import create_folder_if_not_exists, load_models
from src.core.infrastructure.database.database import Base, create_sync_dsn

# Alembic 설정 파일 로드
config = context.config

env = config.get_main_option("env")
if env != "dev" and env != "prod" and env != "stg":
    raise RuntimeError(
        "alembic.ini 파일에 ENV 환경변수가 지정되지 않았습니다. [dev], [prod], [stg] 중 하나를 입력해주세요."
    )
else:
    if not os.path.exists(f"_env/{env}.env"):
        raise RuntimeError(f"환경변수 파일이 존재하지 않습니다. {f'_env/{env}.env'}")
    print("=" * 100)
    print(f"alembic.ini 파일에 선택된 ENV: {env}")
    print("=" * 100)

create_folder_if_not_exists("migrations/versions")

load_models()

load_dotenv(dotenv_path=f"_env/{env}.env", override=True)

if config.config_file_name is not None:
    fileConfig(config.config_file_name)


url = create_sync_dsn(
    database_user=quote_plus(os.getenv("DATABASE_USER") or ""),
    database_password=quote_plus(os.getenv("DATABASE_PASSWORD") or ""),
    database_host=os.getenv("DATABASE_HOST") or "",
    database_port=int(os.getenv("DATABASE_PORT") or ""),
    database_name=os.getenv("DATABASE_NAME") or "",
)

# Base.metadata로 target_metadata 지정
target_metadata = Base.metadata


# Migration 실행 함수
def run_migrations_offline() -> None:
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    connectable = create_engine(
        url=url,
    )
    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            include_schemas=False,
        )
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
