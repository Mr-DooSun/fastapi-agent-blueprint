# Project DNA - Shared Pattern Reference Extracted from Code

> Shared canonical reference for both Claude and Codex workflow assets.
> Update this file when shared architecture patterns change, then sync the harness docs that point to it.

> This file is auto-extracted/updated from `src/user/` (reference domain) and `src/_core/` (Base classes)
> when `/sync-guidelines` is run. **Run `/sync-guidelines` instead of editing manually.**
>
> Last updated: 2026-04-14

## Section Index
§0 Project Scale and Design Philosophy |
§1 Directory Structure | §2 Base Class Path | §3 Generic Type Signatures | §4 CRUD Methods
§5 DI Pattern | §6 Conversion Patterns | §7 Security Tools | §8 Active Features
§9 Router Pattern | §10 Exception Pattern | §11 Admin Page Pattern
§12 S3 Vector Store Pattern | §13 Embedding Pattern

---

## §0. Project Scale and Design Philosophy

### Scale
- AI Agent Backend Platform targeting enterprise-grade services with 10+ domains and 5+ team members
- All proposals and designs must consider scalability, maintainability, and team collaboration at this scale

### Enterprise Practice Criteria for Proposals

Skills proactively consider the following perspectives when generating code, making design proposals, or performing reviews:

**Scalability**
- List query APIs always include pagination by default
- Suggest separating into async Worker tasks when large-scale data processing is expected
- Specify joinedload/selectinload for relationship queries that risk N+1 queries

**Team Collaboration**
- Cross-domain dependencies must always be proposed via Protocol-based DIP (direct import proposals are prohibited)
- When modifying shared DTOs, first analyze the impact scope (which domains reference them)
- API signature changes are proposed with backward compatibility by default

**Operations**
- Data mutation (CUD) APIs must verify whether audit trail is needed
- Suggest timeout, retry, and circuit breaker settings when integrating with external APIs
- Error responses must include error_codes at a level that clients can act upon

**Security**
- Sensitive data (PII) must be excluded from Responses and not logged
- Endpoints requiring authentication must be explicitly marked
- Environment-specific settings (secrets, DB URLs) must be managed via environment variables only

---

## §1. Layer Directory Structure

```
src/{name}/
├── __init__.py
├── domain/
│   ├── __init__.py
│   ├── dtos/{name}_dto.py
│   ├── protocols/{name}_repository_protocol.py
│   ├── services/{name}_service.py
│   ├── exceptions/{name}_exceptions.py
│   └── value_objects/                    # (as needed)
├── application/                           # (optional — only for complex logic)
│   ├── __init__.py
│   └── use_cases/{name}_use_case.py
├── infrastructure/
│   ├── __init__.py
│   ├── database/
│   │   ├── __init__.py
│   │   └── models/{name}_model.py
│   ├── repositories/{name}_repository.py
│   └── di/{name}_container.py
└── interface/
    ├── __init__.py
    ├── server/
    │   ├── schemas/{name}_schema.py
    │   ├── routers/{name}_router.py
    │   └── bootstrap/{name}_bootstrap.py
    ├── admin/
    │   ├── configs/{name}_admin_config.py
    │   └── pages/{name}_page.py
    └── worker/
        ├── payloads/{name}_payload.py
        ├── tasks/{name}_test_task.py
        └── bootstrap/{name}_bootstrap.py
```

### DynamoDB Domain Variant

DynamoDB를 사용하는 도메인은 `infrastructure/database/` 대신 `infrastructure/dynamodb/`를 사용:

```
src/{name}/
├── infrastructure/
│   ├── dynamodb/
│   │   └── models/{name}_model.py    # extends DynamoModel
│   ├── repositories/{name}_repository.py  # extends BaseDynamoRepository
│   └── di/{name}_container.py        # dynamodb_client=core_container.dynamodb_client
└── (나머지 동일)
```

## §2. Base Class Import Path

