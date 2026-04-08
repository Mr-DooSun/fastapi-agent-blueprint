from dependency_injector.wiring import Provide, inject
from nicegui import ui

from src._core.infrastructure.admin.auth import require_auth
from src._core.infrastructure.admin.base_admin_page import (
    BaseAdminPage,
    ColumnConfig,
)
from src._core.infrastructure.admin.layout import admin_layout
from src._core.infrastructure.admin.renderers import (
    render_detail_page,
    render_list_page,
)
from src.user.domain.services.user_service import UserService
from src.user.infrastructure.di.user_container import UserContainer

user_admin_page = BaseAdminPage(
    domain_name="user",
    display_name="User",
    icon="person",
    columns=[
        ColumnConfig(field_name="id", header_name="ID", width=80),
        ColumnConfig(field_name="username", header_name="Username", searchable=True),
        ColumnConfig(field_name="full_name", header_name="Full Name"),
        ColumnConfig(field_name="email", header_name="Email", searchable=True),
        ColumnConfig(field_name="password", header_name="Password", masked=True),
        ColumnConfig(field_name="created_at", header_name="Created At"),
        ColumnConfig(field_name="updated_at", header_name="Updated At"),
    ],
    searchable_fields=["username", "email"],
    sortable_fields=["id", "username", "created_at"],
    default_sort_field="id",
)

# page_configs is injected by bootstrap_admin() after discovery
page_configs: list[BaseAdminPage] = []


@ui.page("/admin/user")
@inject
async def user_list_page(
    page: int = 1,
    search: str = "",
    user_service: UserService = Provide[UserContainer.user_service],
):
    if not require_auth():
        return
    admin_layout(page_configs, current_domain="user")
    await render_list_page(
        page_config=user_admin_page, service=user_service, page=page, search=search
    )


@ui.page("/admin/user/{record_id}")
@inject
async def user_detail_page(
    record_id: int,
    user_service: UserService = Provide[UserContainer.user_service],
):
    if not require_auth():
        return
    admin_layout(page_configs, current_domain="user")
    await render_detail_page(
        page_config=user_admin_page, service=user_service, record_id=record_id
    )
