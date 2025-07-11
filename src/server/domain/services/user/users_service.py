# -*- coding: utf-8 -*-


from src.core.application.dtos.user.users_dto import (
    CoreCreateUsersDto,
    CoreUpdateUsersDto,
    CoreUsersDto,
)
from src.core.domain.services.base_service import BaseService
from src.server.infrastructure.repositories.user.users_repository import UsersRepository


class UsersService(BaseService):
    def __init__(self, users_repository: UsersRepository) -> None:
        super().__init__(base_repository=users_repository)

    @property
    def create_dto(self):
        return CoreCreateUsersDto

    @property
    def response_dto(self):
        return CoreUsersDto

    @property
    def update_dto(self):
        return CoreUpdateUsersDto
