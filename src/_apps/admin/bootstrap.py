import importlib

from fastapi import FastAPI
from nicegui import ui

from src._apps.admin.di.container import create_admin_container
from src._core.config import settings
from src._core.infrastructure.admin.auth import AdminAuthProvider, require_auth
from src._core.infrastructure.admin.base_admin_page import BaseAdminPage
from src._core.infrastructure.admin.layout import admin_layout
from src._core.infrastructure.admin.renderers import render_list_page
from src._core.infrastructure.discovery import discover_domains


def bootstrap_admin(fastapi_app: FastAPI) -> None:
    """Bootstrap NiceGUI admin dashboard onto the existing FastAPI app."""
    admin_container = create_admin_container()
    page_configs = _discover_admin_pages()

    _register_login_page()
    _register_dashboard_page(page_configs)

    for page_config in page_configs:
        _register_domain_page(page_config, page_configs, admin_container)

    ui.run_with(fastapi_app, storage_secret=settings.admin_storage_secret)


def _discover_admin_pages() -> list[BaseAdminPage]:
    """Auto-discover admin page configs from all domains."""
    pages: list[BaseAdminPage] = []
    for name in discover_domains():
        try:
            module_path = f"src.{name}.interface.admin.pages.{name}_page"
            module = importlib.import_module(module_path)
            page_config = getattr(module, f"{name}_admin_page")
            pages.append(page_config)
        except (ModuleNotFoundError, AttributeError):
            continue
    return pages


def _register_login_page() -> None:
    @ui.page("/admin/login")
    def login_page():
        with ui.card().classes("absolute-center w-80"):
            ui.label("Admin Login").classes("text-h5 q-mb-md")
            username = ui.input("Username").classes("full-width")
            password = ui.input(
                "Password", password=True, password_toggle_button=True
            ).classes("full-width")

            async def try_login():
                if AdminAuthProvider.authenticate(username.value, password.value):
                    AdminAuthProvider.login(username.value)
                    ui.navigate.to("/admin/")
                else:
                    ui.notify("Invalid credentials", type="negative")

            password.on("keydown.enter", try_login)
            ui.button("Login", on_click=try_login).classes("q-mt-md full-width")


def _register_dashboard_page(page_configs: list[BaseAdminPage]) -> None:
    @ui.page("/admin/")
    async def dashboard_page():
        if not require_auth():
            return
        admin_layout(page_configs, current_domain="")
        ui.label("Dashboard").classes("text-h4 q-mb-lg")
        ui.label("Welcome to the Admin Dashboard").classes("text-subtitle1 q-mb-lg")

        with ui.row().classes("q-gutter-md"):
            for pc in page_configs:
                with (
                    ui.card()
                    .classes("cursor-pointer")
                    .on(
                        "click",
                        lambda p=pc: ui.navigate.to(f"/admin/{p.domain_name}"),
                    )
                ):
                    with ui.row().classes("items-center q-pa-sm"):
                        ui.icon(pc.icon).classes("text-h4 text-blue-800")
                        ui.label(pc.display_name).classes("text-h6")


def _register_domain_page(
    page_config: BaseAdminPage,
    all_page_configs: list[BaseAdminPage],
    admin_container,
) -> None:
    domain_name = page_config.domain_name

    @ui.page(f"/admin/{domain_name}")
    async def domain_list_page():
        if not require_auth():
            return
        admin_layout(all_page_configs, current_domain=domain_name)

        domain_container = getattr(admin_container, f"{domain_name}_container")
        service = getattr(domain_container, f"{domain_name}_service")()

        await render_list_page(page_config=page_config, service=service)
