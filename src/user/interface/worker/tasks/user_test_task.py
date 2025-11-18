import asyncio

from celery import shared_task
from dependency_injector.wiring import Provide, inject

from src.user.application.use_cases.user_use_case import UserUseCase
from src.user.domain.entities.user_entity import UserEntity
from src.user.infrastructure.di.user_container import UserContainer


@shared_task(name="{project-name}.user.test")
@inject
def consume_task(
    user_use_case: UserUseCase = Provide[UserContainer.user_use_case],
    **kwargs,
):
    entity = UserEntity.model_validate(kwargs)

    asyncio.run(user_use_case.process_user(entity=entity))
