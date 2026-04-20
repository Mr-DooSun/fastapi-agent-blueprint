# FastAPI Agent Blueprint — Shared Collaboration Rules

This file is the canonical source for project-shared AI collaboration rules.
Tool-specific harness files must reference this document instead of duplicating its contents.

## Tool-Specific Harnesses

- `CLAUDE.md` — Claude-specific hooks, plugins, slash skills, and tool usage guidance
- `.codex/config.toml` — Codex CLI project settings, profiles, feature flags, and MCP configuration
- `.codex/hooks.json` — Codex command-hook configuration
- `.agents/skills/` — repo-local Codex workflow skills
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

## Optional Infrastructure

Every non-DB infra in `CoreContainer` is optional — toggle via env vars, no code change. When a group is disabled, the provider returns a stub (where graceful degradation matters) or `None` (for data stores). Background: [ADR 042](docs/history/042-optional-infrastructure-di-pattern.md).

| Infra | Enable flag | Disabled behavior |
|---|---|---|
| Storage (S3 / MinIO) | `STORAGE_TYPE=s3` or `minio` | `storage_client()` / `storage()` return `None` |
| DynamoDB | `DYNAMODB_ACCESS_KEY` set | `dynamodb_client()` returns `None` |
| S3 Vectors | `S3VECTORS_ACCESS_KEY` set | `s3vector_client()` returns `None` |
| Embedding | `EMBEDDING_PROVIDER` + `EMBEDDING_MODEL` both set | `embedding_client()` returns `StubEmbedder` (keyword bag-of-words) |
| LLM | `LLM_PROVIDER` + `LLM_MODEL` both set | `llm_model()` returns PydanticAI `TestModel` via `build_stub_llm_model` when `pydantic-ai` is installed, `None` otherwise |
| Broker | `BROKER_TYPE=sqs` / `rabbitmq` / `inmemory` | Defaults to `inmemory` — no external broker required |

**Consumer rule:** data-store clients (`None`-returning) require an explicit guard at the call site when your domain needs them; stub-returning infras just work (but signal "stub" via startup warning logs). Use `providers.Selector` in your domain container to branch between real and stub paths if needed — `src/docs/infrastructure/di/docs_container.py` is the reference pattern.

**Package-level extras:** optional runtime infras are also gated at the `pyproject.toml` level. Install only what you need — `uv sync --extra admin` for the NiceGUI dashboard, `--extra aws` for object storage / DynamoDB / S3 Vectors (boto3 + aioboto3 + type stubs), `--extra sqs` / `--extra rabbitmq` for those broker backends, `--extra pydantic-ai` for LLM / Embedding, etc. When an extra is absent, the matching bootstrap path silently skips and the server continues to boot — the 4 AWS client modules (`ObjectStorageClient`, `ObjectStorage`, `DynamoDBClient`, `S3VectorClient`) import cleanly via `TYPE_CHECKING` + lazy `__init__` imports, and `CoreContainer` resolves the matching Selector to `None` when the env var is unset. `make setup` installs `--extra admin --extra aws` by default for full dev coverage; `make quickstart` only needs `--extra admin` (SQLite + InMemory broker). Every other extra opts in explicitly.

## Terminology

- **Request/Response**: API communication schema (`interface/server/schemas/`)
- **Payload**: Worker message contract schema (`interface/worker/payloads/`) — background: [ADR 016](docs/history/archive/016-worker-payload-schema.md)
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
make quickstart   # zero-config evaluation (SQLite + InMemory broker)
make demo         # curl walkthrough against running quickstart
make dev          # real local dev (PostgreSQL via docker-compose)
make worker
make diagrams     # regenerate SVGs under docs/assets/architecture/
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
- Shared rule sources: `AGENTS.md`, `docs/ai/shared/`, `docs/ai/shared/skills/`, `.claude/`, `.codex/`, and `.agents/`
- Update related documentation in the same change when shared rules or harness behavior changes
  - `README.md`
  - `docs/README.ko.md`
  - `CONTRIBUTING.md`
  - `CLAUDE.md`
  - `docs/ai/shared/` and `docs/ai/shared/skills/`
  - `.claude/rules/` and `.claude/skills/` references when relevant
  - `.codex/hooks.json`, `.codex/rules/`, and `.agents/skills/` when relevant
- When modifying a skill procedure, verify both `.claude/skills/` and `.agents/skills/` wrappers reference the same shared procedure
  - For Hybrid C skills: `docs/ai/shared/skills/{name}.md` is the canonical source for the procedure
  - Claude and Codex wrappers must stay in sync with the shared procedure's Phase/Step structure
- If architecture or shared patterns change, inspect drift before closing the work
  - Claude workflow entry point: `/sync-guidelines`
  - Codex workflow: use `$sync-guidelines` or follow the documented verification steps in `README.md` / `CONTRIBUTING.md`
  - Both tools should run sync after architecture changes — not just the active tool

### Skill Split Convention (Hybrid C)

When extracting shared skill procedures to `docs/ai/shared/skills/`:

**Wrapper keeps** (`.claude/skills/`, `.agents/skills/`):
- Tool-specific frontmatter (name, description, argument-hint, metadata, etc.)
- Phase/Step overview (1-2 line summary per phase — agent sees the full flow before reading external file)
- Tool-specific post-steps (e.g., Claude's `.claude/rules/*` update)
- User interaction flow when it differs between tools

**Shared procedure contains** (`docs/ai/shared/skills/{name}.md`):
- Detailed steps per phase (inspection targets, conditions, branching logic)
- Output format examples
- Checklists, file lists, grep patterns
- Cross-references to other `docs/ai/shared/` documents