| Class | Import Path |
|---------|------------|
| BaseRepositoryProtocol | `src._core.domain.protocols.repository_protocol.BaseRepositoryProtocol` |
| BaseService | `src._core.domain.services.base_service.BaseService` |
| BaseRepository | `src._core.infrastructure.database.base_repository.BaseRepository` |
| Base (ORM DeclarativeBase) | `src._core.infrastructure.database.database.Base` |
| Database | `src._core.infrastructure.database.database.Database` |
| BaseDynamoRepositoryProtocol | `src._core.domain.protocols.dynamo_repository_protocol.BaseDynamoRepositoryProtocol` |
| BaseDynamoService | `src._core.domain.services.base_dynamo_service.BaseDynamoService` |
| BaseDynamoRepository | `src._core.infrastructure.dynamodb.base_dynamo_repository.BaseDynamoRepository` |
| DynamoModel | `src._core.infrastructure.dynamodb.dynamodb_model.DynamoModel` |
| DynamoModelMeta | `src._core.infrastructure.dynamodb.dynamodb_model.DynamoModelMeta` |
| GSIDefinition | `src._core.infrastructure.dynamodb.dynamodb_model.GSIDefinition` |
| DynamoDBClient | `src._core.infrastructure.dynamodb.dynamodb_client.DynamoDBClient` |
| DynamoKey | `src._core.domain.value_objects.dynamo_key.DynamoKey` |
| SortKeyCondition | `src._core.domain.value_objects.dynamo_key.SortKeyCondition` |
| CursorPage | `src._core.domain.value_objects.cursor_page.CursorPage` |
| CursorPaginationInfo | `src._core.application.dtos.base_response.CursorPaginationInfo` |
| BaseRequest | `src._core.application.dtos.base_request.BaseRequest` |
| BaseResponse | `src._core.application.dtos.base_response.BaseResponse` |
| SuccessResponse | `src._core.application.dtos.base_response.SuccessResponse` |
| ErrorResponse | `src._core.application.dtos.base_response.ErrorResponse` |
| PaginationInfo | `src._core.application.dtos.base_response.PaginationInfo` |
| BasePayload | `src._core.application.dtos.base_payload.BasePayload` |
| PayloadConfig | `src._core.application.dtos.base_config.PayloadConfig` |
| ApiConfig | `src._core.application.dtos.base_config.ApiConfig` |
| BaseCustomException | `src._core.exceptions.base_exception.BaseCustomException` |
| ValueObject | `src._core.domain.value_objects.value_object.ValueObject` |
| QueryFilter | `src._core.domain.value_objects.query_filter.QueryFilter` |
| make_pagination | `src._core.common.pagination.make_pagination` |
| hash_password | `src._core.common.security.hash_password` |
| verify_password | `src._core.common.security.verify_password` |
| BaseVectorStoreProtocol | `src._core.domain.protocols.vector_store_protocol.BaseVectorStoreProtocol` |
| BaseEmbeddingProtocol | `src._core.domain.protocols.embedding_protocol.BaseEmbeddingProtocol` |
| BaseS3VectorStore | `src._core.infrastructure.s3vectors.base_s3vector_store.BaseS3VectorStore` |
| S3VectorModel | `src._core.infrastructure.s3vectors.s3vector_model.S3VectorModel` |
| S3VectorModelMeta | `src._core.infrastructure.s3vectors.s3vector_model.S3VectorModelMeta` |
| S3VectorData | `src._core.infrastructure.s3vectors.s3vector_model.S3VectorData` |
| S3VectorClient | `src._core.infrastructure.s3vectors.s3vector_client.S3VectorClient` |
| VectorQuery | `src._core.domain.value_objects.vector_query.VectorQuery` |
| VectorSearchResult | `src._core.domain.value_objects.vector_search_result.VectorSearchResult` |
| OpenAIEmbeddingClient | `src._core.infrastructure.embedding.openai_embedding_client.OpenAIEmbeddingClient` |
| BedrockEmbeddingClient | `src._core.infrastructure.embedding.bedrock_embedding_client.BedrockEmbeddingClient` |
| chunk_text | `src._core.common.text_utils.chunk_text` |
| chunk_text_by_tokens | `src._core.common.text_utils.chunk_text_by_tokens` |
| generate_vector_id | `src._core.common.uuid_utils.generate_vector_id` |
| CoreContainer | `src._core.infrastructure.di.core_container.CoreContainer` |

### Inheritance Chain

- `BaseRequest` → `ApiConfig` → `BaseModel` (camelCase alias, frozen, populate_by_name)
- `BaseResponse` → `ApiConfig` → `BaseModel`
- `SuccessResponse` → `ApiConfig`, `Generic[ReturnType]`
- `BasePayload` → `PayloadConfig` → `BaseModel` (frozen, extra="forbid", no alias)
- `ValueObject` → `BaseModel` (frozen=True)

