# -*- coding: utf-8 -*-
from typing import List, Union

from src.core.application.dtos.user_dto import UserDto
from src.core.application.responses.base import BaseResponse


class UserResponse(BaseResponse):
    data: Union[UserDto, List[UserDto]]
