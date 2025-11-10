from sqladmin import ModelView
from sqlalchemy.orm import class_mapper

from src.user.infrastructure.database.models.user_model import UserModel


class UserView(ModelView, model=UserModel):  # type: ignore[call-arg]
    category = "유저"
    name = "유저 목록"
    column_list = [attr.key for attr in class_mapper(UserModel).column_attrs]

    column_labels = {
        UserModel.id: "ID",
        UserModel.username: "이름",
        UserModel.email: "이메일",
        UserModel.password: "비밀번호",
        UserModel.created_at: "가입일",
        UserModel.updated_at: "수정일",
    }

    column_searchable_list = [UserModel.id, UserModel.username, UserModel.email]
    column_sortable_list = [UserModel.id, UserModel.username, UserModel.created_at]