## §3. Generic Type Signatures

```python
# BaseRepositoryProtocol / BaseRepository — 1 TypeVar (ReturnDTO only)
# Repository only calls entity.model_dump(), no field-specific access needed
ReturnDTO = TypeVar("ReturnDTO", bound=BaseModel)

class BaseRepositoryProtocol(Generic[ReturnDTO]): ...
class BaseRepository(Generic[ReturnDTO], ABC): ...

# BaseService — 3 TypeVars (CreateDTO, UpdateDTO, ReturnDTO)
# Service overrides access specific fields (e.g., entity.password), so typed inputs are required
# Background: ADR 011 Post-decision Update (2026-04-09)
CreateDTO = TypeVar("CreateDTO", bound=BaseModel)
UpdateDTO = TypeVar("UpdateDTO", bound=BaseModel)

class BaseService(Generic[CreateDTO, UpdateDTO, ReturnDTO]): ...

# SuccessResponse
ReturnType = TypeVar("ReturnType")
class SuccessResponse(ApiConfig, Generic[ReturnType]): ...

# Reference domain (user) usage example:
class UserRepositoryProtocol(BaseRepositoryProtocol[UserDTO]): pass
class UserRepository(BaseRepository[UserDTO]): ...
class UserService(BaseService[CreateUserRequest, UpdateUserRequest, UserDTO]): ...
```

### DynamoDB Generic Type Signatures

```python
# BaseDynamoRepositoryProtocol / BaseDynamoRepository — 1 TypeVar (ReturnDTO only)
class BaseDynamoRepositoryProtocol(Generic[ReturnDTO]): ...
class BaseDynamoRepository(Generic[ReturnDTO], ABC): ...

# BaseDynamoService — 3 TypeVars (CreateDTO, UpdateDTO, ReturnDTO)
class BaseDynamoService(Generic[CreateDTO, UpdateDTO, ReturnDTO]): ...

# DynamoDB domain usage example:
class ChatRoomRepositoryProtocol(BaseDynamoRepositoryProtocol[ChatRoomDTO]): pass
class ChatRoomRepository(BaseDynamoRepository[ChatRoomDTO]): ...
class ChatRoomService(BaseDynamoService[CreateChatRoomRequest, UpdateChatRoomRequest, ChatRoomDTO]): ...
```

### S3 Vector Store Generic Type Signatures

```python
# BaseVectorStoreProtocol / BaseS3VectorStore — 1 TypeVar (ReturnDTO only)
class BaseVectorStoreProtocol(Generic[ReturnDTO]): ...
class BaseS3VectorStore(Generic[ReturnDTO], ABC): ...

# S3 Vector domain usage example:
class DocumentVectorStoreProtocol(BaseVectorStoreProtocol[DocumentDTO]): pass
class DocumentS3VectorStore(BaseS3VectorStore[DocumentDTO]): ...
```

### BaseS3VectorStore.__init__ Signature

```python
def __init__(
    self,
    s3vector_client: S3VectorClient,
    *,
    model: type[S3VectorModel],
    return_entity: type[ReturnDTO],
    bucket_name: str,
) -> None:
```

### BaseRepository.__init__ Signature

```python
def __init__(
    self,
    database: Database,
    *,
    model: type[Base],
    return_entity: type[ReturnDTO],
) -> None:
```

## §4. Base CRUD Methods

### BaseRepositoryProtocol Methods

| Method | Signature |
|--------|---------|
| insert_data | `async (entity: BaseModel) -> ReturnDTO` |
| insert_datas | `async (entities: list[BaseModel]) -> list[ReturnDTO]` |
| select_datas | `async (page: int, page_size: int) -> list[ReturnDTO]` |
| select_data_by_id | `async (data_id: int) -> ReturnDTO` |
| select_datas_by_ids | `async (data_ids: list[int]) -> list[ReturnDTO]` |
| select_datas_with_count | `async (page: int, page_size: int, query_filter: QueryFilter \| None = None) -> tuple[list[ReturnDTO], int]` |
| update_data_by_data_id | `async (data_id: int, entity: BaseModel) -> ReturnDTO` |
| delete_data_by_data_id | `async (data_id: int) -> bool` |
| count_datas | `async () -> int` |

### BaseService Methods (Repository Delegation Mapping)

> `BaseService[CreateDTO, UpdateDTO, ReturnDTO]` provides all methods below.
> Domain Services extend `BaseService[Create{Name}Request, Update{Name}Request, {Name}DTO]` and only override when custom logic is needed.

