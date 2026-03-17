# Project Overview

## Purpose
FastAPI 기반 레이어드 아키텍처 보일러플레이트. DDD 기반 모듈형 레이어드 아키텍처.

## Tech Stack
- Python 3.12.9+, FastAPI 0.115+, Pydantic 2.10+
- SQLAlchemy 2.0+ (async ORM)
- dependency-injector 4.46+
- Taskiq (async task queue)
- aioboto3 (S3), sqladmin (admin UI)
- uv (package manager)

## 4-Layer Structure (per domain module)
```
Interface Layer    → src/{domain}/interface/server|admin|worker
Application Layer  → src/{domain}/application/use_cases
Domain Layer       → src/{domain}/domain/services, dtos, protocols
Infrastructure     → src/{domain}/infrastructure/database, repositories, di
```

## App Entry Points
- `src/_apps/server/` — FastAPI server
- `src/_apps/worker/` — Taskiq worker
- `src/_apps/admin/` — SQLAdmin

## Dependency Direction
Interface → Application → Domain ← Infrastructure
