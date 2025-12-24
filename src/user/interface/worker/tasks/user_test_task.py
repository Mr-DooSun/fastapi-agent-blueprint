from dependency_injector.wiring import Provide, inject

from src._apps.worker.broker import broker
from src.user.application.use_cases.user_use_case import UserUseCase
from src.user.domain.entities.user_entity import UserEntity
from src.user.infrastructure.di.user_container import UserContainer


@broker.task(task_name="{project-name}.user.test")
@inject
async def consume_task(
    user_use_case: UserUseCase = Provide[UserContainer.user_use_case],
    **kwargs,
) -> None:
    entity = UserEntity.model_validate(kwargs)

    await user_use_case.process_user(entity=entity)