| BaseService Method | Signature | Repository Call |
|-------------------|-----------|----------------|
| create_data | `(entity: CreateDTO) -> ReturnDTO` | insert_data(entity=entity) |
| create_datas | `(entities: list[CreateDTO]) -> list[ReturnDTO]` | insert_datas(entities=entities) |
| get_datas | `(page, page_size, query_filter) -> (list[ReturnDTO], PaginationInfo)` | select_datas_with_count(...) |
| get_data_by_data_id | `(data_id: int) -> ReturnDTO` | select_data_by_id(data_id=data_id) |
| get_datas_by_data_ids | `(data_ids: list[int]) -> list[ReturnDTO]` | select_datas_by_ids(data_ids=data_ids) |
| update_data_by_data_id | `(data_id: int, entity: UpdateDTO) -> ReturnDTO` | update_data_by_data_id(data_id, entity) |
| delete_data_by_data_id | `(data_id: int) -> bool` | delete_data_by_data_id(data_id=data_id) |
| count_datas | `() -> int` | count_datas() |

### BaseDynamoRepositoryProtocol Methods

| Method | Signature |
|--------|---------|
| put_item | `async (entity: BaseModel) -> ReturnDTO` |
| get_item | `async (key: DynamoKey) -> ReturnDTO` |
| query_items | `async (partition_key_value: str, sort_key_condition?, index_name?, filter_expression?, limit?, cursor?, scan_forward?) -> CursorPage[ReturnDTO]` |
| update_item | `async (key: DynamoKey, entity: BaseModel) -> ReturnDTO` |
| delete_item | `async (key: DynamoKey) -> bool` |

### BaseDynamoService Methods

| Method | Signature | Repository Call |
|--------|-----------|----------------|
| create_item | `(entity: CreateDTO) -> ReturnDTO` | put_item(entity=entity) |
| get_item | `(key: DynamoKey) -> ReturnDTO` | get_item(key=key) |
| query_items | `(partition_key_value, ...) -> CursorPage[ReturnDTO]` | query_items(...) |
| update_item | `(key: DynamoKey, entity: UpdateDTO) -> ReturnDTO` | update_item(key, entity) |
| delete_item | `(key: DynamoKey) -> bool` | delete_item(key=key) |

### DynamoDB DI Pattern

```python
class {Name}Container(containers.DeclarativeContainer):
    core_container = providers.DependenciesContainer()

    {name}_repository = providers.Singleton(
        {Name}Repository,
        dynamodb_client=core_container.dynamodb_client,  # ← DynamoDB
    )

    {name}_service = providers.Factory(
        {Name}Service,
        {name}_repository={name}_repository,
    )
```

## §5. DI Pattern

```python
from dependency_injector import containers, providers

class {Name}Container(containers.DeclarativeContainer):
    core_container = providers.DependenciesContainer()

    {name}_repository = providers.Singleton(
        {Name}Repository,
        database=core_container.database,
    )

    {name}_service = providers.Factory(
        {Name}Service,
        {name}_repository={name}_repository,
    )

    # Add UseCase only when complex business logic is needed
    # {name}_use_case = providers.Factory(
    #     {Name}UseCase,
    #     {name}_service={name}_service,
    # )
```

| Component | Provider Type | Notes |
|---------|--------------|------|
| Database | `providers.Singleton` | |
| Repository | `providers.Singleton` | |
| Service | `providers.Factory` | Direct injection from Router |
| UseCase | `providers.Factory` | Add only for complex logic |
| Domain Container | `containers.DeclarativeContainer` | |
| External Container reference | `providers.DependenciesContainer()` |
| App Container (Server/Worker) | `containers.DynamicContainer` (factory function) |
| Domain auto-discovery | `src._core.infrastructure.discovery.discover_domains()` |
| Dynamic Container loading | `src._core.infrastructure.discovery.load_domain_container()` |
| S3VectorClient | `providers.Singleton` | S3 Vectors API wrapper |
| Embedding (multi-backend) | `providers.Selector` | Selects OpenAI/Bedrock by config |
| Broker (multi-backend) | `providers.Selector` | Selects SQS/RabbitMQ/InMemory by config |

### App-level Container (Auto-discovery)

