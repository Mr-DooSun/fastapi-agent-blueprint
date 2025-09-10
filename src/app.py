# -*- coding: utf-8 -*-
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src._core.application.dtos.base_response import ErrorResponse
from src._core.application.routers.api import docs_router, health_check_router
from src._core.middleware.exception_middleware import ExceptionMiddleware
from src._shared.infrastructure.di.server_container import ServerContainer
from src.user.interface.server.bootstrap.user_bootstrap import bootstrap_user_domain


def create_app():
    server_container = ServerContainer()
    database = server_container.core_container.database()

    app = FastAPI(
        title="FastAPI Layered Architecture (Monolith)",
        description="DDD 기반 모놀리식 아키텍처 - 각 도메인이 독립적으로 구성됨",
        version="1.0.0",
        root_path="/api",
        docs_url="/docs-swagger",
        redoc_url="/docs-redoc",
        responses={
            400: {"model": ErrorResponse, "description": "잘못된 요청"},
            401: {"model": ErrorResponse, "description": "인증 필요 또는 토큰 불일치"},
            403: {"model": ErrorResponse, "description": "권한 없음"},
            404: {"model": ErrorResponse, "description": "해당 리소스 없음"},
            500: {"model": ErrorResponse, "description": "서버 오류"},
        },
    )

    app.add_middleware(ExceptionMiddleware)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(router=health_check_router.router, tags=["status"])
    app.include_router(router=docs_router.router, tags=["docs"])

    bootstrap_user_domain(
        app=app, database=database, user_container=server_container.user_container
    )

    return app


app = create_app()
