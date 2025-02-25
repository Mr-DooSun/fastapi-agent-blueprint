# -*- coding: utf-8 -*-


from src.core.application.dtos.user_dto import CreateUserDto, UpdateUserDto
from src.core.application.responses.user_response import UserDto
from src.core.application.services.base_service import BaseService
from src.server.infrastructure.repositories.user_repository import UserRepository


class UserService(BaseService):
    def __init__(self, user_repository: UserRepository) -> None:
        super().__init__(base_repository=user_repository)
        self.users_repository = user_repository

    @property
    def create_dto(self):
        return CreateUserDto

    @property
    def response_dto(self):
        return UserDto

    @property
    def update_dto(self):
        return UpdateUserDto
