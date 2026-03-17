from src._core.exceptions.base_exception import BaseCustomException


class UserNotFoundException(BaseCustomException):
    def __init__(self, user_id: int) -> None:
        super().__init__(
            status_code=404,
            message=f"User with ID [ {user_id} ] not found",
            error_code="USER_NOT_FOUND",
        )


class UserAlreadyExistsException(BaseCustomException):
    def __init__(self, username: str) -> None:
        super().__init__(
            status_code=409,
            message=f"User with username [ {username} ] already exists",
            error_code="USER_ALREADY_EXISTS",
        )
