"""Test helpers for server-level DI overrides.

Import these in ``tests/e2e/conftest.py`` instead of reaching into the
container internals directly. This decouples test code from the container
structure so internal refactors do not break test fixtures.

Usage::

    from src._apps.server.testing import override_database, reset_database_override

    override_database(app, test_db)
    yield
    reset_database_override(app)
"""

from __future__ import annotations

from fastapi import FastAPI

from src._core.infrastructure.persistence.rdb.database import Database


def override_database(app: FastAPI, test_db: Database) -> None:
    """Replace the running app's Database singleton with ``test_db``."""
    _core(app).database.override(test_db)


def reset_database_override(app: FastAPI) -> None:
    """Restore the original Database singleton."""
    _core(app).database.reset_override()


def _core(app: FastAPI):
    return app.state.container.core_container()
