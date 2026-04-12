# FastAPI Agent Blueprint — Shared Collaboration Rules

This file is the canonical source for project-shared AI collaboration rules.
Tool-specific harness files must reference this document instead of duplicating its contents.

## Tool-Specific Harnesses

- `CLAUDE.md` — Claude-specific hooks, plugins, slash skills, and tool usage guidance
- `.codex/config.toml` — Codex CLI project settings, profiles, feature flags, and MCP configuration
- `.codex/hooks.json` — Codex command-hook configuration
- `.agents/skills/` — repo-local Codex workflow skills
- `.agents/plugins/` — repo-local Codex plugin marketplace and plugin package
- `docs/ai/shared/` — shared workflow references consumed by both Claude and Codex
- `.mcp.json` — Claude-only MCP server configuration

## Project Scale

This project is an AI Agent Backend Platform targeting enterprise-grade services with 10+ domains and 5+ team members.
All proposals and designs must consider scalability, maintainability, and team collaboration at this scale.

## Absolute Prohibitions

- No Infrastructure imports from the Domain layer
- No exposing Model objects outside the Repository
- No separate Mapper classes (inline conversion is sufficient)
- No Entity pattern — unified to DTO (background: [ADR 004](docs/history/004-dto-entity-responsibility.md))
- No modifying or deleting shared rule sources without cross-reference verification
  - Shared rule sources: `AGENTS.md`, `docs/ai/shared/`, `.claude/`, `.codex/`, and `.agents/`
  - Before changing them, verify no dependent tool configs or skills reference the changed content

Note: Domain → Interface **schema** imports (Request/Response types) are permitted.
When fields match, Request is passed directly to Service — creating a separate DTO is prohibited per ADR 004.

## Layer Architecture (3-Tier Hybrid)

- Default: Router → Service (extends `BaseService`) → Repository (extends `BaseRepository`)
- DynamoDB domain: Router → Service (extends `BaseDynamoService`) → Repository (extends `BaseDynamoRepository`)
- Complex logic: Router → UseCase (manually written) → Service → Repository
- UseCase criteria: multiple Service composition, cross-transaction boundaries, or other orchestration complexity
- When in doubt: start without UseCase, add it when complexity grows

## Terminology

- **Request/Response**: API communication schema (`interface/server/schemas/`)
- **Payload**: Worker message contract schema (`interface/worker/payloads/`) — background: [ADR 016](docs/history/016-worker-payload-schema.md)
- **DTO**: Internal data carrier between layers — Repository → Router (`domain/dtos/`)
- **Model**: DB table mapping, never exposed outside Repository (`infrastructure/database/models/`)
- **DynamoModel**: DynamoDB table mapping, never exposed outside Repository (`infrastructure/dynamodb/models/`)

## Conversion Patterns

### Write Direction (Request → DB)

- Router → Service: `entity=item` (pass Request directly)
- Service → Repository: pass entity as-is, or transform via `entity.model_copy(update={...})` when domain logic requires it
- Repository → DB: `Model(**entity.model_dump(exclude_none=True))`

### Read Direction (DB → Response)

- DB → Repository: `DTO.model_validate(model, from_attributes=True)`
- Repository → Service → Router: pass DTO as-is
- Router → Client: `Response(**dto.model_dump(exclude={"password"}))`

### Worker Direction (Message → Service)

- Message → Task: `Payload.model_validate(kwargs)`
- Task → Service: pass payload as-is when fields match
- Task → Service: `DTO(**payload.model_dump(), extra=...)` when fields differ

## Write DTO Creation Criteria

- When fields match Request: pass Request directly, no separate Create/Update DTO needed
- When fields differ (auth context injection, derived fields, etc.): create a separate DTO in `domain/dtos/`
  - Example: `CreateUserDTO(**item.model_dump(), created_by=current_user.id)`

## Security Principles

- Do not expose internal details (traceback, DB schema, raw query) in production error responses
- Prevent OWASP Top 10 violations when writing code

## Common Commands

### Run

```bash
make dev
make worker
```

### Test

```bash
make test
make test-cov
make check
```

### Lint / Format

```bash
make lint
make format
make pre-commit
```

### Migration

```bash
make migrate
make migration
uv run alembic downgrade -1
uv run alembic current
```

## Drift Management

- `AGENTS.md` is the canonical source for shared rules; tool-specific harness docs must point here instead of re-copying rules
- Keep root `AGENTS.md` short and stable; when local context needs more detail, prefer `AGENTS.override.md` or named skills instead of expanding the root doc
- Codex memories are personal/session optimization only; do not treat them as a shared rule source
- Update related documentation in the same change when shared rules or harness behavior changes
  - `README.md`
  - `docs/README.ko.md`
  - `CONTRIBUTING.md`
  - `CLAUDE.md`
  - `docs/ai/shared/`
  - `.claude/rules/` and `.claude/skills/` references when relevant
  - `.codex/hooks.json`, `.codex/rules/`, `.agents/skills/`, and `.agents/plugins/` when relevant
- If architecture or shared patterns change, inspect drift before closing the work
  - Claude workflow entry point: `/sync-guidelines`
  - Codex workflow: use `$sync-guidelines` or follow the documented verification steps in `README.md` / `CONTRIBUTING.md`
