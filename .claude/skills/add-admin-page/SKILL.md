---
name: add-admin-page
argument-hint: domain_name
description: |
  This skill should be used when the user asks to
  "add admin page", "add admin", "admin dashboard",
  or wants to add NiceGUI admin pages to an existing domain.
---

# Add Admin Page to Existing Domain

Domain name: $ARGUMENTS

## Procedure Overview
1. Analysis — verify domain exists, read DTO fields, ask user preferences
2. Implementation — directory structure → admin config → page routes
3. Verification — pre-commit, import check, server start

Read `docs/ai/shared/skills/add-admin-page.md` for detailed steps and code templates.
Also refer to `docs/ai/shared/project-dna.md` §11 for admin page pattern.
