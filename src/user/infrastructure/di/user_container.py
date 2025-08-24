# -*- coding: utf-8 -*-

from dependency_injector import containers, providers

from src.user.domain.services.users_service import UsersService
from src.user.infrastructure.repositories.users_repository import (
    UsersRepository,
)
from src.user.server.application.use_cases.users_use_case import UsersUseCase


class UserContainer(containers.DeclarativeContainer):
    core_container = providers.DependenciesContainer()

    users_repository = providers.Singleton(
        UsersRepository,
        database=core_container.database,
    )

    users_service = providers.Factory(
        UsersService,
        users_repository=users_repository,
    )

    users_use_case = providers.Factory(
        UsersUseCase,
        users_service=users_service,
    )
