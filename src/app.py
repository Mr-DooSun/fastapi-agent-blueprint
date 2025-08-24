# -*- coding: utf-8 -*-
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.core.application.routers.api import docs_router, health_check_router
from src.core.infrastructure.di.core_container import CoreContainer
from src.core.middleware.exception_middleware import ExceptionMiddleware
from src.user.server.infrastructure.bootstrap.user_bootstrap import (
    bootstrap_user_domain,
)


def create_app():
    """모놀리식 DDD FastAPI 앱 - 도메인별 독립 구성을 통합"""
    app = FastAPI(
        title="FastAPI Layered Architecture (Monolith)",
        description="DDD 기반 모놀리식 아키텍처 - 각 도메인이 독립적으로 구성됨",
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

    # 도메인별 독립 설정
    core_container = CoreContainer()
    database = core_container.database()

    # User 도메인 bootstrap
    bootstrap_user_domain(app, database=database)

    return app


app = create_app()
