# -*- coding: utf-8 -*-
"""User 도메인 독립 Bootstrap"""
from fastapi import FastAPI
from sqladmin import Admin

from src._core.infrastructure.database.database import Database
from src.user.infrastructure.di.user_container import UserContainer
from src.user.interface.admin.views.users_view import UsersView
from src.user.interface.server.routers import users_router


def create_user_container(user_container: UserContainer):
    user_container.wire(packages=["src.user.interface.server.routers"])
    return user_container


def setup_user_routes(app: FastAPI):
    """User 도메인 라우터 등록"""
    app.include_router(router=users_router.router, prefix="/v1", tags=["사용자"])


def setup_user_admin(app: FastAPI, database: Database):
    """User 도메인 관리자 뷰 등록"""
    admin = Admin(app=app, engine=database.engine)
    admin.add_view(UsersView)
    return admin


def bootstrap_user_domain(
    app: FastAPI, database: Database, user_container: UserContainer
):
    user_container = create_user_container(user_container=user_container)
    setup_user_routes(app=app)

    if database:
        setup_user_admin(app=app, database=database)
