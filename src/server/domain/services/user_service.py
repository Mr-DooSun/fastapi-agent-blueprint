# -*- coding: utf-8 -*-


from src.core.applications.dtos.user_dto import CreateUserDto, UpdateUserDto, UserDto
from src.core.domain.services.base_service import BaseService
from src.server.infrastructure.repositories.user_repository import UserRepository


class UserService(BaseService):
    def __init__(self, user_repository: UserRepository) -> None:
        super().__init__(base_repository=user_repository)

    @property
    def create_dto(self):
        return CreateUserDto

    @property
    def response_dto(self):
        return UserDto

    @property
    def update_dto(self):
        return UpdateUserDto
