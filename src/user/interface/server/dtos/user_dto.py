from src._core.application.dtos.base_request import BaseRequest
from src._core.application.dtos.base_response import BaseResponse
from src.user.domain.entities.user_entity import (
    CreateUserEntity,
    UpdateUserEntity,
    UserEntity,
)


class UserResponse(BaseResponse, UserEntity):
    pass


class CreateUserRequest(BaseRequest, CreateUserEntity):
    pass


class UpdateUserRequest(BaseRequest, UpdateUserEntity):
    pass
