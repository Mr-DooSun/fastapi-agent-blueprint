# Suggested Commands

> Last synced: 2026-04-11 via /sync-guidelines
> Purpose: Quick reference for Claude Code when executing shell commands.
> Also referenced when running Skills.

## Run
```bash
# FastAPI server (dev)
uvicorn src._apps.server.app:app --reload --host 127.0.0.1 --port 8001
# or
python run_server_local.py --env local

# Taskiq worker
python run_worker_local.py --env local
```

## Test
```bash
pytest tests/ -v
pytest tests/unit/ -v
pytest tests/integration/ -v
pytest tests/e2e/ -v
pytest tests/integration/ -v -k "dynamo"   # DynamoDB tests only
```

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

## Admin Dashboard
```bash
# Auto-mounted on server → http://127.0.0.1:8001/admin
# Login with ADMIN_ID / ADMIN_PASSWORD from .env
```
