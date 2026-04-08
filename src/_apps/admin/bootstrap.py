import importlib

from fastapi import FastAPI
from nicegui import ui

from src._apps.admin.di.container import create_admin_container
from src._apps.admin.pages import (
    dashboard,  # noqa: F401 (registers @ui.page)
    login,  # noqa: F401 (registers @ui.page)
)
from src._core.config import settings
from src._core.infrastructure.admin.base_admin_page import BaseAdminPage
from src._core.infrastructure.discovery import discover_domains


def bootstrap_admin(fastapi_app: FastAPI) -> None:
    """Bootstrap NiceGUI admin dashboard onto the existing FastAPI app."""
    admin_container = create_admin_container()

    # Shared list — domain pages and dashboard both reference this same object.
    # Pages are rendered at request time, so all entries are present by then.
    page_configs: list[BaseAdminPage] = []
    _discover_and_register_pages(page_configs, admin_container)

    dashboard.page_configs = page_configs

    ui.run_with(fastapi_app, storage_secret=settings.admin_storage_secret)


def _discover_and_register_pages(
    page_configs: list[BaseAdminPage], admin_container
) -> None:
    """Auto-discover admin pages: import registers @ui.page routes, then wire DI."""
    for name in discover_domains():
        try:
            module_path = f"src.{name}.interface.admin.pages.{name}_page"
            module = importlib.import_module(module_path)

            page_config = getattr(module, f"{name}_admin_page")
            page_configs.append(page_config)

            # Inject service provider so BaseAdminPage can resolve service internally
            domain_container = getattr(admin_container, f"{name}_container")
            page_config._service_provider = getattr(
                domain_container, f"{name}_service"
            )

            # Module variable injection for navigation (same as dashboard pattern)
            module.page_configs = page_configs
        except (ModuleNotFoundError, AttributeError):
            continue
