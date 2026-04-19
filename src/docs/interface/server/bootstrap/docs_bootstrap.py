"""Docs domain independent bootstrap."""

from __future__ import annotations

from fastapi import FastAPI

from src._core.infrastructure.persistence.rdb.database import Database
from src.docs.infrastructure.di.docs_container import DocsContainer
from src.docs.interface.server.routers import docs_router


def create_docs_container(docs_container: DocsContainer) -> DocsContainer:
    docs_container.wire(packages=["src.docs.interface.server.routers"])
    return docs_container


def setup_docs_routes(app: FastAPI) -> None:
    """Register docs domain routes."""
    app.include_router(router=docs_router.router, prefix="/v1", tags=["Docs"])


def bootstrap_docs_domain(
    app: FastAPI, database: Database, docs_container: DocsContainer
) -> None:
    docs_container = create_docs_container(docs_container=docs_container)
    setup_docs_routes(app=app)
