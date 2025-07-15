# -*- coding: utf-8 -*-

from src.core.application.dtos.common.base_request import BaseRequest
from src.core.application.dtos.common.base_response import BaseResponse
from src.core.domain.entities.user.users_entity import (
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
