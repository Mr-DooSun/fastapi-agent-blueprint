# -*- coding: utf-8 -*-
from datetime import datetime

from pydantic import Field

from src.core.domain.entities.entity import Entity


class CoreUsersEntity(Entity):
    id: int = Field(..., description="유저 고유 식별자")
    username: str = Field(..., description="유저 아이디")
    full_name: str = Field(..., description="유저 이름")
    email: str = Field(..., description="유저 이메일")
    password: str = Field(..., description="유저 비밀번호")
    created_at: datetime = Field(..., description="유저 생성 시간")
    updated_at: datetime = Field(..., description="유저 수정 시간")


class CoreCreateUsersEntity(Entity):
    username: str = Field(..., description="유저 아이디")
    full_name: str = Field(..., description="유저 이름")
    email: str = Field(..., description="유저 이메일")
    password: str = Field(..., description="유저 비밀번호")


class CoreUpdateUsersEntity(Entity):
    username: str = Field(..., description="유저 아이디")
    full_name: str = Field(..., description="유저 이름")
    email: str = Field(..., description="유저 이메일")
    password: str = Field(..., description="유저 비밀번호")
