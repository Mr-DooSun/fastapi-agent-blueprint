# -*- coding: utf-8 -*-
from src.core.application.responses.base import BaseResponse
from src.core.domain.entities.user_entity import UserEntity


class UserDto(UserEntity):
    pass


class UserResponse(BaseResponse):
    data: UserDto
