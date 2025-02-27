# -*- coding: utf-8 -*-

from src.core.domain.entities.user_entity import (
    CreateUserEntity,
    UpdateUserEntity,
    UserEntity,
)
from src.core.infrastructure.database.database import Database
from src.core.infrastructure.database.models.user_model import UserModel
from src.core.infrastructure.repositories.base_repository import BaseRepository


class UserRepository(BaseRepository):
    def __init__(self, database: Database) -> None:
        super().__init__(database=database)

    @property
    def model(self):
        return UserModel

    @property
    def create_entity(self):
        return CreateUserEntity

    @property
    def return_entity(self):
        return UserEntity

    @property
    def update_entity(self):
        return UpdateUserEntity
