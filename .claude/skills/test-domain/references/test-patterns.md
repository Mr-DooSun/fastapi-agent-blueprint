# 테스트 패턴 상세

## 테스트 피라미드

### Unit Tests — `tests/unit/{name}/`

#### Service 테스트 (`tests/unit/{name}/domain/test_{name}_service.py`)
- MockRepository 클래스: Protocol의 모든 메서드를 in-memory dict로 구현
- 테스트 항목:
  - `test_create_data` — 생성 후 DTO 반환 확인
  - `test_get_data_by_data_id` — ID로 조회 확인
  - `test_get_datas_with_count` — 페이지네이션 데이터 + 카운트 확인
  - `test_update_data_by_data_id` — 수정 후 변경된 DTO 확인
  - `test_delete_data_by_data_id` — 삭제 후 True 반환 확인

#### UseCase 테스트 (`tests/unit/{name}/application/test_{name}_use_case.py`)
- MockService 클래스: Service 메서드를 Mock으로 구현
- 테스트 항목:
  - `test_create_data` — UseCase가 Service에 위임하는지 확인
  - `test_get_datas` — PaginationInfo가 올바르게 생성되는지 확인
  - `test_get_data_by_data_id` — 단건 조회 위임 확인

### Integration Tests — `tests/integration/{name}/`

#### Repository 테스트 (`tests/integration/{name}/infrastructure/test_{name}_repository.py`)
- `conftest.py`의 `test_db` 픽스처 사용 (SQLite in-memory)
- 실제 DB 연산 테스트: insert → select → update → delete

### E2E Tests — `tests/e2e/{name}/`

#### Router 테스트 (`tests/e2e/{name}/test_{name}_router.py`)
- TestClient로 HTTP 요청 테스트
- 상태 코드, 응답 구조, 에러 응답 확인

## Factory 패턴
`tests/factories/{name}_factory.py` 참고 패턴: `tests/factories/user_factory.py`

```python
from src.{name}.domain.dtos.{name}_dto import {Name}DTO
from src.{name}.interface.server.dtos.{name}_dto import Create{Name}Request, Update{Name}Request

def make_{name}_dto(**overrides) -> {Name}DTO:
    defaults = {
        "id": 1,
        # ... 도메인 필드 기본값
        "created_at": datetime.now(),
        "updated_at": datetime.now(),
    }
    defaults.update(overrides)
    return {Name}DTO(**defaults)

def make_create_{name}_request(**overrides) -> Create{Name}Request:
    defaults = {
        # ... 생성 필드 기본값
    }
    defaults.update(overrides)
    return Create{Name}Request(**defaults)
```
