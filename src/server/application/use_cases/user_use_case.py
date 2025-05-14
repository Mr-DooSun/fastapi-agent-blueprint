# -*- coding: utf-8 -*-


from src.core.application.dtos.user_dto import CoreCreateUserDto, CoreUpdateUserDto, CoreUserDto
from src.core.application.use_cases.base_use_case import BaseUseCase
from src.server.domain.services.user_service import UserService


class UserUseCase(BaseUseCase):
    def __init__(self, user_service: UserService) -> None:
        super().__init__(base_service=user_service)

    @property
    def create_dto(self):
        return CoreCreateUserDto

    @property
    def response_dto(self):
        return CoreUserDto

    @property
    def update_dto(self):
        return CoreUpdateUserDto
