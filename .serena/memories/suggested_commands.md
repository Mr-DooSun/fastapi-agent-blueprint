# Suggested Commands

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
```

## Lint / Format
```bash
# pre-commit (ruff + mypy)
pre-commit run --all-files
```

## DB Migrations
```bash
alembic revision --autogenerate -m "message"
alembic upgrade head
```

## Package Management (uv)
```bash
uv add <package>
uv sync
```

## Verify Imports (architecture rules)
```bash
# Entity import 완전 제거 확인
grep -r "from src._core.domain.entities" src/
# Domain의 Infrastructure import 확인 (없어야 함)
grep -r "from src._core.infrastructure" src/_core/domain/
```
