# -*- coding: utf-8 -*-


from src._core.application.use_cases.base_use_case import BaseUseCase
from src.user.domain.entities.users_entity import (
    CoreCreateUsersEntity,
    CoreUpdateUsersEntity,
    CoreUsersEntity,
)
from src.user.domain.services.users_service import UsersService


class UsersUseCase(
    BaseUseCase[CoreCreateUsersEntity, CoreUsersEntity, CoreUpdateUsersEntity]
):
    def __init__(self, users_service: UsersService) -> None:
        super().__init__(
            base_service=users_service,
            create_entity=CoreCreateUsersEntity,
            return_entity=CoreUsersEntity,
            update_entity=CoreUpdateUsersEntity,
        )
