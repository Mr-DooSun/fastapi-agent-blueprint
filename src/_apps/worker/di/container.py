from dependency_injector import containers, providers

from src.user.infrastructure.di.user_container import UserContainer


class WorkerContainer(containers.DeclarativeContainer):
    core_container = providers.DependenciesContainer()

    user_container = providers.Container(UserContainer, core_container=core_container)
