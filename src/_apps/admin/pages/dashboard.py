from nicegui import ui

from src._core.infrastructure.admin import components as c
from src._core.infrastructure.admin.auth import require_auth_allowlisted
from src._core.infrastructure.admin.base_admin_page import BaseAdminPage
from src._core.infrastructure.admin.error_handler import admin_error_boundary
from src._core.infrastructure.admin.layout import admin_layout

# page_configs is injected by bootstrap_admin() after discovery
page_configs: list[BaseAdminPage] = []


@ui.page("/admin/")
@admin_error_boundary(context="admin_dashboard")
async def dashboard_page():
    session = await require_auth_allowlisted()
    if session is None:
        return
    admin_layout(page_configs, current_domain="", session=session)
    c.page_header("Dashboard", subtitle="Welcome to the Admin Dashboard")

    permissions = set(session.permissions)
    visible_configs = [pc for pc in page_configs if pc.domain_name in permissions]

    def _nav_card(icon: str, label: str, target: str) -> None:
        with c.card(clickable_to=target):
            with ui.row().classes("items-center q-pa-sm"):
                ui.icon(icon).classes("text-h4 text-primary")
                ui.label(label).classes("text-h6")

    with ui.row().classes("q-gutter-md"):
        for pc in visible_configs:
            _nav_card(pc.icon, pc.display_name, f"/admin/{pc.domain_name}")
        if "accounts" in permissions:
            _nav_card("manage_accounts", "Accounts", "/admin/accounts")
        if "audit_log" in permissions:
            _nav_card("fact_check", "Audit Log", "/admin/audit-log")
