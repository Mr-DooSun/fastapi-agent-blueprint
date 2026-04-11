# Domain Scaffolding Layer Details

## File Count Summary
- **Default (no UseCase)**: 15 content + 25 `__init__.py` + 4 tests = **44 files**
- **With UseCase**: 16 content + 25 `__init__.py` + 5 tests = **46 files**

> Every Python package directory gets an empty `__init__.py`.
> The numbered items below are **content files only** — `__init__.py` files are created automatically
> for each directory shown in the tree structure.

## Reference
- Follow `src/user/` exactly. Read the corresponding user file before creating each file and replicate the pattern.
- For **Base class import paths, Generic signatures, DI patterns**,
  refer to `.claude/skills/_shared/project-dna.md`.

## Layer 1: Domain (Absolutely no infrastructure dependencies)

```
src/{name}/
├── __init__.py
└── domain/
    ├── __init__.py
    ├── dtos/
    │   ├── __init__.py
    │   └── {name}_dto.py                  ← #1
    ├── protocols/
    │   ├── __init__.py
    │   └── {name}_repository_protocol.py  ← #2
    ├── services/
    │   ├── __init__.py
    │   └── {name}_service.py              ← #3
    └── exceptions/
        ├── __init__.py
        └── {name}_exceptions.py           ← #4
```

1. `src/{name}/domain/dtos/{name}_dto.py`
   - `from pydantic import BaseModel, Field`
   - `class {Name}DTO(BaseModel)` — id, user-defined fields, created_at, updated_at
   - Use `Field(..., description="...")` for all fields
2. `src/{name}/domain/protocols/{name}_repository_protocol.py`
   - `from src._core.domain.protocols.repository_protocol import BaseRepositoryProtocol`
   - Generic: `BaseRepositoryProtocol[{Name}DTO]` (see project-dna.md section 3)
   - `class {Name}RepositoryProtocol(BaseRepositoryProtocol[{Name}DTO]): pass`
3. `src/{name}/domain/services/{name}_service.py`
   - `from src._core.domain.services.base_service import BaseService`
   - `class {Name}Service(BaseService[Create{Name}Request, Update{Name}Request, {Name}DTO])`
   - BaseService uses 3 TypeVars: `Generic[CreateDTO, UpdateDTO, ReturnDTO]` (background: ADR 011 update)
   - CRUD methods (create_data, get_datas, get_data_by_data_id, etc.) are inherited from BaseService
   - Override methods only when custom business logic is needed
   - Import Request types from `src/{name}/interface/server/schemas/{name}_schema.py`
4. `src/{name}/domain/exceptions/{name}_exceptions.py`
   - `from src._core.exceptions.base_exception import BaseCustomException`
   - `{Name}NotFoundException(status_code=404, error_code="{NAME}_NOT_FOUND")`
   - `{Name}AlreadyExistsException(status_code=409, error_code="{NAME}_ALREADY_EXISTS")`
## Layer 2: Application (Optional — only when complex business logic exists)

> Do not create UseCases for basic CRUD domains.
> BaseService provides all CRUD delegation including pagination, so Router -> Service direct injection is sufficient.
> Add UseCases only when combining multiple Services or when complex business workflows are needed.

```
└── application/
    ├── __init__.py
    └── use_cases/
        ├── __init__.py
        └── {name}_use_case.py             ← #6 (optional)
```

6. `src/{name}/application/use_cases/{name}_use_case.py` — **create only when complex logic exists**
   - `__init__(self, {name}_service: {Name}Service)`
   - Handles complex workflows such as combining multiple Services, transaction orchestration, etc.

## Layer 3: Infrastructure

```
└── infrastructure/
    ├── __init__.py
    ├── database/
    │   ├── __init__.py
    │   └── models/
    │       ├── __init__.py
    │       └── {name}_model.py            ← #7
    ├── repositories/
    │   ├── __init__.py
    │   └── {name}_repository.py           ← #8
    └── di/
        ├── __init__.py
        └── {name}_container.py            ← #9
```

7. `src/{name}/infrastructure/database/models/{name}_model.py`
    - `from src._core.infrastructure.database.database import Base`
    - `class {Name}Model(Base)` — SQLAlchemy 2.0 `Mapped[Type]` + `mapped_column()`
    - `__tablename__ = "{name}"`
    - Use `func.now()` for `created_at`, `updated_at`
8. `src/{name}/infrastructure/repositories/{name}_repository.py`
    - `from src._core.infrastructure.database.base_repository import BaseRepository`
    - Generic: `BaseRepository[{Name}DTO]` (see project-dna.md section 3)
    - `class {Name}Repository(BaseRepository[{Name}DTO])`
    - `__init__` signature: refer to **project-dna.md section 3** "BaseRepository.__init__"
    - `super().__init__(database=database, model={Name}Model, return_entity={Name}DTO)`
9. `src/{name}/infrastructure/di/{name}_container.py`
    - DI pattern: refer to **project-dna.md section 5**
    - `class {Name}Container(containers.DeclarativeContainer)`
    - `core_container = providers.DependenciesContainer()`
    - Repository = `providers.Singleton`, Service = `providers.Factory`
    - Do not create UseCase provider by default (add only when complex logic is needed)

### DynamoDB Variant (Layer 3)

When the domain uses DynamoDB instead of RDB, replace `infrastructure/database/` with `infrastructure/dynamodb/`:

```
└── infrastructure/
    ├── dynamodb/
    │   ├── __init__.py
    │   └── models/
    │       ├── __init__.py
    │       └── {name}_model.py            ← DynamoModel subclass
    ├── repositories/
    │   ├── __init__.py
    │   └── {name}_repository.py           ← BaseDynamoRepository[{Name}DTO]
    └── di/
        ├── __init__.py
        └── {name}_container.py            ← dynamodb_client injection
```

