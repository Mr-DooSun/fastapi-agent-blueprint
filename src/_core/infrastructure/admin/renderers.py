from __future__ import annotations

from typing import TYPE_CHECKING

from nicegui import ui

if TYPE_CHECKING:
    from src._core.infrastructure.admin.base_admin_page import BaseAdminPage


async def render_list_page(
    page_config: BaseAdminPage,
    service,
    page: int = 1,
) -> None:
    """Render a paginated AG Grid list view from BaseAdminPage config."""
    dtos, pagination = await service.get_datas(
        page=page, page_size=page_config.page_size
    )

    column_defs = _build_column_defs(page_config)
    masked_fields = page_config.get_masked_field_names()
    row_data = _build_row_data(dtos, masked_fields)

    ui.label(f"{page_config.display_name} Management").classes("text-h5 q-mb-md")

    with ui.row().classes("items-center q-mb-sm"):
        ui.label(
            f"Total: {pagination.total_items} | "
            f"Page {pagination.current_page} / {pagination.total_pages}"
        ).classes("text-caption")

    ui.aggrid(
        {
            "columnDefs": column_defs,
            "rowData": row_data,
            "rowSelection": {"mode": "singleRow"},
            "defaultColDef": {"resizable": True, "filter": True},
        }
    ).classes("w-full").style("height: 600px")

    with ui.row().classes("items-center q-mt-md q-gutter-sm"):
        ui.button(
            "Previous",
            on_click=lambda: ui.navigate.to(
                f"/admin/{page_config.domain_name}?page={pagination.previous_page}"
            ),
        ).props("flat" if pagination.has_previous else "flat disable")
        ui.label(f"{pagination.current_page} / {pagination.total_pages}")
        ui.button(
            "Next",
            on_click=lambda: ui.navigate.to(
                f"/admin/{page_config.domain_name}?page={pagination.next_page}"
            ),
        ).props("flat" if pagination.has_next else "flat disable")


def _build_column_defs(page_config: BaseAdminPage) -> list[dict]:
    """Build AG Grid column definitions from page config."""
    column_defs = []
    for col in page_config.get_visible_columns():
        col_def: dict = {
            "headerName": col.header_name,
            "field": col.field_name,
            "sortable": col.sortable,
        }
        if col.width:
            col_def["width"] = col.width
        if col.masked:
            col_def["valueFormatter"] = "value ? '****' : ''"
        column_defs.append(col_def)
    return column_defs


def _build_row_data(dtos: list, masked_fields: set[str]) -> list[dict]:
    """Build row data from DTOs, masking sensitive fields server-side."""
    rows = []
    for dto in dtos:
        row = dto.model_dump()
        for key, value in row.items():
            if key in masked_fields:
                row[key] = "****" if value else ""
            elif hasattr(value, "isoformat"):
                row[key] = value.isoformat()
        rows.append(row)
    return rows