Domain Containers use `DeclarativeContainer`,
but Server/Worker App-level Containers use `DynamicContainer` + factory functions.
`discover_domains()` automatically detects and registers valid domains under `src/*/`,
so **no App-level container/bootstrap file modifications are needed when adding a new domain.**

```python
# src/_apps/server/di/container.py
from src._core.infrastructure.discovery import discover_domains, load_domain_container

def create_server_container() -> containers.DynamicContainer:
    container = containers.DynamicContainer()
    container.core_container = providers.Container(CoreContainer)
    for domain in discover_domains():
        cls = load_domain_container(domain)
        setattr(container, f"{domain}_container",
                providers.Container(cls, core_container=container.core_container))
    return container
```

### Broker Selection Pattern (Runtime Configuration)

The message broker uses `providers.Selector` to dynamically select between broker backends
based on the `BROKER_TYPE` environment variable:

```python
# src/_core/infrastructure/di/core_container.py
broker = providers.Selector(
    lambda: (settings.broker_type or "inmemory").lower().strip(),
    sqs=providers.Singleton(CustomSQSBroker, queue_url=..., ...),
    rabbitmq=providers.Singleton(create_rabbitmq_broker, url=...),
    inmemory=providers.Singleton(InMemoryBroker),
)
```

| BROKER_TYPE | Broker Class | Dependency |
|-------------|-------------|------------|
| `sqs` | `CustomSQSBroker` | `taskiq-aws` (main) |
| `rabbitmq` | `AioPikaBroker` | `taskiq-aio-pika` (optional) |
| `inmemory` (default) | `InMemoryBroker` | `taskiq` (main) |

- Selector evaluates at container creation time; selected Singleton is cached
- Task code always uses `from src._apps.worker.broker import broker` — no conditional logic needed
- stg/prod environments require explicit `BROKER_TYPE` setting

### Embedding Selection Pattern (Runtime Configuration)

The embedding service uses `providers.Selector` to dynamically select between embedding backends
based on the `EMBEDDING_PROVIDER` environment variable:

```python
# src/_core/infrastructure/di/core_container.py
embedding_client = providers.Selector(
    lambda: (settings.embedding_provider or "openai").lower().strip(),
    openai=providers.Singleton(OpenAIEmbeddingClient, api_key=..., model=...),
    bedrock=providers.Singleton(BedrockEmbeddingClient, access_key=..., ...),
)
```

| EMBEDDING_PROVIDER | Client Class | Dependency |
|-------------------|-------------|------------|
| `openai` (default) | `OpenAIEmbeddingClient` | `openai`, `tiktoken` (optional extra) |
| `bedrock` | `BedrockEmbeddingClient` | `aioboto3` (main) |

- Both implement `BaseEmbeddingProtocol` (embed_text, embed_batch, dimension)
- Dimension is auto-derived from model name — not user-configurable
- `settings.embedding_dimension` is the single source of truth for vector index dimension

### S3 Vector Store DI Pattern

```python
class {Name}Container(containers.DeclarativeContainer):
    core_container = providers.DependenciesContainer()

    {name}_vector_store = providers.Singleton(
        {Name}S3VectorStore,
        s3vector_client=core_container.s3vector_client,
        embedding_client=core_container.embedding_client,
        bucket_name=settings.s3vectors_bucket_name,
    )

    {name}_service = providers.Factory(
        {Name}Service,
        {name}_vector_store={name}_vector_store,
    )
```

### Interface-Specific DI Pattern

| Interface | Outer decorator | Inner decorator | Service default | Wiring |
|-----------|----------------|-----------------|-----------------|--------|
| Server router | `@router.verb(...)` | `@inject` | `Depends(Provide[...])` | `wire(packages=[...routers])` |
| Admin page | `@ui.page(...)` | — | — | `bootstrap` injects `_service_provider` into `BaseAdminPage` |
| Worker task | `@broker.task(...)` | `@inject` | `Provide[...]` | `wire(modules=[...task])` |

- `Depends()` 래퍼는 FastAPI Router 전용 (FastAPI가 파라미터를 query/body로 해석하는 것을 방지)
- Worker는 bare `Provide[...]` 사용 (프레임워크가 자체적으로 DI 파라미터를 해석하지 않음)
- Admin은 `BaseAdminPage._service_provider`에 provider를 주입하여 내부에서 service를 resolve

## §6. Conversion Patterns

