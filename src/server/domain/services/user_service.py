# -*- coding: utf-8 -*-


from src.core.application.dtos.user_dto import CoreCreateUserDto, CoreUpdateUserDto, CoreUserDto
from src.core.domain.services.base_service import BaseService
from src.server.infrastructure.repositories.user_repository import UserRepository


class UserService(BaseService):
    def __init__(self, user_repository: UserRepository) -> None:
        super().__init__(base_repository=user_repository)

    @property
    def create_dto(self):
        return CoreCreateUserDto

    @property
    def response_dto(self):
        return CoreUserDto

    @property
    def update_dto(self):
        return CoreUpdateUserDto
