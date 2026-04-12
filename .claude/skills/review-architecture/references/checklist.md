# Architecture Audit Checklist Details

> Refer to `.claude/skills/_shared/project-dna.md` for detailed definitions of expected patterns.

## 1. Layer Dependency Rules
Grep-check Python files in each domain:

- [ ] No `from src.{name}.infrastructure` imports in `src/{name}/domain/` files
- [ ] No `from src.{name}.interface` imports in `src/{name}/domain/` files — **except** `schemas/` (Request types are passed directly when fields match, per AGENTS.md Write DTO criteria)
- [ ] No `from src.{name}.infrastructure` imports in `src/{name}/application/` files (excluding DI)
- [ ] No `from sqlalchemy` imports in `src/{name}/domain/` files
- [ ] No `from dependency_injector` imports in `src/{name}/domain/` files

## 2. Conversion Patterns Compliance
Check across all domain files:

- [ ] No `class.*Mapper` class definitions
- [ ] No Entity pattern remnants (`to_entity(`, `from_entity(`, `Entity` class definitions)
- [ ] Repository method return values are DTO types (no Model object exposure)
- [ ] Model -> DTO conversion uses `model_validate(..., from_attributes=True)`
- [ ] Service classes use 3 TypeVars: `BaseService[Create{Name}Request, Update{Name}Request, {Name}DTO]` (not `BaseService[{Name}DTO]`)
- [ ] Service method overrides match parent signature types (no LSP-violating parameter narrowing)

## 3. DTO/Response Integrity
Check interface/server/schemas/ files:

- [ ] Response classes inherit only from `BaseResponse` (no multiple inheritance)
- [ ] Request classes inherit only from `BaseRequest` (no multiple inheritance)
- [ ] Sensitive fields (password, etc.) not included in Response
- [ ] Router uses `model_dump(exclude={...})` to exclude sensitive fields

## 4. DI Container Correctness
Check infrastructure/di/ files (expected pattern: refer to **project-dna.md section 5**):

- [ ] Container inherits from `containers.DeclarativeContainer`
- [ ] `core_container = providers.DependenciesContainer()` declared
- [ ] Repository uses `providers.Singleton`
- [ ] Service uses `providers.Factory`
- [ ] UseCase uses `providers.Factory`

## 5. Test Coverage
Check tests/ directory:

- [ ] `tests/factories/{name}_factory.py` exists
- [ ] `tests/unit/{name}/domain/test_{name}_service.py` exists
- [ ] `tests/unit/{name}/application/test_{name}_use_case.py` exists **(only when UseCase exists)**
- [ ] `tests/integration/{name}/infrastructure/test_{name}_repository.py` exists

## 6. Worker Payload Compliance
Check interface/worker/ files:

- [ ] Worker tasks validate `**kwargs` via a Payload class (not directly via domain DTO)
- [ ] Payload classes inherit from `BasePayload` (not `BaseModel` or `BaseRequest`)
- [ ] Payload files live in `interface/worker/payloads/` (not in domain layer)
- [ ] When fields match: Payload passed directly to Service (same as Request pattern)
- [ ] When fields differ: explicit DTO conversion in task

## 7. Admin Page Compliance
Check interface/admin/ files (expected pattern: refer to **project-dna.md section 11**):

- [ ] Config file exists: `src/{name}/interface/admin/configs/{name}_admin_config.py`
- [ ] Config variable named `{name}_admin_page` (discovery convention)
- [ ] Page file exists: `src/{name}/interface/admin/pages/{name}_page.py`
- [ ] Page file imports config from the configs module (not defined inline)
- [ ] No direct Service import in page file (service resolved via BaseAdminPage internally)
  - Grep: No `from src.{name}.domain.services` in `interface/admin/pages/` files
- [ ] `page_configs: list[BaseAdminPage] = []` declared at module level in page file
- [ ] `require_auth()` called at the top of every `@ui.page` function
- [ ] Sensitive fields use `masked=True` in ColumnConfig (password, secret, token)

## 8. Bootstrap Wiring
Check app-level files and auto-discovery mechanism:

- [ ] `src/{name}/interface/server/bootstrap/{name}_bootstrap.py` exists
- [ ] `src/{name}/infrastructure/di/{name}_container.py` exists (auto-discovery condition)
- [ ] `src/{name}/__init__.py` exists (auto-discovery condition)
- [ ] `wire(packages=[...])` call targets the correct packages
- [ ] **Note**: `discover_domains()` handles auto-detection, so manual registration in App-level `container.py`/`bootstrap.py` is not needed (project-dna.md section 5)

## 9. DynamoDB Domain Compliance
Check only when a domain uses DynamoDB (has `infrastructure/dynamodb/` directory):

- [ ] DynamoDB models stored in `infrastructure/dynamodb/models/` (not `infrastructure/database/`)
- [ ] Model inherits from `DynamoModel` (not SQLAlchemy `Base`)
- [ ] Repository inherits from `BaseDynamoRepository[{Name}DTO]` (not `BaseRepository`)
- [ ] Service inherits from `BaseDynamoService[Create{Name}Request, Update{Name}Request, {Name}DTO]` (not `BaseService`)
- [ ] DI Container uses `dynamodb_client=core_container.dynamodb_client` (not `database=core_container.database`)
- [ ] No `from sqlalchemy` imports in DynamoDB domain files
- [ ] Protocol inherits from `BaseDynamoRepositoryProtocol[{Name}DTO]` (not `BaseRepositoryProtocol`)
