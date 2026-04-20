import importlib

from taskiq import AsyncBroker, TaskiqState

from src._apps.worker.broker import container
from src._apps.worker.di.container import create_worker_container
from src._core.config import settings
from src._core.infrastructure.discovery import discover_domains
from src._core.infrastructure.logging.configure import configure_logging
from src._core.infrastructure.logging.taskiq_middleware import (
    StructlogContextMiddleware,
)


def bootstrap_app(app: AsyncBroker) -> None:
    # Structured logging — configure once before any task can run so worker
    # logs (including the CLI startup banner) land in the same JSON /
    # console pipeline as the server (#9).
    configure_logging(
        log_level=settings.log_level,
        json_logs=settings.effective_log_json,
    )

    # Bind correlation IDs and task identifiers on every task execution so
    # logs emitted from tasks carry the same request_id that dispatched
    # them (when the dispatcher used ``.with_labels(correlation_id=...)``).
    app.add_middlewares(StructlogContextMiddleware())

    @app.on_event("startup")
    async def startup(state: TaskiqState):
        worker_container = create_worker_container(core_container=container)
        _bootstrap_domains(app=app, worker_container=worker_container)


def _bootstrap_domains(app: AsyncBroker, worker_container) -> None:
    """Dynamically bootstrap workers for all domains detected by discover_domains()."""
    for name in discover_domains():
        module_path = f"src.{name}.interface.worker.bootstrap.{name}_bootstrap"
        module = importlib.import_module(module_path)
        bootstrap_fn = getattr(module, f"bootstrap_{name}_domain")
        domain_container = getattr(worker_container, f"{name}_container")

        bootstrap_fn(app=app, **{f"{name}_container": domain_container})