| Conversion | Pattern | Example |
|------|------|------|
| ORM → DTO | `ReturnDTO.model_validate(data, from_attributes=True)` | `UserDTO.model_validate(data, from_attributes=True)` |
| Request → Service | Direct pass `entity=item` (when fields match) | `create_data(entity=item)` |
| Request → DTO | `CreateDTO(**item.model_dump(), extra=...)` (when fields differ) | `CreateOrderDTO(**item.model_dump(), user_id=current_user.id)` |
| DTO → Response | `{Name}Response(**data.model_dump(exclude={...}))` | `UserResponse(**data.model_dump(exclude={"password"}))` |
| Message → Payload | `{Name}Payload.model_validate(kwargs)` | `UserTestPayload.model_validate(kwargs)` |
| Payload → Service | Direct pass `entity=payload` (when fields match) | `create_data(entity=payload)` |

## §7. Security Tools

### Pre-commit (Auto-run)

- trailing-whitespace, end-of-file-fixer, check-yaml/json/toml
- check-added-large-files (1MB), check-merge-conflict, debug-statements, mixed-line-ending (LF)
- ruff check --fix (Unified rules for E, W, F, UP, I, B, C4, SIM, S -- replaces pyupgrade, autoflake, isort, flake8, bandit)
- ruff format (Black-compatible formatting)

### Pre-commit (Manual Stage)

- mypy (--ignore-missing-imports, --check-untyped-defs)

### Commit Message

- conventional-pre-commit (feat, fix, refactor, docs, chore, test, ci, perf, style, i18n)

### Architecture Violation Check (Auto-run)

- no-domain-infra-import: No Infrastructure imports from Domain layer
- no-entity-pattern: No Entity pattern -- unified to DTO (background: ADR 004)

### Claude Hook

- SessionStart (check-required-plugins): pyright-lsp 플러그인 설치 확인, CONTEXT7_API_KEY 환경변수 검증
- PreToolUse (pre-tool-security): SQL injection, hardcoded secrets, Domain→Infra import, sensitive data logging check
- PostToolUse (post-tool-format): Edit/Write 후 `.py` 파일 자동 포맷팅 (ruff format + ruff check)
- Stop (stop-sync-reminder): git diff 기반으로 변경 파일을 Foundation/Structure로 분류하여 /sync-guidelines 실행 권고

## §8. Active Features

| Feature | Status | Notes |
|------|------|------|
| Taskiq async tasks | Active | Broker abstraction (SQS/RabbitMQ/InMemory), @broker.task decorator |
| SQLAlchemy 2.0+ | Active | Mapped[T] + mapped_column() |
| Pydantic 2.x | Active | model_validate, model_dump, ConfigDict |
| dependency-injector | Active | DeclarativeContainer, @inject + Provide |
| AWS S3 (aioboto3) | Active | ObjectStorage + ObjectStorageClient |
| AWS DynamoDB (aioboto3) | Active | BaseDynamoRepository + DynamoDBClient (optional infra) |
| NiceGUI (BaseAdminPage) | Active | Admin dashboard (AG Grid, auto-discovery, Template Method rendering) |
| alembic (migrations) | Active | DB migrations |
| Password hashing (bcrypt) | Active | hash_password(), verify_password() in src._core.common.security |
| AWS S3 Vectors (aioboto3) | Active | BaseS3VectorStore + S3VectorClient (optional infra) |
| Embedding (OpenAI/Bedrock) | Active | Selector pattern, BaseEmbeddingProtocol, auto-dimension |
| Text chunking (semantic-text-splitter) | Active | chunk_text(), chunk_text_by_tokens() in src._core.common.text_utils |
| JWT/Authentication | Not implemented | |
| File Upload (UploadFile) | Not implemented | |
| RBAC/Permissions | Not implemented | |
| Rate Limiting (slowapi) | Not implemented | |
| WebSocket | Not implemented | |

## §9. Router Pattern

```python
from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, Query
from src._core.application.dtos.base_response import SuccessResponse

router = APIRouter()

@router.post(
    "/{name}",
    summary="...",
    response_model=SuccessResponse[{Name}Response],
    response_model_exclude={"pagination"},
)
@inject
async def create_{name}(
    item: Create{Name}Request,
    {name}_service: {Name}Service = Depends(Provide[{Name}Container.{name}_service]),
) -> SuccessResponse[{Name}Response]:
    data = await {name}_service.create_data(entity=item)
    return SuccessResponse(data={Name}Response(**data.model_dump(exclude={...})))
```

