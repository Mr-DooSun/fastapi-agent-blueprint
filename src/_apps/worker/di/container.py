from dependency_injector import containers, providers

from src._core.infrastructure.di.core_container import CoreContainer
from src.user.infrastructure.di.user_container import UserContainer


class WorkerContainer(containers.DeclarativeContainer):
    core_container = providers.Container(CoreContainer)

    user_container = providers.Container(UserContainer, core_container=core_container)
