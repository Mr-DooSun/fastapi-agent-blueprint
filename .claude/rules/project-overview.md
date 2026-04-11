# Project Overview

> Last synced: 2026-04-11 via /sync-guidelines
> For tech stack, refer to project-dna.md §8; for layer structure, refer to §1.
> This file only contains **project-level context** not covered in project-dna.md.

## Purpose
AI Agent Backend Platform built on FastAPI with DDD modular layered architecture

## App Entrypoints
- Server: `src/_apps/server/` — FastAPI (uvicorn)
- Worker: `src/_apps/worker/` — Taskiq (broker abstraction: SQS/RabbitMQ/InMemory)
- Admin: `src/_apps/admin/` — NiceGUI (mounted on server via ui.run_with)

## Dependency Direction
Interface → Application → Domain ← Infrastructure

## Infrastructure Options
- RDB: PostgreSQL, MySQL, SQLite (DATABASE_ENGINE env var)
- DynamoDB: Optional (DYNAMODB_* env vars, BaseDynamoRepository)
- Object Storage: S3/MinIO (S3_*/MINIO_* env vars)
- Message Broker: SQS/RabbitMQ/InMemory (BROKER_TYPE env var)

## Environment Config Validation
- Settings (pydantic-settings) with model_validator
- stg/prod: unsafe defaults blocked, broker required, partial config groups rejected

## Key Value Objects
- QueryFilter: Immutable filter for paginated queries (sort/search). Used in BaseRepository.select_datas_with_count() and BaseService.get_datas().
- DynamoKey: Composite key for DynamoDB (partition_key + optional sort_key). Used in BaseDynamoRepository operations.
