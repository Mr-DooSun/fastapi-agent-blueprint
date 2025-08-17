# -*- coding: utf-8 -*-
from dependency_injector import containers, providers

from src.core.infrastructure.di.core_container import CoreContainer
from src.consumer.infrastructure.di.containers.storage_container import StorageContainer


class ConsumerContainer(containers.DeclarativeContainer):
    core_container = providers.Container(CoreContainer)

    storage_container = providers.Container(StorageContainer, core_container=core_container)