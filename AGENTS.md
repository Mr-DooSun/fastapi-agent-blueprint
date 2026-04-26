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

### Process Governor Reference Documents

Issue #117 introduced a hybrid local process governor. The four documents below, indexed from [ADR 045](docs/history/045-hybrid-harness-target-architecture.md), define how default coding work is routed:

- [`docs/history/045-hybrid-harness-target-architecture.md`](docs/history/045-hybrid-harness-target-architecture.md) — top-level decisions + design-question resolutions
- [`docs/ai/shared/harness-asset-matrix.md`](docs/ai/shared/harness-asset-matrix.md) — living inventory of every harness asset and its bucket (Keep / Replace / Overlay / Drop)
- [`docs/ai/shared/target-operating-model.md`](docs/ai/shared/target-operating-model.md) — the target workflow, exception model, Claude/Codex alignment, and sample-workflow traces
- [`docs/ai/shared/migration-strategy.md`](docs/ai/shared/migration-strategy.md) — phased migration plan, rollback rules, and the asset-move ordering

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

## Default Coding Flow

> Source of truth: [ADR 045](docs/history/045-hybrid-harness-target-architecture.md) + [`docs/ai/shared/target-operating-model.md`](docs/ai/shared/target-operating-model.md). Edit those first, then sync this section via `/sync-guidelines`.

Coding work proceeds through seven steps by default. Mandatory-by-default steps must be either performed or explicitly skipped via an escape token (see below). Other steps are conditional.

```
problem framing → approach options → plan → implement
                → verify → self-review → completion gate
```

Mandatory-by-default for implementation-class work: `framing`, `plan`, `verify`, `self-review`.
Conditionally mandatory (architecture commitment present): `approach options`.
Currently advisory (becomes mandatory in migration Phase 4): `completion gate`.

### Precedence

The Default Coding Flow ranks **below** the following four layers, in this order:

1. Active sandbox / approval policy / explicit user scope (e.g. read-only, review-only)
2. `.codex/rules/*` prefix rules (`forbidden` / `prompt`)
3. Safety hooks (security checks, destructive-command guards)
4. `## Absolute Prohibitions` (this document)

Escape tokens never override any of these four layers; they only reduce process burden inside the Default Coding Flow itself.

### Exception Tokens

A prompt may opt out of mandatory-by-default steps by carrying a leading exception token on its first line. Tokens are recognised after NFKC normalisation, case-insensitive, only as the leading bracketed token followed by whitespace or end-of-line.

| Token (English) | Token (Korean) | Meaning |
|---|---|---|
| `[trivial]` | `[자명]` | Self-evident change (typo, comment, rename); skip framing / approach / plan |
| `[hotfix]` | `[긴급]` | Urgent fix; skip approach options; verify still required |
| `[exploration]` | `[탐색]` | Read-only investigation or spike; nothing produces a commit |

Recognition regex: `^\s*\[(trivial|hotfix|exploration|자명|긴급|탐색)\](?:\s|$)`.

Use of an exception token carries a follow-up obligation: the next commit message must record the rationale (one line is enough).

Auto-escapes (no token required): `changed_files == 0`, doc-only changes, comment-only changes.

### Skill Mapping

Each step routes to one or more skills. The shared procedure for each skill (under [`docs/ai/shared/skills/`](docs/ai/shared/skills/)) carries a "Default Flow Position" section documenting which step(s) the skill participates in, and tool-specific wrappers (`.claude/skills/`, `.agents/skills/`) mirror the same position. See [`target-operating-model.md`](docs/ai/shared/target-operating-model.md) §1 for the canonical mapping.

### Claude / Codex Alignment

This document is canonical. Tool-specific enforcement adapters are defined per migration phase in [`migration-strategy.md`](docs/ai/shared/migration-strategy.md). In particular, Codex enforcement is built around prompt-time routing and changed-file completion checks, not Bash-only `PostToolUse` matchers — skill-body instructions alone are insufficient because Codex does not read a skill until it is invoked.

## Layer Architecture (3-Tier Hybrid)

- Default: Router → Service (extends `BaseService`) → Repository (extends `BaseRepository`)
- DynamoDB domain: Router → Service (extends `BaseDynamoService`) → Repository (extends `BaseDynamoRepository`)
- Complex logic: Router → UseCase (manually written) → Service → Repository
- UseCase criteria: multiple Service composition, cross-transaction boundaries, or other orchestration complexity
- When in doubt: start without UseCase, add it when complexity grows

## Responsibility Matrix

Each concern has exactly one home. Do not duplicate or split these across layers.

| Concern | Location | Rule |
|---------|----------|------|
| Pure business logic | `{domain}/domain/services/` | No SDK imports, no infra |
| Domain contracts (AI) | `{domain}/domain/protocols/` or `_core/domain/protocols/` | `typing.Protocol` + `@runtime_checkable` |
| Provider SDK calls | `_core/infrastructure/{llm,embedding,classifier,rag}/` | PydanticAI, boto3 SDK isolated here |
| Provider SDK exception translation | `_core/infrastructure/llm/error_mapper.py` | ACL — infra only, never domain |
| Provider helpers | `_core/infrastructure/ai/providers.py` | `parse_model_name`, `build_*_provider` |
| DI container, lazy factories | `{domain}/infrastructure/di/{domain}_container.py` | `_build_*` factories belong here |
| Bootstrap orchestration | `_apps/{server,worker}/bootstrap.py` | Private `_configure_*`, `_install_*`, `_setup_*` functions |
| Admin service contract | `_core/domain/protocols/admin_service_protocol.py` | `AdminCrudServiceProtocol` |
| Test DI overrides | `_apps/server/testing.py` | Public `override_database` / `reset_database_override` |

