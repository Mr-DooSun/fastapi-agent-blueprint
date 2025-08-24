# -*- coding: utf-8 -*-
from sqladmin import ModelView
from sqlalchemy.orm import class_mapper

from src.core.infrastructure.database.models.user.users_model import UsersModel


class UsersView(ModelView, model=UsersModel):
    category = "유저"
    name = "유저 목록"
    column_list = [attr.key for attr in class_mapper(UsersModel).column_attrs]

    column_labels = {
        UsersModel.id: "ID",
        UsersModel.username: "이름",
        UsersModel.email: "이메일",
        UsersModel.password: "비밀번호",
        UsersModel.created_at: "가입일",
        UsersModel.updated_at: "수정일",
    }

    column_searchable_list = [UsersModel.id, UsersModel.username, UsersModel.email]
    column_sortable_list = [UsersModel.id, UsersModel.username, UsersModel.created_at]
