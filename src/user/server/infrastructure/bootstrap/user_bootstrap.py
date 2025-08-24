# -*- coding: utf-8 -*-
"""User 도메인 독립 Bootstrap"""
from fastapi import FastAPI
from sqladmin import Admin

from src.core.infrastructure.database.database import Database
from src.user.server.admin.views.users_view import UsersView
from src.user.server.application.routers import users_router


def setup_user_routes(app: FastAPI):
    """User 도메인 라우터 등록"""
    app.include_router(router=users_router.router, prefix="/v1", tags=["사용자"])


def setup_user_admin(app: FastAPI, database: Database):
    """User 도메인 관리자 뷰 등록"""
    admin = Admin(app=app, engine=database.engine)
    admin.add_view(UsersView)
    return admin


def bootstrap_user_domain(app: FastAPI, database: Database = None):
    """User 도메인 완전 독립 설정"""
    # 라우터 등록
    setup_user_routes(app)

    # 관리자 페이지 (필요시)
    if database:
        setup_user_admin(app, database)
