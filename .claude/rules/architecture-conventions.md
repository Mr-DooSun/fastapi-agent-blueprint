# Architecture Conventions

> Last synced: 2026-04-14 via /sync-guidelines
> For Absolute Prohibitions, Conversion Patterns, Write DTO criteria, and common commands, refer to AGENTS.md.
> This file only contains **structural context** that supplements AGENTS.md for Claude.

## Data Flow (3-Tier Hybrid)
```
Default (simple CRUD):
  Write: Request → Service(BaseService) → Repository → Model → DB
  Read:  Response ← Service ← Repository ← DTO ← Model

Complex logic:
  Write: Request → UseCase → Service → Repository → Model → DB
  Read:  Response ← UseCase ← Service ← Repository ← DTO ← Model
```
> UseCase is added only when combining multiple Services or crossing transaction boundaries
> For detailed Conversion Patterns: refer to the "Conversion Patterns" section in AGENTS.md

## DynamoDB Data Flow
```
  Write: Request → Service(BaseDynamoService) → Repository(BaseDynamoRepository) → DynamoModel → DynamoDB
  Read:  CursorPage[DTO] ← Service ← Repository ← DTO ← DynamoModel
```
Key differences from RDB:
- Composite keys via DynamoKey(partition_key, sort_key?)
- Cursor-based pagination via CursorPage (not offset-based)
- BaseDynamoService/BaseDynamoRepository — mirrors RDB counterparts

## S3 Vectors Data Flow
```
  Write: Entity → VectorStore(BaseS3VectorStore) → S3VectorModel → S3 Vectors API
  Read:  VectorSearchResult[DTO] ← VectorStore ← DTO ← S3 Vectors API response
```
Key differences from RDB/DynamoDB:
- String keys (UUID v4 hex) via `generate_vector_id`
- Similarity search via VectorQuery (top_k, filters) → VectorSearchResult
- Subclass must implement `_to_model()` for domain-specific DTO → S3VectorModel conversion
- `S3VectorModelMeta.dimension` auto-derived from `settings.embedding_dimension`

## BaseService Generic Structure
- `BaseService(Generic[CreateDTO, UpdateDTO, ReturnDTO])` — 3 TypeVars (ADR 011 update, 2026-04-09)
- `BaseRepositoryProtocol(Generic[ReturnDTO])` / `BaseRepository(Generic[ReturnDTO])` — 1 TypeVar (Repository only calls model_dump, no field-specific access)
- `BaseDynamoService(Generic[CreateDTO, UpdateDTO, ReturnDTO])` — mirrors BaseService
- `BaseDynamoRepositoryProtocol(Generic[ReturnDTO])` / `BaseDynamoRepository(Generic[ReturnDTO])` — mirrors BaseRepository
- `BaseVectorStoreProtocol(Generic[ReturnDTO])` / `BaseS3VectorStore(Generic[ReturnDTO])` — vector store pattern
- Domain Service example: `UserService(BaseService[CreateUserRequest, UpdateUserRequest, UserDTO])`
- DO NOT simplify back to 1 TypeVar — this was tried and reverted (see ADR 011 Post-decision Update)

## Broker Selection
- providers.Selector in CoreContainer: SQS/RabbitMQ/InMemory by BROKER_TYPE env var
- Task code: `from src._apps.worker.broker import broker` — no conditional logic
- stg/prod require explicit BROKER_TYPE setting

## Embedding Selection
- providers.Selector in CoreContainer: OpenAI/Bedrock by EMBEDDING_PROVIDER env var
- Both implement BaseEmbeddingProtocol (embed_text, embed_batch, dimension)
- Dimension auto-derived from model name — `settings.embedding_dimension` is single source of truth

## Object Roles

### DTO (Domain DTO)
- Location: `src/{domain}/domain/dtos/{domain}_dto.py`
- Role: Carries read results from Repository → Service → Router (full data)
- **Read-only, single type**: `{Name}DTO` — may include sensitive fields (password, etc.)
- Create/Update DTO is only created separately when fields differ from Request

### API Schema (Interface DTO)
- Location: `src/{domain}/interface/server/schemas/{domain}_schema.py`
- Inherits `BaseRequest` / `BaseResponse`
- Explicit field declarations
- Intentionally excludes sensitive fields (Response)
- When fields are identical, Request also serves as the layer DTO

### Model (SQLAlchemy ORM)
- Location: `src/{domain}/infrastructure/database/models/{domain}_model.py`
- Must never leave the Repository layer
- Conversion: `DTO → Model: Model(**dto.model_dump())`
- Conversion: `Model → DTO: DTO.model_validate(model, from_attributes=True)`

### DynamoModel
- Location: `src/{domain}/infrastructure/dynamodb/models/{domain}_model.py`
- Uses `DynamoModelMeta` + `__dynamo_meta__` for table schema declaration
- Must never leave the Repository layer (same rule as ORM Model)

### S3VectorModel
- Location: `src/{domain}/infrastructure/s3vectors/models/{domain}_model.py`
- Uses `S3VectorModelMeta` + `__s3vector_meta__` for index schema declaration
- Must never leave the VectorStore layer (same rule as ORM Model/DynamoModel)
- Conversion: `Entity → Model: _to_model()` (abstract, subclass implements)
- Conversion: `API response → DTO: return_entity.model_validate(metadata)`

### Admin Page Config (BaseAdminPage)
- Config: `src/{domain}/interface/admin/configs/{domain}_admin_config.py`
- Page: `src/{domain}/interface/admin/pages/{domain}_page.py`
- Config-only declaration (no ui import); route handlers in separate page file
- DI: _service_provider internal resolve (no @inject/Provide)
