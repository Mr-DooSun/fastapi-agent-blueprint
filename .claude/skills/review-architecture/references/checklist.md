# Architecture Audit Checklist Details

> Refer to `.claude/skills/_shared/project-dna.md` for detailed definitions of expected patterns.

## 1. Layer Dependency Rules
Grep-check Python files in each domain:

- [ ] No `from src.{name}.infrastructure` imports in `src/{name}/domain/` files
- [ ] No `from src.{name}.interface` imports in `src/{name}/domain/` files
- [ ] No `from src.{name}.infrastructure` imports in `src/{name}/application/` files (excluding DI)
- [ ] No `from sqlalchemy` imports in `src/{name}/domain/` files
- [ ] No `from dependency_injector` imports in `src/{name}/domain/` files

## 2. Conversion Patterns Compliance
Check across all domain files:

- [ ] No `class.*Mapper` class definitions
- [ ] No Entity pattern remnants (`to_entity(`, `from_entity(`, `Entity` class definitions)
- [ ] Repository method return values are DTO types (no Model object exposure)
- [ ] Model -> DTO conversion uses `model_validate(..., from_attributes=True)`

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
- [ ] Service receives domain DTO, not Payload (conversion happens in task)

## 7. Bootstrap Wiring
Check app-level files and auto-discovery mechanism:

- [ ] `src/{name}/interface/server/bootstrap/{name}_bootstrap.py` exists
- [ ] `src/{name}/infrastructure/di/{name}_container.py` exists (auto-discovery condition)
- [ ] `src/{name}/__init__.py` exists (auto-discovery condition)
- [ ] `wire(packages=[...])` call targets the correct packages
- [ ] **Note**: `discover_domains()` handles auto-detection, so manual registration in App-level `container.py`/`bootstrap.py` is not needed (project-dna.md section 5)