- Model: `from src._core.infrastructure.dynamodb.dynamodb_model import DynamoModel, DynamoModelMeta`
- Repository: `from src._core.infrastructure.dynamodb.base_dynamo_repository import BaseDynamoRepository`
- DI: `dynamodb_client=core_container.dynamodb_client` (not `database=core_container.database`)
- Refer to **project-dna.md "DynamoDB Generic Type Signatures"** and **"DynamoDB DI Pattern"** for details

## Layer 4: Interface

```
└── interface/
    ├── __init__.py
    ├── server/
    │   ├── __init__.py
    │   ├── schemas/
    │   │   ├── __init__.py
    │   │   └── {name}_schema.py           ← #10
    │   ├── routers/
    │   │   ├── __init__.py
    │   │   └── {name}_router.py           ← #11
    │   └── bootstrap/
    │       ├── __init__.py
    │       └── {name}_bootstrap.py        ← #12
    ├── admin/
    │   ├── __init__.py
    │   ├── configs/
    │   │   ├── __init__.py
    │   │   └── {name}_admin_config.py     ← #13
    │   └── pages/
    │       ├── __init__.py
    │       └── {name}_page.py             ← #14
    └── worker/
        ├── __init__.py
        ├── payloads/
        │   ├── __init__.py
        │   └── {name}_payload.py          ← #15
        ├── tasks/
        │   ├── __init__.py
        │   └── {name}_test_task.py        ← #16
        └── bootstrap/
            ├── __init__.py
            └── {name}_bootstrap.py        ← #17
```

10. `src/{name}/interface/server/schemas/{name}_schema.py`
    - `from src._core.application.dtos.base_response import BaseResponse`
    - `from src._core.application.dtos.base_request import BaseRequest`
    - `{Name}Response(BaseResponse)` — exclude sensitive fields
    - `Create{Name}Request(BaseRequest)` — creation fields
    - `Update{Name}Request(BaseRequest)` — all fields Optional (`| None = None`)
    - **Multiple inheritance absolutely prohibited**
11. `src/{name}/interface/server/routers/{name}_router.py`
    - Router pattern: refer to **project-dna.md section 9**
    - `router = APIRouter()`
    - CRUD endpoints: POST /{name}, POST /{name}s, GET /{name}s, GET /{name}/{id}, PUT /{name}/{id}, DELETE /{name}/{id}
    - `@inject` + `Depends(Provide[{Name}Container.{name}_service])`
    - Conversion Patterns: refer to **project-dna.md section 6**
    - Return: `SuccessResponse(data=...)`
12. `src/{name}/interface/server/bootstrap/{name}_bootstrap.py`
    - `create_{name}_container()` — `wire(packages=["src.{name}.interface.server.routers"])`
    - `setup_{name}_routes(app)` — `app.include_router(prefix="/v1", tags=["{name}"])`
    - `bootstrap_{name}_domain(app, database, {name}_container)`
13. `src/{name}/interface/admin/configs/{name}_admin_config.py`
    - Admin page config: refer to **project-dna.md section 11**
    - `{name}_admin_page = BaseAdminPage(...)` with `ColumnConfig` for each DTO field
    - Mark sensitive fields with `masked=True` (e.g., password)
14. `src/{name}/interface/admin/pages/{name}_page.py`
    - Admin page routes: refer to **project-dna.md section 11**
    - `page_configs: list[BaseAdminPage] = []` — injected by `bootstrap_admin()`
    - `@ui.page` routes for list and detail views
    - No `@inject`/`Provide` needed (service resolved internally by `BaseAdminPage`)
15. `src/{name}/interface/worker/payloads/{name}_payload.py`
    - `from src._core.application.dtos.base_payload import BasePayload`
    - `class {Name}TestPayload(BasePayload)` — worker message contract
    - Define only the fields needed for the test task message
    - Does NOT inherit from domain DTO (independent contract)
16. `src/{name}/interface/worker/tasks/{name}_test_task.py`
    - `@broker.task(task_name=f"{settings.task_name_prefix}.{name}.test")`
    - Requires `from src._core.config import settings` import
    - `@inject` + `Provide[{Name}Container.{name}_service]`
    - `**kwargs` → `{Name}TestPayload.model_validate(kwargs)` → pass payload to Service directly
17. `src/{name}/interface/worker/bootstrap/{name}_bootstrap.py`
    - `wire(modules=[{name}_test_task])`
    - Function name: `bootstrap_{name}_domain` (unified convention with server)

## Layer 5: App Wiring (Automatic — no manual registration needed)

> `discover_domains()` in `src/_core/infrastructure/discovery.py`
> automatically detects `src/{name}/infrastructure/di/{name}_container.py`.
> The `DynamicContainer` factory functions in Server/Worker dynamically register these,
> so there is no need to modify `container.py` or `bootstrap.py`.
>
> Auto-discovery conditions:
> - `src/{name}/__init__.py` exists
> - `src/{name}/infrastructure/di/{name}_container.py` exists
> - Directory name does not start with `_` or `.`

## Layer 6: Tests

18. `tests/factories/{name}_factory.py` — `make_{name}_dto()`, `make_create_{name}_request()`, `make_{name}_test_payload()`
19. `tests/unit/{name}/domain/test_{name}_service.py` — MockRepository + CRUD tests
20. `tests/unit/{name}/application/test_{name}_use_case.py` — **only when UseCase exists** MockService + tests
21. `tests/integration/{name}/infrastructure/test_{name}_repository.py` — uses test_db fixture
22. `tests/e2e/{name}/test_{name}_router.py` — TestClient HTTP 요청 테스트
