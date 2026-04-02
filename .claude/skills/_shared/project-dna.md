# Project DNA - Project Pattern Reference Extracted from Code

> This file is auto-extracted/updated from `src/user/` (reference domain) and `src/_core/` (Base classes)
> when `/sync-guidelines` is run. **Run `/sync-guidelines` instead of editing manually.**
>
> Last updated: 2026-03-19

## Section Index
§0 Project Scale and Design Philosophy |
§1 Directory Structure | §2 Base Class Path | §3 Generic Type Signatures | §4 CRUD Methods
§5 DI Pattern | §6 Conversion Patterns | §7 Security Tools | §8 Active Features
§9 Router Pattern | §10 Exception Pattern | §11 Event Pattern

---

## §0. Project Scale and Design Philosophy

### Scale
- Enterprise-grade service with 10+ domains and 5+ team members
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
│   ├── events/{name}_events.py
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
    │   └── views/{name}_view.py
    └── worker/
        ├── tasks/{name}_test_task.py
        └── bootstrap/{name}_bootstrap.py
```

## §2. Base Class Import Path

| Class | Import Path |
|---------|------------|
| BaseRepositoryProtocol | `src._core.domain.protocols.repository_protocol.BaseRepositoryProtocol` |
| BaseService | `src._core.domain.services.base_service.BaseService` |
| BaseRepository | `src._core.infrastructure.database.base_repository.BaseRepository` |
| Base (ORM DeclarativeBase) | `src._core.infrastructure.database.database.Base` |
| Database | `src._core.infrastructure.database.database.Database` |
| BaseRequest | `src._core.application.dtos.base_request.BaseRequest` |
| BaseResponse | `src._core.application.dtos.base_response.BaseResponse` |
| SuccessResponse | `src._core.application.dtos.base_response.SuccessResponse` |
| ErrorResponse | `src._core.application.dtos.base_response.ErrorResponse` |
| PaginationInfo | `src._core.application.dtos.base_response.PaginationInfo` |
| ApiConfig | `src._core.application.dtos.base_config.ApiConfig` |
| BaseCustomException | `src._core.exceptions.base_exception.BaseCustomException` |
| DomainEvent | `src._core.domain.events.domain_event.DomainEvent` |
| ValueObject | `src._core.domain.value_objects.value_object.ValueObject` |
| make_pagination | `src._core.common.pagination.make_pagination` |
| CoreContainer | `src._core.infrastructure.di.core_container.CoreContainer` |

### Inheritance Chain

- `BaseRequest` → `ApiConfig` → `BaseModel` (camelCase alias, frozen, populate_by_name)
- `BaseResponse` → `ApiConfig` → `BaseModel`
- `SuccessResponse` → `ApiConfig`, `Generic[ReturnType]`
- `ValueObject` → `BaseModel` (frozen=True)
- `DomainEvent` → `BaseModel` (event_id: UUID, occurred_at: datetime)

## §3. Generic Type Signatures

```python
# Shared by BaseRepositoryProtocol / BaseRepository / BaseService
ReturnDTO = TypeVar("ReturnDTO", bound=BaseModel)

class BaseRepositoryProtocol(Generic[ReturnDTO]): ...
class BaseRepository(Generic[ReturnDTO], ABC): ...
class BaseService(Generic[ReturnDTO]): ...

# SuccessResponse
ReturnType = TypeVar("ReturnType")
class SuccessResponse(ApiConfig, Generic[ReturnType]): ...

# Reference domain (user) usage example:
class UserRepositoryProtocol(BaseRepositoryProtocol[UserDTO]): pass
class UserRepository(BaseRepository[UserDTO]): ...
class UserService(BaseService[UserDTO]): ...
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
| select_datas_with_count | `async (page: int, page_size: int) -> tuple[list[ReturnDTO], int]` |
| update_data_by_data_id | `async (data_id: int, entity: BaseModel) -> ReturnDTO` |
| delete_data_by_data_id | `async (data_id: int) -> bool` |
| count_datas | `async () -> int` |

