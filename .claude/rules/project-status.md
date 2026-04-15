# Project Status

> Last synced: 2026-04-14 via /sync-guidelines

## Current Version Context
- Latest release: v0.3.0 (2026-04-10)
- Active domains: user (reference domain)
- Infrastructure: RDB (PostgreSQL/MySQL/SQLite), DynamoDB, S3, S3 Vectors, Embedding, Broker (SQS/RabbitMQ/InMemory)

## Recent Major Changes (since v0.3.0)
| Feature | Issue | Impact |
|---------|-------|--------|
| NiceGUI Admin Dashboard | #14 | New interface layer: admin/ (configs + pages) |
| Environment Config Validation | #53 | Settings model_validator, strict mode for stg/prod |
| Flexible RDB Config | #7 | DatabaseConfig.from_env(), multi-engine support |
| DynamoDB Support | #13 | BaseDynamoRepository, DynamoModel, DynamoDBClient |
| Broker Abstraction | #8 | providers.Selector for SQS/RabbitMQ/InMemory |
| BaseService 3-TypeVar | ADR 011 | Generic[CreateDTO, UpdateDTO, ReturnDTO] restoration |
| Password Hashing | - | hash_password/verify_password in _core.common.security |
| Serena Removal & Pyright Adoption | #63 | pyright-lsp 기본 코드 인텔리전스, PostToolUse 포맷팅 훅, tool-agnostic 스킬 전환 |
| Codex CLI Harness & Hybrid C Skills | #66 | Shared AGENTS.md, docs/ai/shared/ reference layer, 14 Hybrid C skill migrations |
| S3 Vectors Support | #70 | BaseS3VectorStore, S3VectorModel, S3VectorClient, VectorQuery/VectorSearchResult |
| Embedding Service Abstraction | #69 | Selector pattern (OpenAI/Bedrock), BaseEmbeddingProtocol, auto-dimension |
| Text Chunking | #69 | semantic-text-splitter, chunk_text/chunk_text_by_tokens |
| ADR 035/036 | #69 | Embedding abstraction + text chunking design decisions |

## Architecture Violation Status
- Domain → Infrastructure import: CLEAN
- Mapper class: CLEAN
- Entity pattern: CLEAN

## Not Yet Implemented
- JWT/Authentication
- RBAC/Permissions
- File Upload (UploadFile)
- Rate Limiting (slowapi)
- WebSocket
