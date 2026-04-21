import importlib

import structlog
from taskiq import AsyncBroker, TaskiqState

from src._apps.worker.broker import container
from src._apps.worker.di.container import create_worker_container
from src._core.config import settings
from src._core.infrastructure.discovery import discover_domains
from src._core.infrastructure.logging.configure import configure_logging
from src._core.infrastructure.logging.taskiq_middleware import (
    StructlogContextMiddleware,
)

_logger = structlog.stdlib.get_logger("src._apps.worker.bootstrap")


def bootstrap_app(app: AsyncBroker) -> None:
    _configure_logging_pipeline()
    _install_middleware(app)
    _register_startup_event(app)


# ---------------------------------------------------------------------------
# Private orchestration steps
# ---------------------------------------------------------------------------


def _configure_logging_pipeline() -> None:
    """Configure structlog before any task can run."""
    configure_logging(
        log_level=settings.log_level,
        json_logs=settings.effective_log_json,
    )


def _install_middleware(app: AsyncBroker) -> None:
    """Bind correlation IDs and task identifiers on every task execution."""
    app.add_middlewares(StructlogContextMiddleware())


def _register_startup_event(app: AsyncBroker) -> None:
    @app.on_event("startup")
    async def startup(state: TaskiqState):
        worker_container = create_worker_container(core_container=container)
        _bootstrap_domains(worker_container=worker_container)


def _bootstrap_domains(worker_container) -> None:
    """Dynamically bootstrap all domains detected by discover_domains().

    Domains without a worker bootstrap module are silently skipped so that
    server-only domains do not crash the worker boot.
    """
    for name in discover_domains():
        module_path = f"src.{name}.interface.worker.bootstrap.{name}_bootstrap"
        try:
            module = importlib.import_module(module_path)
            bootstrap_fn = getattr(module, f"bootstrap_{name}_domain")
        except (ModuleNotFoundError, AttributeError):
            _logger.debug("domain_worker_bootstrap_skipped", domain=name)
            continue

        domain_container = getattr(worker_container, f"{name}_container")
        bootstrap_fn(**{f"{name}_container": domain_container})