## §10. Exception Pattern

```python
from src._core.exceptions.base_exception import BaseCustomException

class {Name}NotFoundException(BaseCustomException):
    def __init__(self, {name}_id: int) -> None:
        super().__init__(
            status_code=404,
            message=f"{Name} with ID [ { {name}_id } ] not found",
            error_code="{NAME}_NOT_FOUND",
        )

class {Name}AlreadyExistsException(BaseCustomException):
    def __init__(self, {field}: str) -> None:
        super().__init__(
            status_code=409,
            message=f"{Name} with {field} [ { {field} } ] already exists",
            error_code="{NAME}_ALREADY_EXISTS",
        )
```

## §11. Admin Page Pattern

### File Structure & Naming Convention

```
interface/admin/
├── configs/{name}_admin_config.py   # Config declaration
└── pages/{name}_page.py            # Route handlers
```

- Config variable: `{name}_admin_page = BaseAdminPage(...)` — name must match `{name}_admin_page` for auto-discovery
- Config module path: `src.{name}.interface.admin.configs.{name}_admin_config`
- Page module path: `src.{name}.interface.admin.pages.{name}_page`

### Config File Pattern (`configs/{name}_admin_config.py`)

```python
from src._core.infrastructure.admin.base_admin_page import (
    BaseAdminPage,
    ColumnConfig,
)

{name}_admin_page = BaseAdminPage(
    domain_name="{name}",
    display_name="{Name}",
    icon="person",                    # Material icon name
    columns=[
        ColumnConfig(field_name="id", header_name="ID", width=80),
        ColumnConfig(field_name="username", header_name="Username", searchable=True),
        ColumnConfig(field_name="password", header_name="Password", masked=True),
        ColumnConfig(field_name="created_at", header_name="Created At"),
    ],
    searchable_fields=["username", "email"],
    sortable_fields=["id", "username", "created_at"],
    default_sort_field="id",
)
```

- `ColumnConfig` options: `field_name`, `header_name`, `sortable`, `searchable`, `hidden`, `masked`, `width`
- Sensitive fields (password, secret, token): always set `masked=True`
- Config only — no route logic, no `ui` import

### Page File Pattern (`pages/{name}_page.py`)

```python
from nicegui import ui

from src._core.infrastructure.admin.auth import require_auth
from src._core.infrastructure.admin.base_admin_page import BaseAdminPage
from src._core.infrastructure.admin.layout import admin_layout
from src.{name}.interface.admin.configs.{name}_admin_config import {name}_admin_page

# Injected by bootstrap_admin() after discovery
page_configs: list[BaseAdminPage] = []


@ui.page("/admin/{name}")
async def {name}_list_page(page: int = 1, search: str = ""):
    if not require_auth():
        return
    admin_layout(page_configs, current_domain="{name}")
    await {name}_admin_page.render_list(page=page, search=search)


@ui.page("/admin/{name}/{record_id}")
async def {name}_detail_page(record_id: int):
    if not require_auth():
        return
    admin_layout(page_configs, current_domain="{name}")
    await {name}_admin_page.render_detail(record_id=record_id)
```

### DI & Auto-discovery

- No `@inject`/`Provide` needed — service is resolved internally by `BaseAdminPage._service_provider`
- `bootstrap_admin()` auto-discovers domains via `discover_domains()`, loads config module, wires `_service_provider` from DI container, and imports page module (triggers `@ui.page` registration)
- `page_configs` list is injected by bootstrap into each page module (shared reference for navigation rendering)
- **No manual bootstrap registration needed** when adding admin pages to a domain

### Custom Rendering

For domain-specific rendering, subclass `BaseAdminPage` in the config file and override hook methods:
- `render_grid(dtos)` — custom AG Grid rendering
- `render_detail_card(dto)` — custom detail view
- `_fetch_list_data(page, search)` / `_fetch_detail_data(record_id)` — custom data fetching

## §12. S3 Vector Store Pattern

### S3VectorModel (Data Model)

`DynamoModel` counterpart — subclasses define index schema via `__s3vector_meta__` and declare metadata as Pydantic fields.

