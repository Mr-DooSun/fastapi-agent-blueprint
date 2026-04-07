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
    dtos = await service.get_datas()

    column_defs = _build_column_defs(page_config)
    row_data = _build_row_data(dtos, page_config)

    ui.label(f"{page_config.display_name} Management").classes("text-h5 q-mb-md")

    ui.aggrid(
        {
            "columnDefs": column_defs,
            "rowData": row_data,
            "rowSelection": {"mode": "singleRow"},
            "defaultColDef": {"resizable": True, "filter": True},
            "pagination": True,
            "paginationPageSize": page_config.page_size,
        }
    ).classes("w-full").style("height: 600px")


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


def _build_row_data(dtos: list, page_config: BaseAdminPage) -> list[dict]:
    """Build row data from DTOs, converting datetime fields to strings."""
    rows = []
    for dto in dtos:
        row = dto.model_dump()
        for key, value in row.items():
            if hasattr(value, "isoformat"):
                row[key] = value.isoformat()
        rows.append(row)
    return rows
