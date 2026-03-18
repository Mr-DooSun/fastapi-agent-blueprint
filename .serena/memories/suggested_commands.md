# Suggested Commands

> 용도: Serena/Claude가 쉘 명령을 실행할 때 참조하는 빠른 레퍼런스.
> Skills 실행 시에도 이 명령어 목록을 참조한다.

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

## Verify Imports (architecture rules)
```bash
# Entity import 완전 제거 확인
grep -r "from src._core.domain.entities" src/
# Domain의 Infrastructure import 확인 (없어야 함)
grep -r "from src._core.infrastructure" src/_core/domain/
```