```python
from typing import ClassVar
from src._core.infrastructure.s3vectors.s3vector_model import (
    S3VectorModel, S3VectorModelMeta, S3VectorData,
)

class {Name}S3VectorModel(S3VectorModel):
    __s3vector_meta__: ClassVar[S3VectorModelMeta] = S3VectorModelMeta(
        index_name="{name}-search",
        # dimension defaults to settings.embedding_dimension (auto-derived)
        distance_metric="cosine",
        filter_fields=["category", "author_id"],
        non_filter_fields=["content_preview"],
    )

    category: str
    author_id: str
    content_preview: str
```

- `key`: auto-generated UUID v4 hex (via `generate_vector_id`)
- `data`: `S3VectorData(float32=[...])` — embedding vector
- Remaining fields → metadata (filter/non-filter)
- `to_s3vector()` serializes to S3 Vectors API format; `from_s3vector()` deserializes

### S3VectorModelMeta Fields

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `index_name` | `str` | required | S3 Vectors index name |
| `data_type` | `Literal["float32"]` | `"float32"` | Vector data type |
| `dimension` | `int` | `settings.embedding_dimension` | Vector dimension (auto-derived) |
| `distance_metric` | `Literal["cosine", "euclidean"]` | `"cosine"` | Distance metric |
| `filter_fields` | `list[str]` | `[]` | Filterable metadata fields |
| `non_filter_fields` | `list[str]` | `[]` | Non-filterable metadata fields |

### BaseS3VectorStore (Repository Counterpart)

Implements `BaseVectorStoreProtocol`. Subclass must implement `_to_model()` for domain-specific conversion.

```python
from src._core.infrastructure.s3vectors.base_s3vector_store import BaseS3VectorStore

class {Name}S3VectorStore(BaseS3VectorStore[{Name}DTO]):
    def __init__(self, s3vector_client, *, bucket_name):
        super().__init__(
            s3vector_client=s3vector_client,
            model={Name}S3VectorModel,
            return_entity={Name}DTO,
            bucket_name=bucket_name,
        )

    def _to_model(self, entity: BaseModel) -> {Name}S3VectorModel:
        return {Name}S3VectorModel(
            data=S3VectorData(float32=entity.embedding),
            category=entity.category,
            # ... map DTO fields to model metadata
        )
```

### BaseVectorStoreProtocol Methods

| Method | Signature |
|--------|---------|
| upsert | `async (entities: Sequence[BaseModel]) -> int` |
| search | `async (query: VectorQuery) -> VectorSearchResult[ReturnDTO]` |
| get | `async (keys: list[str]) -> list[ReturnDTO]` |
| delete | `async (keys: list[str]) -> bool` |

### S3 Vector Domain Variant (Directory Structure)

```
src/{name}/
├── infrastructure/
│   ├── s3vectors/
│   │   └── models/{name}_model.py    # extends S3VectorModel
│   ├── repositories/{name}_vector_store.py  # extends BaseS3VectorStore
│   └── di/{name}_container.py        # s3vector_client + embedding_client injection
└── (나머지 동일)
```

## §13. Embedding Pattern

### BaseEmbeddingProtocol

Backend-agnostic protocol for embedding implementations. Both OpenAI and Bedrock implement this.

```python
class BaseEmbeddingProtocol:
    @property
    def dimension(self) -> int: ...
    async def embed_text(self, text: str) -> list[float]: ...
    async def embed_batch(self, texts: list[str]) -> list[list[float]]: ...
```

### Provider Implementations

| Provider | Client Class | Batching | Dimension Source |
|----------|-------------|----------|-----------------|
| OpenAI | `OpenAIEmbeddingClient` | Auto (2048 items / 300K tokens) | Model lookup table |
| Bedrock | `BedrockEmbeddingClient` | Sequential (per-text invoke) | Model lookup table |

- OpenAI requires optional extras: `uv sync --extra openai` (openai + tiktoken)
- Bedrock uses aioboto3 (already a main dependency)
- Both raise domain exceptions: `EmbeddingRateLimitException`, `EmbeddingAuthenticationException`, `EmbeddingInputTooLongException`

### Text Chunking Utilities

| Function | Strategy | Use Case |
|----------|----------|----------|
| `chunk_text(text, chunk_size, overlap)` | Character-based (Unicode boundary aware) | General-purpose splitting |
| `chunk_text_by_tokens(text, model, max_tokens, overlap)` | Token-based (tiktoken-rs) | Embedding preprocessing |

- `semantic-text-splitter` handles Unicode word/sentence boundaries internally
- Token-based chunking uses tiktoken-rs (built into semantic-text-splitter) — no separate tiktoken install needed
