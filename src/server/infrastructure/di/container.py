# -*- coding: utf-8 -*-
from dependency_injector import providers

from src.core.infrastructure.di.container import CoreContainer
from src.server.domain.services.user_service import UserService
from src.server.infrastructure.repositories.user_repository import UserRepository


class ServerContainer(CoreContainer):
    user_repository = providers.Singleton(
        UserRepository,
        session=CoreContainer.database,
    )

    user_service = providers.Factory(
        UserService,
        user_repository=user_repository,
    )
