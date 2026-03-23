from src._core.infrastructure.database.base_repository import BaseRepository
from src._core.infrastructure.database.database import Database
from src.user.domain.dtos.user_dto import UserDTO
from src.user.infrastructure.database.models.user_model import UserModel


class UserRepository(BaseRepository[UserDTO]):
    def __init__(self, database: Database) -> None:
        super().__init__(
            database=database,
            model=UserModel,
            return_entity=UserDTO,
        )
