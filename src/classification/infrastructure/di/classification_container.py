from dependency_injector import containers, providers

from src.classification.domain.services.classification_service import (
    ClassificationService,
)


class ClassificationContainer(containers.DeclarativeContainer):
    core_container = providers.DependenciesContainer()

    classification_service = providers.Factory(
        ClassificationService,
        llm_config=core_container.llm_config,
    )
