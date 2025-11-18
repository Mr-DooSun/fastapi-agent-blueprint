from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src._apps.server.di.container import ServerContainer
from src._core.application.routers.api import docs_router, health_check_router
from src._core.config import settings
from src._core.middleware.exception_middleware import ExceptionMiddleware
from src.user.interface.server.bootstrap.user_bootstrap import bootstrap_user_domain


def bootstrap_app(app: FastAPI) -> None:
    # 미들웨어 설정
    app.add_middleware(ExceptionMiddleware)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # 공통 라우터 (Core)
    app.include_router(router=health_check_router.router, tags=["status", "NEW"])
    if settings.is_dev:
        app.include_router(router=docs_router.router, tags=["docs"])

    # 각 도메인 bootstrap
    server_container = ServerContainer()
    bootstrap_user_domain(
        app=app,
        database=server_container.core_container.database(),
        user_container=server_container.user_container,
    )
