import importlib

import structlog
from asgi_correlation_id import CorrelationIdMiddleware
from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from starlette.exceptions import HTTPException as StarletteHTTPException

from src._apps.server.di.container import create_server_container
from src._core.application.routers.api import docs_router, health_check_router
from src._core.config import settings
from src._core.exceptions.base_exception import BaseCustomException
from src._core.exceptions.exception_handlers import (
    custom_exception_handler,
    generic_exception_handler,
    http_exception_handler,
    validation_exception_handler,
)
from src._core.infrastructure.discovery import discover_domains
from src._core.infrastructure.logging.configure import configure_logging
from src._core.infrastructure.logging.request_log_middleware import (
    RequestLogMiddleware,
)
from src._core.infrastructure.persistence.rdb.database import Base, Database

_logger = structlog.stdlib.get_logger("src._apps.server.bootstrap")


def bootstrap_app(app: FastAPI) -> None:
    # Structured logging — configure once before any route or middleware can
    # emit a record so startup logs (including our own) land in the chosen
    # pipeline (JSON in stg/prod, coloured console in dev) (#9).
    configure_logging(
        log_level=settings.log_level,
        json_logs=settings.effective_log_json,
    )

    # Exception handlers
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)
    app.add_exception_handler(BaseCustomException, custom_exception_handler)
    app.add_exception_handler(Exception, generic_exception_handler)

    # Middlewares — Starlette applies the LAST one added as the OUTERMOST.
    # ``CorrelationIdMiddleware`` must see the raw request first (so it can
    # read / generate the X-Request-ID header before the log middleware
    # tries to bind it), so it is added AFTER the request-log middleware.
    # Order after registration becomes:
    #   Request → CorrelationId → RequestLog → CORS → TrustedHost → App
    app.add_middleware(TrustedHostMiddleware, allowed_hosts=settings.allowed_hosts)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allow_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.add_middleware(RequestLogMiddleware)
    app.add_middleware(CorrelationIdMiddleware)

    # Bootstrap DI container (auto-discovery)
    server_container = create_server_container()
    app.state.container = server_container

    # Quickstart convenience: auto-create tables from model metadata so that
    # `make quickstart` works with an empty SQLite file and no migrations.
    # Real environments (local/dev/stg/prod) must use Alembic.
    if settings.env.lower() == "quickstart":
        _auto_create_tables(server_container.core_container.database())

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

    # Bootstrap admin dashboard (NiceGUI) — gated on the ``admin`` extra
    _maybe_bootstrap_admin(app=app)


def _maybe_bootstrap_admin(app: FastAPI) -> None:
    """Mount the NiceGUI admin dashboard if the ``admin`` extra is installed.

    ``nicegui`` is an optional dependency — installing it is gated behind the
    ``admin`` extra (``uv sync --extra admin``). If it is absent, the server
    still boots; the admin routes simply are not mounted (the #101 acceptance
    criterion for API-only deployments). The skip path emits a structured
    ``admin_mount_skipped`` record so operators who expected the dashboard at
    ``/admin`` can diagnose from logs without re-reading the README.
    """
    try:
        from src._apps.admin.bootstrap import bootstrap_admin
    except ImportError:
        _logger.info(
            "admin_mount_skipped",
            reason="nicegui_not_installed",
            install_hint="uv sync --extra admin",
        )
        return

    bootstrap_admin(app)


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


def _auto_create_tables(database: Database) -> None:
    """Create tables from SQLAlchemy metadata — quickstart only.

    Invoked at bootstrap time when ``ENV=quickstart`` so a fresh SQLite file
    immediately has the schema needed for the `user` domain (and any other
    domain whose models are registered on ``Base.metadata``).

    Real deployments use Alembic migrations; calling ``create_all`` against
    a non-sqlite engine would mask migration drift.
    """
    Base.metadata.create_all(database.engine)
