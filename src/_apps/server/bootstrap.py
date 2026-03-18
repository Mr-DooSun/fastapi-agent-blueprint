import importlib

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware

from src._apps.server.di.container import create_server_container
from src._core.application.routers.api import docs_router, health_check_router
from src._core.config import settings
from src._core.infrastructure.discovery import discover_domains
from src._core.middleware.exception_middleware import ExceptionMiddleware


def bootstrap_app(app: FastAPI) -> None:
    # 미들웨어 설정
    app.add_middleware(ExceptionMiddleware)

    # TrustedHostMiddleware 설정
    app.add_middleware(TrustedHostMiddleware, allowed_hosts=settings.allowed_hosts)

    # CORSMiddleware 설정
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allow_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # 공통 라우터 (Core)
    app.include_router(router=health_check_router.router, tags=["status", "NEW"])
    if settings.is_dev:
        app.include_router(router=docs_router.router, tags=["docs"])

    # 각 도메인 bootstrap (자동 발견)
    server_container = create_server_container()
    _bootstrap_domains(app=app, server_container=server_container)


def _bootstrap_domains(app: FastAPI, server_container) -> None:
    """discover_domains()로 탐지된 모든 도메인을 동적으로 bootstrap한다."""
    for name in discover_domains():
        module_path = f"src.{name}.interface.server.bootstrap.{name}_bootstrap"
        module = importlib.import_module(module_path)
        bootstrap_fn = getattr(module, f"bootstrap_{name}_domain")
        domain_container = getattr(server_container, f"{name}_container")

        bootstrap_fn(
            app=app,
            database=server_container.core_container.database(),
            **{f"{name}_container": domain_container},
        )
