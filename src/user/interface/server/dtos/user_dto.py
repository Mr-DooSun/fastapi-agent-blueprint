from datetime import datetime

from src._core.application.dtos.base_request import BaseRequest
from src._core.application.dtos.base_response import BaseResponse


class UserResponse(BaseResponse):
    id: int
    username: str
    full_name: str
    email: str
    created_at: datetime
    updated_at: datetime


class CreateUserRequest(BaseRequest):
    username: str
    full_name: str
    email: str
    password: str


class UpdateUserRequest(BaseRequest):
    username: str | None = None
    full_name: str | None = None
    email: str | None = None
    password: str | None = None
