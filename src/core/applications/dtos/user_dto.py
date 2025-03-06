# -*- coding: utf-8 -*-

from src.core.applications.dtos.base_request import BaseRequest
from src.core.domain.entities.user_entity import (
    CreateUserEntity,
    UpdateUserEntity,
    UserEntity,
)


class UserDto(UserEntity):
    pass


class CreateUserDto(BaseRequest, CreateUserEntity):
    pass


class UpdateUserDto(BaseRequest, UpdateUserEntity):
    pass
