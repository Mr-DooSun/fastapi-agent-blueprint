# Project DNA - 코드에서 추출된 프로젝트 패턴 참조

> 이 파일은 `/sync-guidelines` 실행 시 `src/user/`(레퍼런스 도메인)와 `src/_core/`(Base 클래스)에서
> 자동 추출/갱신됩니다. **수동 편집 대신 `/sync-guidelines`를 실행하세요.**
>
> 최종 갱신: 2026-03-19

## 섹션 인덱스
§0 프로젝트 스케일 및 설계 철학 |
§1 디렉토리 구조 | §2 Base Class 경로 | §3 Generic 시그니처 | §4 CRUD 메서드
§5 DI 패턴 | §6 변환 패턴 | §7 보안 도구 | §8 활성 기능
§9 Router 패턴 | §10 Exception 패턴 | §11 Event 패턴

---

## §0. 프로젝트 스케일 및 설계 철학

### 스케일
- 도메인 10개 이상, 팀원 5명 이상의 엔터프라이즈급 서비스
- 모든 제안과 설계는 이 규모를 전제로 확장성, 유지보수성, 팀 협업을 고려한다

### 제안 시 엔터프라이즈 관행 적용 기준

Skills가 코드 생성, 설계 제안, 리뷰를 수행할 때 아래 관점을 능동적으로 고려한다:

**확장성**
- 목록 조회 API는 항상 pagination을 기본 포함한다
- 대량 데이터 처리가 예상되면 비동기 Worker 태스크 분리를 제안한다
- N+1 쿼리 위험이 있는 관계 조회는 joinedload/selectinload를 명시한다

**팀 협업**
- 도메인 간 의존성은 반드시 Protocol 기반 DIP로 제안한다 (직접 import 제안 금지)
- 공유 DTO 변경 시 영향 범위(어떤 도메인이 참조하는지)를 먼저 분석한다
- API 시그니처 변경은 하위 호환성을 기본으로 제안한다

**운영**
- 데이터 변경(CUD) API는 audit trail 필요 여부를 확인한다
- 외부 API 연동 시 timeout, retry, circuit breaker 설정을 제안한다
- 에러 응답은 클라이언트가 대응 가능한 수준의 error_code를 포함한다

**보안**
- 민감 데이터(PII)는 Response에서 제외하고 로그에 기록하지 않는다
- 인증이 필요한 엔드포인트는 명시적으로 표시한다
- 환경별 설정(시크릿, DB URL)은 환경변수로만 관리한다

---

## §1. 레이어 디렉토리 구조

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
│   └── value_objects/                    # (필요 시)
├── application/
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
    │   ├── dtos/{name}_dto.py
    │   ├── routers/{name}_router.py
    │   └── bootstrap/{name}_bootstrap.py
    ├── admin/
    │   └── views/{name}_view.py
    └── worker/
        ├── tasks/{name}_test_task.py
        └── bootstrap/{name}_bootstrap.py
```

## §2. Base Class Import 경로

| 클래스명 | Import 경로 |
|---------|------------|
| BaseRepositoryProtocol | `src._core.domain.protocols.repository_protocol.BaseRepositoryProtocol` |
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

### 상속 체인

- `BaseRequest` → `ApiConfig` → `BaseModel` (camelCase alias, frozen, populate_by_name)
- `BaseResponse` → `ApiConfig` → `BaseModel`
- `SuccessResponse` → `ApiConfig`, `Generic[ReturnType]`
- `ValueObject` → `BaseModel` (frozen=True)
- `DomainEvent` → `BaseModel` (event_id: UUID, occurred_at: datetime)

## §3. Generic 타입 시그니처

```python
# BaseRepositoryProtocol / BaseRepository 공통
CreateDTO = TypeVar("CreateDTO", bound=BaseModel)
ReturnDTO = TypeVar("ReturnDTO", bound=BaseModel)
UpdateDTO = TypeVar("UpdateDTO", bound=BaseModel)

class BaseRepositoryProtocol(Generic[CreateDTO, ReturnDTO, UpdateDTO]): ...
class BaseRepository(Generic[CreateDTO, ReturnDTO, UpdateDTO], ABC): ...

# SuccessResponse
ReturnType = TypeVar("ReturnType")
class SuccessResponse(ApiConfig, Generic[ReturnType]): ...

# 레퍼런스 도메인 (user) 사용 예:
class UserRepositoryProtocol(BaseRepositoryProtocol[BaseModel, UserDTO, BaseModel]): pass
class UserRepository(BaseRepository[BaseModel, UserDTO, BaseModel]): ...
```

### BaseRepository.__init__ 시그니처

```python
def __init__(
    self,
    database: Database,
    *,
    model: type[Base],
    return_entity: type[ReturnDTO],
    create_entity: type[CreateDTO] | None = None,
    update_entity: type[UpdateDTO] | None = None,
) -> None:
```

## §4. Base CRUD 메서드

### BaseRepositoryProtocol 메서드

| 메서드 | 시그니처 |
|--------|---------|
| insert_data | `async (entity: CreateDTO) -> ReturnDTO` |
| insert_datas | `async (entities: list[CreateDTO]) -> list[ReturnDTO]` |
| select_datas | `async (page: int, page_size: int) -> list[ReturnDTO]` |
| select_data_by_id | `async (data_id: int) -> ReturnDTO` |
| select_datas_by_ids | `async (data_ids: list[int]) -> list[ReturnDTO]` |
| select_datas_with_count | `async (page: int, page_size: int) -> tuple[list[ReturnDTO], int]` |
| update_data_by_data_id | `async (data_id: int, entity: UpdateDTO) -> ReturnDTO` |
| delete_data_by_data_id | `async (data_id: int) -> bool` |
| count_datas | `async () -> int` |

### Service 메서드 (Repository 위임 매핑)

| Service 메서드 | Repository 호출 |
|---------------|----------------|
| create_data(entity) | insert_data(entity=entity) |
| create_datas(entities) | insert_datas(entities=entities) |
| get_datas_with_count(page, page_size) | select_datas_with_count(page, page_size) |
| get_data_by_data_id(data_id) | select_data_by_id(data_id=data_id) |
| get_datas_by_data_ids(data_ids) | select_datas_by_ids(data_ids=data_ids) |
| update_data_by_data_id(data_id, entity) | update_data_by_data_id(data_id, entity) |
| delete_data_by_data_id(data_id) | delete_data_by_data_id(data_id=data_id) |
| count_datas() | count_datas() |

## §5. DI 패턴

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

    {name}_use_case = providers.Factory(
        {Name}UseCase,
        {name}_service={name}_service,
    )
```

