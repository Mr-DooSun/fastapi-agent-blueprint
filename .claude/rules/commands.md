# Suggested Commands

> Last synced: 2026-04-22 via /sync-guidelines (responsibility-driven refactor, pre-v0.5.0)
> Purpose: Quick reference for Claude Code when executing shell commands.
> Also referenced when running Skills.
> Makefile targets (`make dev`, `make test`, etc.) are available as shortcuts — see `AGENTS.md` Common Commands.

## Run
```bash
# 개발환경 셋업 (admin + aws extras 포함 — #104)
make setup

# Zero-config quickstart (SQLite + InMemory broker, no external infra)
make quickstart
make demo            # in a second terminal — runs curl CRUD walkthrough
make demo-rag        # RAG end-to-end (seed 3 docs → list → query, #80)

# 로컬 개발 (PostgreSQL via docker-compose.local.yml)
make dev
make worker

# 직접 실행 (참고용)
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
uv sync --group dev --extra admin --extra aws    # 개발 기본 (make setup과 동일, #104)
uv sync --extra admin                            # NiceGUI 관리 대시보드만
uv sync --extra aws                              # S3/MinIO/DynamoDB/S3Vectors
uv sync --extra pydantic-ai --extra aws          # Bedrock LLM/Embedding (aioboto3 포함)
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
# 로그 레벨 / 포맷 조정 — server/worker 공통
LOG_LEVEL=DEBUG make dev
LOG_JSON_FORMAT=true make dev   # dev에서도 JSON 렌더러 강제 (파이프라인 확인용)
LOG_JSON_FORMAT=false make dev  # stg/prod에서 일시적으로 console 렌더러로 디버깅
```

- 기본: dev/local/quickstart → console, stg/prod → JSON (`settings.effective_log_json`)
- 모든 신규 코드는 `structlog.stdlib.get_logger(__name__)` 사용
- `DATABASE_ECHO=true`는 `logging.getLogger("sqlalchemy.engine").setLevel(INFO)`로 변환되어 structlog 파이프라인을 한 번만 경유

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
# Admin 대시보드는 `admin` extra가 설치된 경우에만 마운트됨 (#104)
uv sync --extra admin            # nicegui 설치
# → http://127.0.0.1:8001/admin (ADMIN_ID / ADMIN_PASSWORD from .env)

# 미설치 시에는 서버는 정상 boot하고 구조화 로그만 남김:
#   event="admin_mount_skipped" reason="nicegui_not_installed"
#   install_hint="uv sync --extra admin"
```
