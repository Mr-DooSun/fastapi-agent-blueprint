---
name: add-admin-page
description: Add a NiceGUI admin page for an existing domain while keeping config and page routing separated and masking sensitive fields.
metadata:
  short-description: Add admin page
---

# Add Admin Page

1. Read `AGENTS.md` and `docs/ai/shared/project-dna.md`.
2. Inspect the target domain DTO and the reference admin implementation under `src/user/interface/admin/`.
3. Create or update:
   - `interface/admin/configs/{name}_admin_config.py`
   - `interface/admin/pages/{name}_page.py`
4. Keep `BaseAdminPage` construction in the config file only.
5. Keep `@ui.page` routes in the page file only.
6. Mask fields such as `password`, `secret`, `token`, and `key`.
7. Do not add manual bootstrap registration when auto-discovery already covers it.
