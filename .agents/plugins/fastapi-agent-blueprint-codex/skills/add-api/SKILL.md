---
name: add-api
description: Add an API endpoint to an existing domain using the repository's bottom-up layering, DTO rules, and router conventions.
metadata:
  short-description: Add API endpoint
---

# Add API

1. Read `AGENTS.md` and `docs/ai/shared/project-dna.md`.
2. Inspect the target domain's Router, Service, Repository, and optional UseCase.
3. Work bottom-up:
   - Repository only if custom query logic is required
   - Service for domain behavior
   - UseCase only for orchestration complexity
   - Request/Response schemas only when existing ones do not fit
   - Router last
4. Apply the conversion patterns from `AGENTS.md`.
5. Reuse BaseService or BaseRepository behavior instead of adding redundant code.
6. Add tests for the new behavior and report how to verify it in Swagger or via tests.
