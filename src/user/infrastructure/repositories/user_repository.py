from src._core.infrastructure.database.base_repository import BaseRepository
from src._core.infrastructure.database.database import Database
from src.user.domain.entities.user_entity import (
    CreateUserEntity,
    UpdateUserEntity,
    UserEntity,
)
from src.user.infrastructure.database.models.user_model import UserModel


class UserRepository(BaseRepository[CreateUserEntity, UserEntity, UpdateUserEntity]):
    def __init__(self, database: Database) -> None:
        super().__init__(
            database=database,
            model=UserModel,
            create_entity=CreateUserEntity,
            return_entity=UserEntity,
            update_entity=UpdateUserEntity,
        )