| 컴포넌트 | Provider 타입 |
|---------|--------------|
| Database | `providers.Singleton` |
| Repository | `providers.Singleton` |
| Service | `providers.Factory` |
| UseCase | `providers.Factory` |
| 도메인 Container | `containers.DeclarativeContainer` |
| 외부 Container 참조 | `providers.DependenciesContainer()` |
| App Container (Server/Worker) | `containers.DynamicContainer` (팩토리 함수) |
| 도메인 자동 발견 | `src._core.infrastructure.discovery.discover_domains()` |
| Container 동적 로드 | `src._core.infrastructure.discovery.load_domain_container()` |

### App-level Container (자동 발견)

도메인 Container는 `DeclarativeContainer`를 사용하지만,
Server/Worker의 App-level Container는 `DynamicContainer` + 팩토리 함수를 사용한다.
`discover_domains()`가 `src/*/` 하위 유효 도메인을 자동 탐지하여 등록하므로,
**새 도메인 추가 시 App-level container/bootstrap 파일 수정이 불필요하다.**

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

## §6. 변환 패턴

| 변환 | 패턴 | 예시 |
|------|------|------|
| ORM → DTO | `ReturnDTO.model_validate(data, from_attributes=True)` | `UserDTO.model_validate(data, from_attributes=True)` |
| Request → Service | `entity=item` 직접 전달 (필드 동일 시) | `create_data(entity=item)` |
| Request → DTO | `CreateDTO(**item.model_dump(), extra=...)` (필드 다를 시) | `CreateOrderDTO(**item.model_dump(), user_id=current_user.id)` |
| DTO → Response | `{Name}Response(**data.model_dump(exclude={...}))` | `UserResponse(**data.model_dump(exclude={"password"}))` |

## §7. 보안 도구

### Pre-commit (자동 실행)

- trailing-whitespace, end-of-file-fixer, check-yaml/json/toml
- pyupgrade (--py312-plus)
- autoflake (미사용 import/변수 제거)
- isort (--profile black)
- black (python3.12)
- flake8 + flake8-bugbear + flake8-comprehensions (--ignore=F841,E501,W503,E203,E402,F401,B008,B006,C901,SIM114,SIM910,SIM904,E704, --max-line-length=88, --max-complexity=20)
- bandit (-ll, --skip=B113,B314,B413)

### Pre-commit (수동 - manual stage)

- mypy (--ignore-missing-imports, --check-untyped-defs)

### 아키텍처 위반 검사 (자동 실행)

- no-domain-infra-import: Domain에서 Infrastructure import 금지
- no-entity-import: Entity import 금지 (DTO로 대체됨)
- no-entity-methods: to_entity/from_entity 메서드 금지
- no-multiple-inheritance-response: Response/Request 다중상속 금지

### Claude Hook

- PreToolUse (pre-tool-security): SQL injection, 하드코딩 시크릿, Domain→Infra import, 민감 데이터 로그 검사
- PostToolUse (post-tool-sync-warning): 코어 파일(_core/, pyproject.toml, .pre-commit-config.yaml, .serena/memories/, .claude/skills/_shared/, .claude/hooks/) 수정 시 /sync-guidelines 실행 권고
- Stop: 핵심 파일 수정 후 /sync-guidelines 미실행 시 세션 종료 전 경고

## §8. 활성 기능

| 기능 | 상태 | 비고 |
|------|------|------|
| Taskiq async tasks | 활성 | SQS 브로커, @broker.task 데코레이터 |
| SQLAlchemy 2.0+ | 활성 | Mapped[T] + mapped_column() |
| Pydantic 2.x | 활성 | model_validate, model_dump, ConfigDict |
| dependency-injector | 활성 | DeclarativeContainer, @inject + Provide |
| AWS S3 (aioboto3) | 활성 | ObjectStorage + ObjectStorageClient |
| sqladmin (ModelView) | 활성 | Admin 뷰 등록 |
| alembic (migrations) | 활성 | DB 마이그레이션 |
| JWT/Authentication | 미구현 | |
| File Upload (UploadFile) | 미구현 | |
| RBAC/Permissions | 미구현 | |
| Rate Limiting (slowapi) | 미구현 | |
| WebSocket | 미구현 | |

## §9. Router 패턴

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
    {name}_use_case: {Name}UseCase = Depends(Provide[{Name}Container.{name}_use_case]),
) -> SuccessResponse[{Name}Response]:
    data = await {name}_use_case.create_data(entity=item)
    return SuccessResponse(data={Name}Response(**data.model_dump(exclude={...})))
```

## §10. Exception 패턴

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

## §11. Event 패턴

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
