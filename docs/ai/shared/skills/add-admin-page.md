# Add Admin Page — Detailed Procedure

## Analysis

1. Identify the domain name from arguments
2. Verify the domain exists: `src/{name}/` present
3. Verify admin files do NOT already exist: `src/{name}/interface/admin/configs/{name}_admin_config.py`
4. Read the domain's DTO (`src/{name}/domain/dtos/{name}_dto.py`) to identify available fields
5. Ask the user:
   - Which fields to display (default: all)
   - Which fields to mask (e.g., password, secret, token)
   - Which fields to make searchable
   - Material icon name (default: "list")

## Reference
- `src/user/interface/admin/configs/user_admin_config.py` — config pattern
- `src/user/interface/admin/pages/user_page.py` — page route pattern
- Admin Page Pattern: refer to `docs/ai/shared/project-dna.md` section 11

## Implementation Order

### 1. Create Directory Structure

Create `__init__.py` for each new directory:
- `src/{name}/interface/admin/__init__.py`
- `src/{name}/interface/admin/configs/__init__.py`
- `src/{name}/interface/admin/pages/__init__.py`

> Skip directories that already exist (e.g., `interface/` likely exists).

### 2. Create Admin Config File

`src/{name}/interface/admin/configs/{name}_admin_config.py`

Read the user reference file first, then replicate the pattern:

```python
from src._core.infrastructure.admin.base_admin_page import (
    BaseAdminPage,
    ColumnConfig,
)

{name}_admin_page = BaseAdminPage(
    domain_name="{name}",
    display_name="{Name}",
    icon="{icon}",
    columns=[
        ColumnConfig(field_name="id", header_name="ID", width=80),
        # ... one ColumnConfig per DTO field
        # searchable=True for text fields users will search by
        # masked=True for sensitive fields (password, secret, token)
        # hidden=True for fields not shown in list view
    ],
    searchable_fields=[...],       # field_name list
    sortable_fields=[...],         # field_name list
    default_sort_field="id",
)
```

### 3. Create Page Route File

`src/{name}/interface/admin/pages/{name}_page.py`

Read the user reference file first, then replicate the pattern:

```python
from nicegui import ui

from src._core.infrastructure.admin.auth import require_auth
from src._core.infrastructure.admin.base_admin_page import BaseAdminPage
from src._core.infrastructure.admin.layout import admin_layout
from src.{name}.interface.admin.configs.{name}_admin_config import {name}_admin_page

# Injected by bootstrap_admin() after discovery
page_configs: list[BaseAdminPage] = []


@ui.page("/admin/{name}")
async def {name}_list_page(page: int = 1, search: str = ""):
    if not require_auth():
        return
    admin_layout(page_configs, current_domain="{name}")
    await {name}_admin_page.render_list(page=page, search=search)


@ui.page("/admin/{name}/{record_id}")
async def {name}_detail_page(record_id: int):
    if not require_auth():
        return
    admin_layout(page_configs, current_domain="{name}")
    await {name}_admin_page.render_detail(record_id=record_id)
```

## Core Rules
- Config file contains ONLY the `BaseAdminPage` instance declaration (no routes, no `ui` import)
- Page file contains ONLY `@ui.page` routes (no `BaseAdminPage` instantiation)
- No `@inject`/`Provide` — service is resolved internally via `BaseAdminPage._service_provider`
- `bootstrap_admin()` handles auto-discovery, DI wiring, and `page_configs` injection
- **No manual bootstrap registration needed** — auto-discovery handles everything
- Config variable must be named `{name}_admin_page` (discovery convention)
- DI pattern: see `docs/ai/shared/project-dna.md` §11

## Post-completion Verification
1. Run pre-commit: `pre-commit run --files src/{name}/interface/admin/**/*.py`
2. Verify config import: `python -c "from src.{name}.interface.admin.configs.{name}_admin_config import {name}_admin_page; print('OK')"`
3. Start server and visit `/admin/{name}` to confirm the page loads
