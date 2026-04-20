# Suggested Commands

> Last synced: 2026-04-20 via /sync-guidelines
> Purpose: Quick reference for Claude Code when executing shell commands.
> Also referenced when running Skills.
> Makefile targets (`make dev`, `make test`, etc.) are available as shortcuts — see `AGENTS.md` Common Commands.

## Run
```bash
# Zero-config quickstart (SQLite + InMemory broker, no external infra)
make quickstart
make demo            # in a second terminal — runs curl CRUD walkthrough

# FastAPI server (dev — requires PostgreSQL via docker-compose.local.yml)
uvicorn src._apps.server.app:app --reload --host 127.0.0.1 --port 8001
# or
python run_server_local.py --env local

# Taskiq worker
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
- `tests/conftest.py::_override_app_database` (autouse) swaps the running app's `CoreContainer.database` to `test_db`, so e2e tests do not need real PostgreSQL
- `app.state.container` exposes the wired `DynamicContainer` for fixture overrides

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
uv sync
```

## Architecture Diagrams
```bash
# Regenerate SVG exports under docs/assets/architecture/ from the
# Mermaid blocks in docs/ai/shared/architecture-diagrams.md. Required
# whenever that file is edited so CLI/non-Mermaid viewers stay in sync.
make diagrams
```

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
# Auto-mounted on server → http://127.0.0.1:8001/admin
# Login with ADMIN_ID / ADMIN_PASSWORD from .env
```
