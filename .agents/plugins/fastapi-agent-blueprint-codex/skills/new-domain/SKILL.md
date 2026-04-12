---
name: new-domain
description: Scaffold a new domain that follows the repository's layered architecture, naming rules, DI pattern, and test layout.
metadata:
  short-description: New domain scaffolding
---

# New Domain

1. Validate the domain name and confirm `src/{name}/` does not already exist.
2. Read `AGENTS.md`, `docs/ai/shared/project-dna.md`, and `docs/ai/shared/scaffolding-layers.md`.
3. Use `src/user/` as the reference implementation.
4. Follow the layer order from `scaffolding-layers.md`:
   - Domain
   - optional Application
   - Infrastructure
   - Interface
   - app wiring expectations
   - tests
5. Preserve the shared prohibitions:
   - no Domain -> Infrastructure imports
   - no Entity pattern
   - no Mapper classes
6. Verify imports, run targeted formatting or tests, and report any assumptions about fields or optional UseCase creation.
