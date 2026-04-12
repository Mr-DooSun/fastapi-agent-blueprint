---
name: add-admin-page
description: Add a NiceGUI admin page for an existing domain while keeping config and page routing separated and masking sensitive fields.
metadata:
  short-description: Add admin page
---

# Add Admin Page

1. Read `AGENTS.md` and `docs/ai/shared/skills/add-admin-page.md` for the full procedure.
2. Read `docs/ai/shared/project-dna.md` §11 for admin page pattern.
3. Inspect the target domain DTO and the reference admin under `src/user/interface/admin/`.
4. Create config file and page route file in separate directories.
5. Keep `BaseAdminPage` in config only; keep `@ui.page` in page only.
6. Mask sensitive fields and do not add manual bootstrap registration.