## Error Translation

Provider SDK exceptions (PydanticAI, boto3, openai, anthropic) must be translated to domain LLM exceptions in the **infrastructure layer**, never inside domain services.

- **Domain services**: let exceptions propagate — no `try/except` around provider calls
- **Infrastructure adapters** (e.g. `PydanticAIEmbeddingAdapter`): catch SDK exceptions and call `map_llm_error(exc)` (NoReturn — always raises a domain exception)
- **FastAPI `generic_exception_handler`**: catches all unhandled exceptions, calls `try_map_llm_error(exc)` (returns `Optional`) before falling through to 500
- **ACL module**: `src/_core/infrastructure/llm/error_mapper.py` — the only place that knows provider SDK class names

```
Provider SDK exception
  → propagates through domain service untouched
  → caught by FastAPI generic_exception_handler
  → try_map_llm_error(exc) → LLMException (mapped HTTP status)
  OR → 500 Internal Server Error (unrecognised exception)
```

## Optional AI Infra Pattern

All AI features (LLM classification, RAG answering, embedding) follow the same Protocol + Infra Adapter + Selector pattern. Background: [ADR 040](docs/history/040-rag-as-reusable-pattern.md) + [ADR 042](docs/history/042-optional-infrastructure-di-pattern.md).

**Pattern:**
1. `{domain}/domain/protocols/{feature}_protocol.py` — `typing.Protocol` contract
2. `_core/infrastructure/{feature}/pydantic_ai_{feature}.py` — real adapter (or domain-specific if DTO coupling is tight)
3. `_core/infrastructure/{feature}/stub_{feature}.py` — deterministic stub for quickstart/no-LLM
4. Domain container uses `providers.Selector(real=..., stub=...)` to branch

**Reference implementations:**
- RAG: `AnswerAgentProtocol` → `PydanticAIAnswerAgent` / `StubAnswerAgent` (in `_core/infrastructure/rag/`)
- Classifier: `ClassifierProtocol` → `PydanticAIClassifier` / `StubClassifier` (in `classification/infrastructure/classifier/`)

**Selector selector function convention:** `def _classifier_selector() -> str: return "real" if settings.llm_model_name else "stub"`

## Admin Service Contract

Admin pages consume domain services through `AdminCrudServiceProtocol` (`_core/domain/protocols/admin_service_protocol.py`). Any `BaseService` subclass satisfies this protocol automatically.

- `_service_provider: Callable[[], AdminCrudServiceProtocol]` — main CRUD service, wired by bootstrap
- `extra_services_config: dict[str, str]` — declare additional services by alias → container attr name
- `_get_extra_service(alias: str)` — resolve and call an extra service (e.g. `"query"` → `docs_query_service`)

**Example** (docs domain needing a query service alongside the main CRUD service):
```python
docs_admin_page = BaseAdminPage(
    domain_name="docs",
    extra_services_config={"query": "docs_query_service"},
)
# In page handler:
service = docs_admin_page._get_extra_service("query")
```

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

## Structured Logging

Logging is always-on (unlike Optional Infrastructure) and shared across server + worker. Pipeline: `structlog` ProcessorFormatter + `asgi-correlation-id`. Background: #9.

- **Logger acquisition** — all new code uses `structlog.stdlib.get_logger(__name__)`; legacy `logging.getLogger(__name__)` calls still flow through the same pipeline via the ProcessorFormatter bridge but new modules should not add more.
- **Renderer switching** — `LOG_JSON_FORMAT` env var (None → auto: dev/local/quickstart → console, stg/prod → JSON; True/False force override). Controlled by `settings.effective_log_json`.
- **Sensitive-field logging is prohibited** — `password`, `token`, `access_key`, `secret_key`, `api_key`, and any field that Response `model_dump(exclude={...})` strips must NOT appear in `logger.info(event, password=...)`, `logger.bind(...)`, or `structlog.contextvars.bind_contextvars(...)`. The JSON renderer ships structlog kwargs verbatim to aggregators.
- **SQLAlchemy echo** — `DATABASE_ECHO=true` is translated to `logging.getLogger("sqlalchemy.engine").setLevel(INFO)` (not a separate handler) to avoid double-emit between stdlib and structlog pipelines. Do not enable in stg/prod unless secret filtering is in place — bound query parameters reach the log stream.
- **Bootstrap entrypoints** — server: `configure_logging()` → `RequestLogMiddleware` + `CorrelationIdMiddleware` (Starlette adds late-registered middleware as the outermost layer, so CorrelationId is registered last intentionally). Worker: `configure_logging()` → `StructlogContextMiddleware` binds task id / correlation id into contextvars.
- **Env vars** — `LOG_LEVEL` (DEBUG/INFO/WARNING/ERROR), `LOG_JSON_FORMAT` (None/True/False).

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
