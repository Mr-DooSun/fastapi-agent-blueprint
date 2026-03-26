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
    # Middleware setup
    app.add_middleware(ExceptionMiddleware)

    # TrustedHostMiddleware setup
    app.add_middleware(TrustedHostMiddleware, allowed_hosts=settings.allowed_hosts)

    # CORSMiddleware setup
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allow_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Bootstrap DI container (auto-discovery)
    server_container = create_server_container()

    # Wire core container for health check DI
    # (core is not a domain — no separate bootstrap file needed)
    server_container.core_container().wire(
        modules=["src._core.application.routers.api.health_check_router"]
    )

    # Core routers
    app.include_router(router=health_check_router.router, tags=["status", "NEW"])
    if settings.is_dev:
        app.include_router(router=docs_router.router, tags=["docs"])

    # Bootstrap each domain
    _bootstrap_domains(app=app, server_container=server_container)


def _bootstrap_domains(app: FastAPI, server_container) -> None:
    """Dynamically bootstrap all domains detected by discover_domains()."""
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
