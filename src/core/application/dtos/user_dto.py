# -*- coding: utf-8 -*-

from src.core.application.dtos.base_request import BaseRequest
from src.core.domain.entities.user_entity import (
    CoreCreateUserEntity,
    CoreUpdateUserEntity,
    CoreUserEntity,
)


class CoreUserDto(CoreUserEntity):
    pass


class CoreCreateUserDto(BaseRequest, CoreCreateUserEntity):
    pass


class CoreUpdateUserDto(BaseRequest, CoreUpdateUserEntity):
    pass
