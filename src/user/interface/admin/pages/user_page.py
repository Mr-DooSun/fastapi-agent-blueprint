from nicegui import ui

from src._core.infrastructure.admin.auth import require_auth
from src._core.infrastructure.admin.base_admin_page import (
    BaseAdminPage,
    ColumnConfig,
)
from src._core.infrastructure.admin.layout import admin_layout

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
async def user_list_page(page: int = 1, search: str = ""):
    if not require_auth():
        return
    admin_layout(page_configs, current_domain="user")
    await user_admin_page.render_list(page=page, search=search)


@ui.page("/admin/user/{record_id}")
async def user_detail_page(record_id: int):
    if not require_auth():
        return
    admin_layout(page_configs, current_domain="user")
    await user_admin_page.render_detail(record_id=record_id)