### BaseService Methods (Repository Delegation Mapping)

> `BaseService[ReturnDTO]` provides all methods below.
> Domain Services extend `BaseService[{Name}DTO]` and only override when custom logic is needed.

| BaseService Method | Repository Call | Notes |
|-------------------|----------------|------|
| create_data(entity) | insert_data(entity=entity) | |
| create_datas(entities) | insert_datas(entities=entities) | |
| get_datas(page, page_size) | select_datas_with_count(page, page_size) | Returns `(list[ReturnDTO], PaginationInfo)` |
| get_data_by_data_id(data_id) | select_data_by_id(data_id=data_id) | |
| get_datas_by_data_ids(data_ids) | select_datas_by_ids(data_ids=data_ids) | |
| update_data_by_data_id(data_id, entity) | update_data_by_data_id(data_id, entity) | |
| delete_data_by_data_id(data_id) | delete_data_by_data_id(data_id=data_id) | |
| count_datas() | count_datas() | |

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

## §6. Conversion Patterns

| Conversion | Pattern | Example |
|------|------|------|
| ORM → DTO | `ReturnDTO.model_validate(data, from_attributes=True)` | `UserDTO.model_validate(data, from_attributes=True)` |
| Request → Service | Direct pass `entity=item` (when fields match) | `create_data(entity=item)` |
| Request → DTO | `CreateDTO(**item.model_dump(), extra=...)` (when fields differ) | `CreateOrderDTO(**item.model_dump(), user_id=current_user.id)` |
| DTO → Response | `{Name}Response(**data.model_dump(exclude={...}))` | `UserResponse(**data.model_dump(exclude={"password"}))` |

## §7. Security Tools

### Pre-commit (Auto-run)

- trailing-whitespace, end-of-file-fixer, check-yaml/json/toml
- ruff check --fix (Unified rules for E, W, F, UP, I, B, C4, SIM, S -- replaces pyupgrade, autoflake, isort, flake8, bandit)
- ruff format (Black-compatible formatting)

### Pre-commit (Manual Stage)

- mypy (--ignore-missing-imports, --check-untyped-defs)

### Architecture Violation Check (Auto-run)

- no-domain-infra-import: No Infrastructure imports from Domain layer
- no-entity-pattern: No Entity pattern -- unified to DTO (background: ADR 004)

### Claude Hook

- PreToolUse (pre-tool-security): SQL injection, hardcoded secrets, Domain→Infra import, sensitive data logging check
- PostToolUse (post-tool-sync-warning): Recommends running /sync-guidelines when core files (_core/, pyproject.toml, .pre-commit-config.yaml, .serena/memories/, .claude/skills/_shared/, .claude/hooks/) are modified
- Stop (stop-sync-reminder): Warns before turn ends if core files were modified during the session but /sync-guidelines was not run

## §8. Active Features

| Feature | Status | Notes |
|------|------|------|
| Taskiq async tasks | Active | SQS broker, @broker.task decorator |
| SQLAlchemy 2.0+ | Active | Mapped[T] + mapped_column() |
| Pydantic 2.x | Active | model_validate, model_dump, ConfigDict |
| dependency-injector | Active | DeclarativeContainer, @inject + Provide |
| AWS S3 (aioboto3) | Active | ObjectStorage + ObjectStorageClient |
| sqladmin (ModelView) | Active | Admin view registration |
| alembic (migrations) | Active | DB migrations |
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

## §11. Event Pattern

```python
from src._core.domain.events.domain_event import DomainEvent

class {Name}Created(DomainEvent):
    event_type: str = "{name}.created"
    {name}_id: int
    # ... domain-specific fields

class {Name}Updated(DomainEvent):
    event_type: str = "{name}.updated"
    {name}_id: int

class {Name}Deleted(DomainEvent):
    event_type: str = "{name}.deleted"
    {name}_id: int
```
