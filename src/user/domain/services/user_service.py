from src._core.domain.services.base_service import BaseService
from src.user.domain.entities.user_entity import (
    CreateUserEntity,
    UpdateUserEntity,
    UserEntity,
)
from src.user.infrastructure.repositories.user_repository import UserRepository


class UserService(BaseService[CreateUserEntity, UserEntity, UpdateUserEntity]):
    def __init__(self, user_repository: UserRepository) -> None:
        super().__init__(
            base_repository=user_repository,
            create_entity=CreateUserEntity,
            return_entity=UserEntity,
            update_entity=UpdateUserEntity,
        )
