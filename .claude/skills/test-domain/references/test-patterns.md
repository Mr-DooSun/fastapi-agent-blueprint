# Test Pattern Details

## Test Pyramid

### Unit Tests — `tests/unit/{name}/`

#### Service Tests (`tests/unit/{name}/domain/test_{name}_service.py`)
- MockRepository class: implement all Protocol methods with in-memory dict
- Test items:
  - `test_create_data` — verify DTO returned after creation
  - `test_get_data_by_data_id` — verify retrieval by ID
  - `test_get_datas_with_count` — verify pagination data + count
  - `test_update_data_by_data_id` — verify changed DTO after update
  - `test_delete_data_by_data_id` — verify True returned after deletion

#### UseCase Tests (`tests/unit/{name}/application/test_{name}_use_case.py`)
- MockService class: implement Service methods with Mock
- Test items:
  - `test_create_data` — verify UseCase delegates to Service
  - `test_get_datas` — verify PaginationInfo is correctly generated
  - `test_get_data_by_data_id` — verify single item retrieval delegation

### Integration Tests — `tests/integration/{name}/`

#### Repository Tests (`tests/integration/{name}/infrastructure/test_{name}_repository.py`)
- Uses `test_db` fixture from `conftest.py` (SQLite in-memory)
- Test actual DB operations: insert -> select -> update -> delete

### E2E Tests — `tests/e2e/{name}/`

#### Router Tests (`tests/e2e/{name}/test_{name}_router.py`)
- Test HTTP requests with TestClient
- Verify status codes, response structure, error responses

## Factory Pattern
`tests/factories/{name}_factory.py` reference pattern: `tests/factories/user_factory.py`

```python
from src.{name}.domain.dtos.{name}_dto import {Name}DTO
from src.{name}.interface.server.schemas.{name}_schema import Create{Name}Request, Update{Name}Request

def make_{name}_dto(**overrides) -> {Name}DTO:
    defaults = {
        "id": 1,
        # ... domain field defaults
        "created_at": datetime.now(),
        "updated_at": datetime.now(),
    }
    defaults.update(overrides)
    return {Name}DTO(**defaults)

def make_create_{name}_request(**overrides) -> Create{Name}Request:
    defaults = {
        # ... creation field defaults
    }
    defaults.update(overrides)
    return Create{Name}Request(**defaults)
```
