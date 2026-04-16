from dependency_injector import containers, providers

from src.classification.domain.services.classification_service import (
    ClassificationService,
)


class ClassificationContainer(containers.DeclarativeContainer):
    core_container = providers.DependenciesContainer()

    classification_service = providers.Factory(
        ClassificationService,
        llm_model=core_container.llm_model,
    )
