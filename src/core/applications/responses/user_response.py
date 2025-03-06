# -*- coding: utf-8 -*-
from typing import List, Union

from src.core.applications.dtos.user_dto import UserDto
from src.core.applications.responses.base_response import BaseResponse


class UserResponse(BaseResponse):
    data: Union[UserDto, List[UserDto]]
