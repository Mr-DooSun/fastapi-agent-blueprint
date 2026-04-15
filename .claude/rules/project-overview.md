# Project Overview

> Last synced: 2026-04-14 via /sync-guidelines
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
- S3 Vectors: Optional (S3VECTORS_* env vars, BaseS3VectorStore)
- Embedding: Optional (EMBEDDING_PROVIDER env var, OpenAI/Bedrock Selector)
- Message Broker: SQS/RabbitMQ/InMemory (BROKER_TYPE env var)

## Environment Config Validation
- Settings (pydantic-settings) with model_validator
- stg/prod: unsafe defaults blocked, broker required, partial config groups rejected
- Partial config group validation: S3, MinIO, DynamoDB, S3Vectors, SQS, OpenAI, Bedrock

## Key Value Objects
- QueryFilter: Immutable filter for paginated queries (sort/search). Used in BaseRepository.select_datas_with_count() and BaseService.get_datas().
- DynamoKey: Composite key for DynamoDB (partition_key + optional sort_key). Used in BaseDynamoRepository operations.
- VectorQuery: Immutable vector similarity search query (vector, top_k, filters). Used in BaseS3VectorStore.search().
- VectorSearchResult: Vector search result container (items, distances, count). CursorPage counterpart for vector search.
