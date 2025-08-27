# -*- coding: utf-8 -*-

from src.core.application.dtos.base_request import BaseRequest
from src.core.application.dtos.base_response import BaseResponse
from src.user.domain.entities.users_entity import (
    CoreCreateUsersEntity,
    CoreUpdateUsersEntity,
    CoreUsersEntity,
)


class CoreUsersResponse(BaseResponse, CoreUsersEntity):
    pass


class CoreCreateUsersRequest(BaseRequest, CoreCreateUsersEntity):
    pass


class CoreUpdateUsersRequest(BaseRequest, CoreUpdateUsersEntity):
    pass
