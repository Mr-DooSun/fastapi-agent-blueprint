# -*- coding: utf-8 -*-
from src.core.domain.entities.entity import Entity


class UserEntity(Entity):
    username: str
    full_name: str
    email: str
    password: str


class CreateUserEntity(Entity):
    username: str
    full_name: str
    email: str
    password: str


class UpdateUserEntity(Entity):
    username: str
    full_name: str
    email: str
    password: str
