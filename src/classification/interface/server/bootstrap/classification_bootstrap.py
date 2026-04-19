"""Classification domain independent bootstrap"""

from fastapi import FastAPI

from src._core.infrastructure.persistence.rdb.database import Database
from src.classification.infrastructure.di.classification_container import (
    ClassificationContainer,
)
from src.classification.interface.server.routers import classification_router


def create_classification_container(
    classification_container: ClassificationContainer,
):
    classification_container.wire(
        packages=["src.classification.interface.server.routers"]
    )
    return classification_container


def setup_classification_routes(app: FastAPI):
    """Register classification domain routes"""
    app.include_router(
        router=classification_router.router, prefix="/v1", tags=["Classification"]
    )


def bootstrap_classification_domain(
    app: FastAPI,
    database: Database,
    classification_container: ClassificationContainer,
):
    classification_container = create_classification_container(
        classification_container=classification_container
    )
    setup_classification_routes(app=app)
