# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.4.0] - 2026-04-21

### Added

- Zero-config quickstart (`make quickstart` / `make demo` / `ENV=quickstart` with SQLite + InMemory broker + auto create_all) so the blueprint can boot in under 60 seconds with no external infra ([#78](https://github.com/Mr-DooSun/fastapi-agent-blueprint/issues/78))
- End-to-end RAG example as a reusable `_core` pattern (`RagPipeline`, `BaseChunkDTO` / `CitationDTO` / `QueryAnswerDTO`, `AnswerAgentProtocol`, `StubEmbedder` / `StubAnswerAgent` / `PydanticAIAnswerAgent`, `BaseInMemoryVectorStore`) with `src/docs/` consumer domain, `make demo-rag`, and `VECTOR_STORE_TYPE` env var ([#80](https://github.com/Mr-DooSun/fastapi-agent-blueprint/issues/80))
- Optional Infrastructure pattern in CoreContainer — `providers.Selector` + lazy factories for all 5 non-broker optional infras (storage, DynamoDB, S3 Vectors, embedding, LLM); disabled branches return `providers.Object(None)` for data stores or `StubEmbedder` / PydanticAI `TestModel` for AI infras so apps boot with only `DATABASE_ENGINE=sqlite` set and optional extras uninstalled ([#101](https://github.com/Mr-DooSun/fastapi-agent-blueprint/issues/101))
- `build_stub_llm_model()` factory — returns PydanticAI `TestModel` when `pydantic-ai` is installed, `None` otherwise, so `ClassificationService` and future LLM-consuming domains degrade gracefully when `LLM_*` env vars are unset ([#101](https://github.com/Mr-DooSun/fastapi-agent-blueprint/issues/101))
- Structured logging via `structlog` + `asgi-correlation-id` — one `ProcessorFormatter` pipeline bridges structlog-native records and every existing `logging.getLogger(__name__)` call site. Dual renderer (JSON in stg/prod, coloured console in dev), `LOG_LEVEL` / `LOG_JSON_FORMAT` env vars with independent override, per-request `X-Request-ID` correlation bound into `contextvars` and surfaced on every record, `http_request` access-log middleware (method / path / status / duration_ms), Taskiq `StructlogContextMiddleware` binding task IDs + lifting `correlation_id` labels from the dispatcher side, and a `sqlalchemy.engine` double-emit fix that translates `DATABASE_ECHO` into a logger level ([#9](https://github.com/Mr-DooSun/fastapi-agent-blueprint/issues/9))
- AGENTS.md "Optional Infrastructure" reference section and `docs/ai/shared/scaffolding-layers.md` "Optional AI Infra Variant" section for `/new-domain` scaffolding ([#101](https://github.com/Mr-DooSun/fastapi-agent-blueprint/issues/101))
- README restructure (633 → 260 lines), `docs/reference.md`, and `docs/README.ko.md` Korean mirror ([#79](https://github.com/Mr-DooSun/fastapi-agent-blueprint/issues/79))
- Visual architecture diagrams (Mermaid + SVG exports) with canonical `docs/ai/shared/architecture-diagrams.md` and `make diagrams` target ([#81](https://github.com/Mr-DooSun/fastapi-agent-blueprint/issues/81), [#89](https://github.com/Mr-DooSun/fastapi-agent-blueprint/issues/89))
- "Your first domain in 10 minutes" tutorial ([#84](https://github.com/Mr-DooSun/fastapi-agent-blueprint/issues/84))
- Contributor funnel — good-first-issues audit, `examples/` seed, five seed issues for contributors ([#85](https://github.com/Mr-DooSun/fastapi-agent-blueprint/issues/85))
- Secret hygiene — gitleaks pre-commit hook, history scan, `SECURITY.md` expansion ([#87](https://github.com/Mr-DooSun/fastapi-agent-blueprint/issues/87))
- CI `minimal-install` job — runs `uv sync --group dev` alone (no extras) and asserts the app boots, `/api/health` serves, no `/admin` routes are mounted. This is the regression guard for the "extras-uninstall → still boots" promise ([#104](https://github.com/Mr-DooSun/fastapi-agent-blueprint/issues/104))
- ADR 040 (RAG as reusable `_core` pattern), ADR 041 (Multi-backend infrastructure layout — persistence umbrella + vector backend subfolders), ADR 042 (Optional Infrastructure — Selector + lazy factory)

### Changed

- ADR curation — 40 ADRs consolidated down to 14 core + 29 archived under `docs/history/archive/`, with `docs/history/README.md` providing a core-reading-order guide for onboarding ([#83](https://github.com/Mr-DooSun/fastapi-agent-blueprint/issues/83))
- `CoreContainer.llm_config` and `CoreContainer.embedding_config` are no longer public providers — both VOs are now constructed inside the lazy factory functions, reducing the container's surface area without changing the VO classes themselves ([#101](https://github.com/Mr-DooSun/fastapi-agent-blueprint/issues/101))
- `src/_core/infrastructure/` reorganised under the `persistence/` umbrella (RDB at `persistence/rdb/`, DynamoDB at `persistence/nosql/dynamodb/`) with vector backends split into `vectors/s3/` and `vectors/in_memory/` sharing a root `vector_model.py` ([#80](https://github.com/Mr-DooSun/fastapi-agent-blueprint/issues/80), ADR 041)
- RAG DTOs relocated from `_core/domain/value_objects/rag/` to `_core/domain/dtos/rag.py` and renamed `QueryAnswer` → `QueryAnswerDTO` for consistency with the ADR 004 DTO suffix convention ([#80](https://github.com/Mr-DooSun/fastapi-agent-blueprint/issues/80))
- **BREAKING** — `nicegui` moved from core `[project.dependencies]` to a new `[project.optional-dependencies].admin` extra. API-only deployments no longer pay the nicegui install cost; the NiceGUI admin dashboard now requires `uv sync --extra admin`. Contributors running `make setup` / `make quickstart` get the extra automatically. The server bootstrap emits a structured `admin_mount_skipped` record (via the #9 logging pipeline) when nicegui is not installed. This is a SemVer-minor breaking change permitted under the project's `0.x` contract; a deprecation-warning phase was considered but rejected given the small current user base and the cleaner migration story ([#104](https://github.com/Mr-DooSun/fastapi-agent-blueprint/issues/104))
- `Database.__init__` no longer passes `echo=True` to SQLAlchemy's `create_engine` (which would install a parallel `StreamHandler` on `sqlalchemy.engine` and double-emit every query alongside the structlog root handler). `DATABASE_ECHO=true` now translates to `logging.getLogger("sqlalchemy.engine").setLevel(INFO)` — same user-visible semantics, records flow through the structlog pipeline exactly once ([#9](https://github.com/Mr-DooSun/fastapi-agent-blueprint/issues/9))

### Fixed

- `generic_exception_handler` replaced the stray `print(error_trace)` with a structured `logger.exception("unhandled_exception", exc_info=exc, exception_type=...)` — traceback renders inline in both console and JSON modes ([#9](https://github.com/Mr-DooSun/fastapi-agent-blueprint/issues/9))

## [0.3.0] - 2026-04-09

### Added

- NiceGUI admin dashboard with auto-discovery, env-var auth, AG Grid CRUD, and field masking ([#14](https://github.com/Mr-DooSun/fastapi-agent-blueprint/issues/14))
- DynamoDB support with `BaseDynamoRepository`, `DynamoModel`, and `DynamoDBClient` ([#13](https://github.com/Mr-DooSun/fastapi-agent-blueprint/issues/13))
- Broker abstraction with `providers.Selector` for SQS/RabbitMQ/InMemory multi-backend ([#8](https://github.com/Mr-DooSun/fastapi-agent-blueprint/issues/8))
- Flexible RDB configuration with multi-engine and per-environment support ([#7](https://github.com/Mr-DooSun/fastapi-agent-blueprint/issues/7))
- Environment-aware config validation in Settings — strict mode for stg/prod ([#53](https://github.com/Mr-DooSun/fastapi-agent-blueprint/issues/53))
- Password hashing (`hash_password`, `verify_password`) and input validation in `_core.common.security`
- `QueryFilter` value object for paginated query params with sort/search
- DynamoDB Local service in CI for integration tests ([#13](https://github.com/Mr-DooSun/fastapi-agent-blueprint/issues/13))
- Branch name validation in CI for pull requests (`{type}/{description}` format enforcement)
- `/add-admin-page` skill for NiceGUI admin page scaffolding
- ADR 026 (NiceGUI Admin), ADR 027 (Flexible RDB), ADR 028 (Config Validation), ADR 029 (Broker Abstraction)

### Changed

- Replace SQLAdmin with NiceGUI for admin interface ([#14](https://github.com/Mr-DooSun/fastapi-agent-blueprint/issues/14))
- Restore `CreateDTO`/`UpdateDTO` generics to `BaseService` (3 TypeVars) — reverts prior simplification (ADR 011 post-decision update)
- Rename Serena memory `refactoring_status` → `project_status` for clarity ([#60](https://github.com/Mr-DooSun/fastapi-agent-blueprint/issues/60))
- Expand `sync-guidelines` to update all 4 Serena memories (was only 1) ([#60](https://github.com/Mr-DooSun/fastapi-agent-blueprint/issues/60))
- Make `taskiq-aws` an optional dependency with lazy import ([#8](https://github.com/Mr-DooSun/fastapi-agent-blueprint/issues/8))
- Admin views moved from `interface/admin/views/` to `interface/admin/pages/`

### Removed

- `/create-pr` skill — branch name validation moved to CI; PR creation handled by Claude Code built-in capability

### Fixed

- Add missing `__init__.py` in `_core/domain/protocols/` and `_core/domain/value_objects/` ([#60](https://github.com/Mr-DooSun/fastapi-agent-blueprint/issues/60))
- Mount NiceGUI directly on main app instead of sub-app
- Harden admin security with server-side masking and timing-safe auth
- Skip SQS broker test when `taskiq-aws` not installed ([#8](https://github.com/Mr-DooSun/fastapi-agent-blueprint/issues/8))

## [0.2.0] - 2026-04-07

### Added

- Worker Payload Schema: `BasePayload` and `PayloadConfig` for worker message contract validation ([#45](https://github.com/Mr-DooSun/fastapi-agent-blueprint/pull/45))
- Database health check endpoint with `HealthService` ([#19](https://github.com/Mr-DooSun/fastapi-agent-blueprint/pull/19))
- `/create-pr` and `/review-pr` GitHub collaboration skills ([#31](https://github.com/Mr-DooSun/fastapi-agent-blueprint/pull/31))
- Conventional commit message validation hook ([#31](https://github.com/Mr-DooSun/fastapi-agent-blueprint/pull/31))
- `make help` as default Makefile target ([#31](https://github.com/Mr-DooSun/fastapi-agent-blueprint/pull/31))
- 9 missing ADRs (017-025) from full commit history analysis
- ADR 014 (OMC vs Native decision) and ADR 015 (rebranding) and ADR 016 (Worker Payload Schema)

### Changed

- Rebrand project to **AI Agent Backend Platform** (`fastapi-agent-blueprint`) ([#43](https://github.com/Mr-DooSun/fastapi-agent-blueprint/pull/43))
- Rename `interface/dtos/` to `interface/schemas/` for terminology consistency ([#38](https://github.com/Mr-DooSun/fastapi-agent-blueprint/pull/38))
- Unify exception handling with `app.add_exception_handler` ([#35](https://github.com/Mr-DooSun/fastapi-agent-blueprint/pull/35))
- Consolidate sync hook to single git-diff-based Stop hook ([#40](https://github.com/Mr-DooSun/fastapi-agent-blueprint/pull/40))
- Strengthen harness hook security checks and expand detection scope ([#47](https://github.com/Mr-DooSun/fastapi-agent-blueprint/pull/47))
- Extract `HealthService` to follow Router -> Service pattern ([#19](https://github.com/Mr-DooSun/fastapi-agent-blueprint/pull/19))
- Move health check logic into `Database.check_connection()` ([#29](https://github.com/Mr-DooSun/fastapi-agent-blueprint/pull/29))
- Translate all documentation to English (ADRs, skills, references, config, code comments) ([#25](https://github.com/Mr-DooSun/fastapi-agent-blueprint/pull/25))
- Improve ADR template with anti-rationalization principles ([#48](https://github.com/Mr-DooSun/fastapi-agent-blueprint/pull/48))
- Align all 17 existing ADRs with improved template structure ([#48](https://github.com/Mr-DooSun/fastapi-agent-blueprint/pull/48))

### Removed

- Domain Event infrastructure (unused) ([#38](https://github.com/Mr-DooSun/fastapi-agent-blueprint/pull/38))

### Fixed

- Correct `error_code` attribute in `ExceptionMiddleware` ([#26](https://github.com/Mr-DooSun/fastapi-agent-blueprint/pull/26))
- Sync flag file path for sandbox compatibility ([#38](https://github.com/Mr-DooSun/fastapi-agent-blueprint/pull/38))

## [0.1.0] - 2026-03-26

### Added

- Initial project structure with 3-tier hybrid layer architecture
- Domain auto-discovery system (`DynamicContainer` + factory function)
- `BaseService` and `BaseRepository` with generic CRUD operations
- User domain as reference implementation
- Alembic migration support
- Taskiq worker integration with RabbitMQ broker
- SQLAdmin dashboard
- Docker Compose for local development
- GitHub Actions CI workflow
- Ruff for unified linting and formatting
- Claude Code skills: `/new-domain`, `/add-api`, `/add-worker-task`, `/add-cross-domain`, `/review-architecture`, `/security-review`, `/test-domain`, `/fix-bug`, `/onboard`
- ADR documentation (001-013)
- CONTRIBUTING guide and issue templates

[Unreleased]: https://github.com/Mr-DooSun/fastapi-agent-blueprint/compare/v0.3.0...HEAD
[0.3.0]: https://github.com/Mr-DooSun/fastapi-agent-blueprint/compare/v0.2.0...v0.3.0
[0.2.0]: https://github.com/Mr-DooSun/fastapi-agent-blueprint/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/Mr-DooSun/fastapi-agent-blueprint/releases/tag/v0.1.0
