# Suggested Commands

> Last synced: 2026-04-27 via /sync-guidelines (translated Korean prose to English under Tier 1 Language Policy, #131; no command surface changes)
> Purpose: Quick reference for Claude Code when executing shell commands.
> Also referenced when running Skills.
> Default Flow context: see [`AGENTS.md` § Default Coding Flow](../../AGENTS.md#default-coding-flow). The commands below are consulted by the `implement` and `verify` steps; this file is **not** a primary entry point in the Default Flow.
> Makefile targets (`make dev`, `make test`, etc.) are available as shortcuts — see `AGENTS.md` Common Commands.

## Run
```bash
# Dev environment setup (includes admin + aws extras — #104)
make setup

# Zero-config quickstart (SQLite + InMemory broker, no external infra)
make quickstart
make demo            # in a second terminal — runs curl CRUD walkthrough
make demo-rag        # RAG end-to-end (seed 3 docs → list → query, #80)

# Local development (PostgreSQL via docker-compose.local.yml)
make dev
make worker

# Direct invocation (reference only)
uvicorn src._apps.server.app:app --reload --host 127.0.0.1 --port 8001
python run_server_local.py --env local
python run_worker_local.py --env local
```

## Test
```bash
pytest tests/ -v                          # SQLite in-memory (default, no infra)
pytest tests/unit/ -v
pytest tests/integration/ -v
pytest tests/e2e/ -v
pytest tests/integration/ -v -k "dynamo"  # DynamoDB tests only (requires docker dynamodb-local)

# Run against real PostgreSQL (docker-compose.local.yml postgres service)
make test-pg
# or manually:
TEST_DB_ENGINE=postgresql \
  TEST_DB_USER=postgres TEST_DB_PASSWORD=postgres \
  TEST_DB_HOST=localhost TEST_DB_PORT=5432 TEST_DB_NAME=postgres \
  pytest tests/ -v

# Run DynamoDB integration tests against docker dynamodb-local
make test-dynamo
```

- `tests/conftest.py::test_db` switches engine via `TEST_DB_ENGINE` (default `sqlite`)
- `tests/e2e/conftest.py::_override_app_database` (autouse) swaps the running app's `CoreContainer.database` to `test_db` via `src._apps.server.testing.override_database()`, so e2e tests do not need real PostgreSQL
- `app.state.container` exposes the wired `DynamicContainer` for fixture overrides
- Test DI override public API: `from src._apps.server.testing import override_database, reset_database_override`

## Lint / Format
```bash
# pre-commit (ruff + mypy)
pre-commit run --all-files
```

## DB Migrations
```bash
alembic revision --autogenerate -m "{domain}: {description}"
alembic upgrade head
alembic downgrade -1
alembic current
alembic history
```

## Package Management (uv)
```bash
uv add <package>
uv sync                                          # core only
uv sync --group dev --extra admin --extra aws    # Dev default (same as make setup, #104)
uv sync --extra admin                            # NiceGUI admin dashboard only
uv sync --extra aws                              # S3/MinIO/DynamoDB/S3Vectors
uv sync --extra pydantic-ai --extra aws          # Bedrock LLM/Embedding (includes aioboto3)
```

## Architecture Diagrams
```bash
# Regenerate SVG exports under docs/assets/architecture/ from the
# Mermaid blocks in docs/ai/shared/architecture-diagrams.md. Required
# whenever that file is edited so CLI/non-Mermaid viewers stay in sync.
make diagrams
```

## Logging (structlog, #9)
```bash
# Log level / format tuning — shared by server and worker
LOG_LEVEL=DEBUG make dev
LOG_JSON_FORMAT=true make dev   # Force JSON renderer in dev too (for pipeline inspection)
LOG_JSON_FORMAT=false make dev  # Temporary console renderer in stg/prod for debugging
```

- Default: dev/local/quickstart → console, stg/prod → JSON (`settings.effective_log_json`)
- All new code uses `structlog.stdlib.get_logger(__name__)`
- `DATABASE_ECHO=true` is mapped to `logging.getLogger("sqlalchemy.engine").setLevel(INFO)` so the structlog pipeline emits each query exactly once

## Architecture Verification
```bash
# Verify no Domain → Infrastructure imports (should return nothing)
grep -r "from src._core.infrastructure" src/_core/domain/
grep -r "from src.*.infrastructure" src/*/domain/ --include="*.py"

# Verify no Entity pattern remnants (should return nothing)
grep -r "class.*Entity" src/ --include="*.py"

# Verify no Mapper classes (should return nothing)
grep -r "class.*Mapper" src/ --include="*.py"
```

## DynamoDB Local
```bash
# Start DynamoDB Local container
docker run -d -p 8000:8000 amazon/dynamodb-local

# Run DynamoDB integration tests
pytest tests/integration/ -v -k "dynamo"
```

## Broker
```bash
# InMemory (default, no setup needed)
BROKER_TYPE=inmemory python run_worker_local.py --env local

# RabbitMQ
BROKER_TYPE=rabbitmq RABBITMQ_URL=amqp://guest:guest@localhost:5672/ python run_worker_local.py --env local
```

## Storage
```bash
# MinIO (local development)
STORAGE_TYPE=minio python run_server_local.py --env local

# AWS S3
STORAGE_TYPE=s3 python run_server_local.py --env local
```

## Admin Dashboard
```bash
# The admin dashboard mounts only when the `admin` extra is installed (#104)
uv sync --extra admin            # install nicegui
# → http://127.0.0.1:8001/admin (ADMIN_ID / ADMIN_PASSWORD from .env)

# When not installed, the server boots normally and emits a structured log line:
#   event="admin_mount_skipped" reason="nicegui_not_installed"
#   install_hint="uv sync --extra admin"
```
