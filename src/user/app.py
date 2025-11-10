from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src._core.application.routers.api import docs_router, health_check_router
from src._core.infrastructure.di.core_container import CoreContainer
from src._core.middleware.exception_middleware import ExceptionMiddleware
from src.user.infrastructure.di.user_container import UserContainer
from src.user.interface.server.bootstrap.user_bootstrap import bootstrap_user_domain


def create_container():
    """User 도메인 전용 DI 컨테이너"""
    core_container = CoreContainer()
    container = UserContainer(core_container=core_container)
    container.wire(packages=["src.user.server.application.routers"])
    return container


def create_app():
    """User 도메인 전용 FastAPI 앱 - 마이크로서비스"""
    container = create_container()

    app = FastAPI(
        title="User Service",
        description="사용자 관리 마이크로서비스",
        version="1.0.0",
        root_path="/api",
        docs_url="/docs-swagger",
        redoc_url="/docs-redoc",
    )

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
    app.include_router(router=health_check_router.router, tags=["status"])
    app.include_router(router=docs_router.router, tags=["docs"])

    # User 도메인 완전 독립 설정
    bootstrap_user_domain(
        app, database=container.core_container.database(), user_container=container
    )

    return app


app = create_app()
