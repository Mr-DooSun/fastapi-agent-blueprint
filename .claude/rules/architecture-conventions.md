# Architecture Conventions

> Last synced: 2026-04-30 via /sync-guidelines (#10 CRUD write validation hooks and repository validation primitives)
> For Absolute Prohibitions, Conversion Patterns, Write DTO criteria, Responsibility Matrix, Error Translation, Optional AI Infra Pattern, Admin Service Contract, and **Default Coding Flow** (process layer, ADR 045), refer to AGENTS.md.
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
  Write: Entity → VectorStore(BaseS3VectorStore) → VectorModel → S3 Vectors API
  Read:  VectorSearchResult[DTO] ← VectorStore ← DTO ← S3 Vectors API response
```
Key differences from RDB/DynamoDB:
- String keys (UUID v4 hex) via `generate_vector_id`
- Similarity search via VectorQuery (top_k, filters) → VectorSearchResult
- Subclass must implement `_to_model()` for domain-specific DTO → VectorModel conversion
- `VectorModelMeta.dimension` auto-derived from `settings.embedding_dimension`

## BaseService Generic Structure
- `BaseService(Generic[CreateDTO, UpdateDTO, ReturnDTO])` — 3 TypeVars (ADR 011 update, 2026-04-09)
- `BaseRepositoryProtocol(Protocol, Generic[ReturnDTO])` / `BaseRepository(Generic[ReturnDTO])` — 1 TypeVar plus read primitives for Service-owned validation
- `BaseDynamoService(Generic[CreateDTO, UpdateDTO, ReturnDTO])` — mirrors BaseService
- `BaseDynamoRepositoryProtocol(Generic[ReturnDTO])` / `BaseDynamoRepository(Generic[ReturnDTO])` — mirrors BaseRepository
- `BaseVectorStoreProtocol(Generic[ReturnDTO])` / `BaseS3VectorStore(Generic[ReturnDTO])` — vector store pattern
- Domain Service example: `UserService(BaseService[CreateUserRequest, UpdateUserRequest, UserDTO])`
- DO NOT simplify back to 1 TypeVar — this was tried and reverted (see ADR 011 Post-decision Update)
- Service-owned CRUD write validation hooks are canonical in `AGENTS.md` § CRUD Write Validation; keep rule details there.

## Broker Selection
- providers.Selector in CoreContainer: SQS/RabbitMQ/InMemory by BROKER_TYPE env var
- Task code: `from src._apps.worker.broker import broker` — no conditional logic
- stg/prod require explicit BROKER_TYPE setting

## Storage Selection
- Parameter switching in CoreContainer: S3/MinIO by STORAGE_TYPE env var
- Both use the same `ObjectStorageClient` class — only constructor parameters differ
- S3: `region_name`, MinIO: `endpoint_url` + dummy `region_name="us-east-1"`
- No `providers.Selector` needed (same class, different params — contrast with Broker)
- Settings computed properties (`storage_access_key`, etc.) resolve to S3/MinIO fields based on STORAGE_TYPE

## Embedding (PydanticAI Adapter)
- Single `PydanticAIEmbeddingAdapter` replaces per-provider clients (ADR 039)
- No provider-level Selector — PydanticAI handles provider abstraction internally via `model_name` prefix
- `CoreContainer.embedding_client` wraps the adapter in `providers.Selector`: enabled → real adapter; disabled → `StubEmbedder` for graceful degradation (ADR 042)
- `EmbeddingConfig` (frozen dataclass VO) is constructed inside the lazy factory — not a standalone container provider
- Implements `BaseEmbeddingProtocol` (embed_text, embed_batch, dimension)
- Dimension auto-derived from model name — `settings.embedding_dimension` is single source of truth

## LLM (PydanticAI Agent)
- `build_llm_model()` factory returns PydanticAI Model object from `LLMConfig`
- `CoreContainer.llm_model` wraps the factory in `providers.Selector`: enabled → real model; disabled → PydanticAI `TestModel` via `build_stub_llm_model` (or `None` when the `pydantic-ai` extra is uninstalled) (ADR 042)
- `LLMConfig` (frozen dataclass VO) is constructed inside the lazy factory — not a standalone container provider
- Domain services inject the Selector-resolved `llm_model` and create `Agent(model=llm_model)` at init; stub propagates transparently
- Supports OpenAI, Anthropic, Bedrock providers via `model_name` prefix
- Agents are reusable across requests (create once at service init)

## Structured Logging (#9)

- Pipeline: `structlog` ProcessorFormatter + `asgi-correlation-id`. JSON (stg/prod) / console (dev/local/quickstart) renderer auto-selected via `settings.effective_log_json`.
- Server: `configure_logging()` → `TrustedHost → CORS → RequestLogMiddleware → CorrelationIdMiddleware`. Starlette wraps later-added middlewares around earlier ones, so `CorrelationIdMiddleware` is added last on purpose to sit outermost on the request.
- Worker: `configure_logging()` → `app.add_middlewares(StructlogContextMiddleware())` binds task id / correlation id into contextvars; values passed through `with_labels(correlation_id=...)` on the dispatcher are lifted automatically.
- Logger acquisition rule: all application code uses `structlog.stdlib.get_logger(__name__)`.
  - Existing `logging.getLogger(__name__)` callers still flow through the ProcessorFormatter bridge, but new code unifies on the structlog API.
- No sensitive-field logging: fields excluded from Response via `model_dump(exclude={...})` (e.g. `password`, `token`, `access_key`, `secret_key`) must not appear in `logger.info(event, password=...)` / `logger.bind(...)` calls either.
- SQLAlchemy echo: `DATABASE_ECHO=true` is mapped to `logging.getLogger("sqlalchemy.engine").setLevel(INFO)`. The engine handler is registered exactly once so the same query is not double-emitted by stdlib and structlog simultaneously.
- Env vars: `LOG_LEVEL` (DEBUG/INFO/WARNING/ERROR), `LOG_JSON_FORMAT` (None/True/False — `None` derives the renderer from ENV automatically).

## Object Roles

### DTO (Domain DTO)
- Location: `src/{domain}/domain/dtos/{domain}_dto.py`
- Role: Carries read results from Repository → Service → Router (full data)
- **Read-only, single type**: `{Name}DTO` — may include sensitive fields (password, etc.)
- Create/Update DTO is only created separately when fields differ from Request

### Value Object vs DTO — decision rule
- **VO (`src/_core/domain/value_objects/`)**: frozen, value-equal, self-validating. Represents a domain concept whose identity IS its fields (e.g. `VectorQuery`, `EmbeddingConfig`, `LLMConfig`, `DynamoKey`, `QueryFilter`).
  - Prefer `@dataclass(frozen=True)` for config-only VOs (no runtime validation needed).
  - Use `ValueObject(BaseModel, frozen=True)` base when Pydantic validators are required.
- **Shared DTO (`src/_core/domain/dtos/`)**: transfer/carrier across layers. Not frozen. Mutable transients allowed (e.g. `RagPipeline` attaches `_distance` on `BaseChunkDTO`). Read-result containers that are intrinsically values AND never mutated (e.g. `CursorPage`, `VectorSearchResult`) stay in `value_objects/` as frozen VOs.
- **Rule of thumb**: "Can I hand this to another layer and expect it to never change downstream?" — yes → VO (frozen). no → DTO.
- Suffix `DTO` on class names signals carrier role (ADR 004). VOs keep their domain name without suffix.

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

### VectorModel
- Location: `src/{domain}/infrastructure/vectors/models/{domain}_model.py`
- Uses `VectorModelMeta` + `__vector_meta__` for index schema declaration
- Must never leave the VectorStore layer (same rule as ORM Model/DynamoModel)
- Conversion: `Entity → Model: _to_model()` (abstract, subclass implements)
- Conversion: `API response → DTO: return_entity.model_validate(metadata)`

### Admin Page Config (BaseAdminPage)
- Config: `src/{domain}/interface/admin/configs/{domain}_admin_config.py`
- Page: `src/{domain}/interface/admin/pages/{domain}_page.py`
- Config-only declaration (no ui import); route handlers in separate page file
- DI: _service_provider internal resolve (no @inject/Provide)
