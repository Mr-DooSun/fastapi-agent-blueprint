# -*- coding: utf-8 -*-

from src.core.application.dtos.base import BaseRequest
from src.core.domain.entities.user_entity import CreateUserEntity, UpdateUserEntity


class CreateUserRequestDto(BaseRequest, CreateUserEntity):
    pass


class UpdateUserRequestDto(BaseRequest, UpdateUserEntity):
    pass
