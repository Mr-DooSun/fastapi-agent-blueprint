# -*- coding: utf-8 -*-

from src.core.infrastructure.database.database import Database
from src.core.infrastructure.database.models.user.users_model import UsersModel
from src.core.infrastructure.repositories.base_repository import BaseRepository
from src.user.domain.entities.users_entity import (
    CoreCreateUsersEntity,
    CoreUpdateUsersEntity,
    CoreUsersEntity,
)


class UsersRepository(
    BaseRepository[CoreCreateUsersEntity, CoreUsersEntity, CoreUpdateUsersEntity]
):
    def __init__(self, database: Database) -> None:
        super().__init__(
            database=database,
            model=UsersModel,
            create_entity=CoreCreateUsersEntity,
            return_entity=CoreUsersEntity,
            update_entity=CoreUpdateUsersEntity,
        )
