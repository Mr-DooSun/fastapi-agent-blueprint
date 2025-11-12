from src._core.application.use_cases.base_use_case import BaseUseCase
from src.user.domain.entities.user_entity import (
    CreateUserEntity,
    UpdateUserEntity,
    UserEntity,
)
from src.user.domain.services.user_service import UserService


class UserUseCase(BaseUseCase[CreateUserEntity, UserEntity, UpdateUserEntity]):
    def __init__(self, user_service: UserService) -> None:
        super().__init__(
            base_service=user_service,
            create_entity=CreateUserEntity,
            return_entity=UserEntity,
            update_entity=UpdateUserEntity,
        )

    def process_user(self, entity: UserEntity) -> UserEntity:
        return entity
