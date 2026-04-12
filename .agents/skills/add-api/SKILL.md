---
name: add-api
description: Add an API endpoint to an existing domain using the repository's bottom-up layering, DTO rules, and router conventions.
metadata:
  short-description: Add API endpoint
---

# Add API

1. Read `AGENTS.md` and `docs/ai/shared/skills/add-api.md` for the full procedure.
2. Read `docs/ai/shared/project-dna.md` for conversion patterns and router conventions.
3. Inspect the target domain's Router, Service, Repository, and optional UseCase.
4. Work bottom-up: Repository → Service → UseCase(conditional) → Schema → Router.
5. Reuse BaseService or BaseRepository behavior instead of adding redundant code.
6. Add tests for the new behavior and report how to verify it in Swagger or via tests.
