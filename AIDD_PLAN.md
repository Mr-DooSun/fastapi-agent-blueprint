# AIDD 아키텍처 재설계 — 종합 레퍼런스

> **목적**: 다른 디바이스에서 이 파일 하나만 보고 Claude에게 요청해서 작업을 이어갈 수 있도록 모든 맥락, 개념, 실행 계획을 담은 문서

---

## 1. 프로젝트 개요

- **경로**: `/Users/coursemos/develop/fastapi-layered-architecture`
- **브랜치**: `feature/56-add_taskiq`
- **스택**: Python 3.12.9+, FastAPI 0.115+, Pydantic 2.10+, SQLAlchemy 2.0+, dependency-injector 4.46+, Taskiq, aioboto3, sqladmin
- **현재 상태**: 아키텍처 재설계 작업 진행 중 (Phase 1 일부 완료)

---

## 2. 아키텍처 이름 및 개념

### 아키텍처 유형: **DDD 기반 모듈형 레이어드 아키텍처**

헥사고날 아키텍처가 아님. 레이어를 유지하되 도메인(기능) 단위로 모듈화한 구조.

```
전통적 레이어드          모듈형 레이어드 (현재)
───────────────          ──────────────────────
controllers/             src/user/           ← 도메인별 모듈
services/           →       domain/
repositories/               application/
models/                     infrastructure/
                            interface/
```

### 4계층 구조

```
┌─────────────────────────────────────────────┐
│ INTERFACE LAYER                             │
│ server/ (FastAPI), admin/ (SQLAdmin),       │
│ worker/ (Taskiq)                            │
├─────────────────────────────────────────────┤
│ APPLICATION LAYER                           │
│ use_cases/ (비즈니스 흐름 조율)              │
├─────────────────────────────────────────────┤
│ DOMAIN LAYER                                │
│ dtos/ (데이터 계약), services/ (비즈니스 로직)│
├─────────────────────────────────────────────┤
│ INFRASTRUCTURE LAYER                        │
│ database/models/, repositories/, di/        │
└─────────────────────────────────────────────┘

의존성 방향: Interface → Application → Domain ← Infrastructure
```

---

## 3. 핵심 설계 결정: Entity 제거 → DTO + Model 단순화

### 왜 Entity를 제거하는가?

현재 프로젝트의 Entity는 **Model(SQLAlchemy)의 Pydantic 복사본**에 불과하다.

```python
# UserModel (SQLAlchemy) — DB 컬럼
class UserModel(Base):
    id, username, full_name, email, password, created_at, updated_at

# UserEntity (Pydantic) — 완전히 동일한 필드
class UserEntity(Entity):
    id, username, full_name, email, password, created_at, updated_at
```

Entity가 의미 있으려면 다음 중 하나여야 한다:
- 도메인 메서드가 있을 때 (`is_admin()`, `can_edit()` 등)
- DB 구조와 도메인 구조가 다를 때 (`first_name + last_name` → `full_name`)
- 여러 테이블을 집계할 때

현재는 해당 없음 → **오버엔지니어링**. 따라서 제거.

### 새 원칙: DTO + Model 두 계층

| 계층 | 타입 | 역할 |
|---|---|---|
| **DTO** | Pydantic BaseModel | 모든 레이어를 흐르는 데이터. 내부 전달 + API 경계 |
| **API Schema** | Pydantic (BaseResponse 상속) | API 응답 전용. 민감 필드(password) 제외 |
| **Model** | SQLAlchemy DeclarativeBase | DB 영속성 전용. Repository 밖으로 나가지 않음 |

---

## 4. 객체 역할 정의 (엄격한 규칙)

### DTO (Domain DTO)
```
위치:   src/{domain}/domain/dtos/{domain}_dto.py
역할:   모든 레이어(Service, UseCase, Repository)를 흐르는 내부 데이터
규칙:   - 도메인 계층에 위치 (모든 계층에서 import 가능)
        - ABC 없음. 그냥 BaseModel
        - 3종 세트: {Name}DTO / Create{Name}DTO / Update{Name}DTO
        - password 같은 민감 필드 포함 (내부 전달용)
```

```python
# src/user/domain/dtos/user_dto.py
class UserDTO(BaseModel):
    id: int
    username: str
    full_name: str
    email: str
    password: str          # 내부 전달용. API 응답에서는 제외
    created_at: datetime
    updated_at: datetime

class CreateUserDTO(BaseModel):
    username: str
    full_name: str
    email: str
    password: str

class UpdateUserDTO(BaseModel):
    username: str | None = None
    full_name: str | None = None
    email: str | None = None
    password: str | None = None
```

### API Schema (Interface DTO)
```
위치:   src/{domain}/interface/server/dtos/{domain}_dto.py
역할:   API 경계 전용. 외부에 공개할 필드만 선언
규칙:   - DTO를 상속하지 않음 (기존 다중상속 패턴 폐기)
        - 명시적 필드 선언 (password 같은 민감 필드 의도적 제외)
        - BaseRequest / BaseResponse 상속
        - camelCase 직렬화 (ApiConfig 적용)
```

```python
# src/user/interface/server/dtos/user_dto.py
class UserResponse(BaseResponse):
    id: int
    username: str
    full_name: str
    email: str
    # password 없음 — 의도적 제외
    created_at: datetime
    updated_at: datetime

class CreateUserRequest(BaseRequest):
    username: str
    full_name: str
    email: str
    password: str

class UpdateUserRequest(BaseRequest):
    username: str | None = None
    full_name: str | None = None
    email: str | None = None
    password: str | None = None
```

### Model (SQLAlchemy ORM)
```
위치:   src/{domain}/infrastructure/database/models/{domain}_model.py
역할:   DB 테이블 매핑 전용
규칙:   - Repository 레이어 밖으로 절대 나가지 않음
        - Service, UseCase, Interface에서 import 금지
        - 변환: DTO → Model: Model(**dto.model_dump())
                Model → DTO: DTO.model_validate(model, from_attributes=True)
```

---

## 5. 데이터 흐름 (변경 전 vs 변경 후)

### 변경 전 (문제 있는 흐름)
```
CreateUserRequest(BaseRequest, CreateUserEntity)  ← 다중상속!
    ↓ item.to_entity(CreateUserEntity)
CreateUserEntity
    ↓
UseCase → Service → Repository
    ↓ model_validate(from_attributes=True)
UserEntity
    ↓ UserResponse.from_entity(data)  ← from_entity 결합!
UserResponse(BaseResponse, UserEntity)  ← 다중상속!
```

### 변경 후 (깔끔한 흐름)
```
CreateUserRequest(BaseRequest)  ← 명시적 필드만
    ↓ CreateUserDTO(**item.model_dump())
CreateUserDTO
    ↓
UseCase → Service → Repository
    ↓ UserDTO.model_validate(model, from_attributes=True)
UserDTO
    ↓ UserResponse(**user_dto.model_dump(exclude={'password'}))
UserResponse(BaseResponse)  ← 명시적 필드만
```

**핵심 변화**: Mapper 클래스 없음. 인라인 변환으로 충분.

---

## 6. Protocol(인터페이스) 개념

### Protocol이란?

다른 언어의 **인터페이스(Interface)** 와 동일한 개념. Python이 늦게 도입(3.8+)하면서 이름을 `Protocol`로 붙임.

```
Java/C#:      interface IRepository { void Save(); }
Go:           type Repository interface { Save() }
TypeScript:   interface Repository { save(): void }
Python:       class RepositoryProtocol(Protocol): def save(self): ...
백엔드 용어:   그냥 "인터페이스"
DDD 용어:     "Repository Interface" 또는 "Port"
```

### ABC vs Protocol 차이

| | ABC | Protocol |
|---|---|---|
| 방식 | 명시적 상속 필요 | 상속 없이 메서드 시그니처만 맞으면 통과 |
| 기존 코드 수정 | 필요 | 불필요 |
| 주 용도 | 공통 구현 상속 | 타입 계약 (인터페이스) |
| 테스트 Mock | 상속 필요 | 아무 클래스나 메서드만 맞으면 OK |

### 현재 BaseRepository는?

`BaseRepository`는 "Protocol + 기본 구현"이 합쳐진 것. Protocol이라기보다 **공통 구현을 제공하는 추상 기반 클래스**.

```python
# BaseRepository = ABC + 실제 SQL 구현 코드
class BaseRepository(Generic[...], ABC):
    async def insert_data(self, ...):
        async with self.database.session() as session:  # 실제 구현 있음
            ...

# BaseRepositoryProtocol = 순수 계약만 (인터페이스)
class BaseRepositoryProtocol(Protocol[...]):
    async def insert_data(self, ...): ...  # 시그니처만
```

### 왜 Protocol을 추가하는가?

```python
# ❌ 현재 문제: Domain이 Infrastructure를 직접 import → 계층 위반
# src/_core/domain/services/base_service.py
from src._core.infrastructure.database.base_repository import BaseRepository  # 위반!

# ✅ 해결: Domain은 Protocol(도메인 내부)만 알면 됨
# src/_core/domain/services/base_service.py
from src._core.domain.protocols.repository_protocol import BaseRepositoryProtocol  # OK

class BaseService:
    def __init__(self, base_repository: BaseRepositoryProtocol):  # 인터페이스만
        self.base_repository = base_repository  # 실제론 BaseRepository 주입됨 (DI)
```

**실제 이점**: 테스트 시 DB 없이 Mock 주입 가능

```python
# 테스트용 Mock — BaseRepositoryProtocol을 상속하지 않아도 됨
class MockUserRepository:
    async def insert_data(self, dto: CreateUserDTO) -> UserDTO:
        return UserDTO(id=1, **dto.model_dump(), ...)

# DB 없이 순수 Python으로 Service 테스트
service = UserService(user_repository=MockUserRepository())  # ✅
```

---

## 7. 현재 디렉토리 구조 (변경 전)

```
src/
├── _core/
│   ├── application/
│   │   ├── dtos/
│   │   │   ├── base_config.py      # ApiConfig (camelCase 설정)
│   │   │   ├── base_request.py     # BaseRequest + to_entity() ← 제거 예정
│   │   │   └── base_response.py    # BaseResponse + from_entity() ← 제거 예정
│   │   ├── routers/api/
│   │   │   ├── health_check_router.py
│   │   │   └── docs_router.py
│   │   └── use_cases/
│   │       └── base_use_case.py    # BaseUseCase[CreateEntity, ReturnEntity, UpdateEntity]
│   ├── domain/
│   │   ├── entities/
│   │   │   └── entity.py           # Entity(ABC, BaseModel) ← 제거 예정
│   │   └── services/
│   │       └── base_service.py     # BaseService — infra import 있음 ← 수정 예정
│   ├── infrastructure/
│   │   ├── database/
│   │   │   ├── database.py
│   │   │   ├── base_repository.py  # BaseRepository (실제 CRUD 구현)
│   │   │   └── config.py
│   │   ├── di/core_container.py
│   │   ├── http/
│   │   ├── storage/
│   │   └── taskiq/
│   ├── middleware/exception_middleware.py
│   ├── exceptions/base_exception.py
│   ├── common/
│   │   ├── pagination.py
│   │   └── dto_utils.py            # dtos_to_entities(), entities_to_dtos() ← 제거 예정
│   └── config.py
│
├── _apps/
│   ├── server/   (FastAPI 앱)
│   ├── worker/   (Taskiq 워커)
│   └── admin/
│
└── user/                           # 도메인 모듈 예시
    ├── domain/
    │   ├── entities/
    │   │   └── user_entity.py      # UserEntity, CreateUserEntity, UpdateUserEntity ← 제거
    │   └── services/
    │       └── user_service.py
    ├── application/
    │   └── use_cases/
    │       └── user_use_case.py
    ├── infrastructure/
    │   ├── database/models/user_model.py
    │   ├── repositories/user_repository.py
    │   └── di/user_container.py
    └── interface/
        ├── server/
        │   ├── routers/user_router.py
        │   ├── dtos/user_dto.py    # UserResponse(BaseResponse, UserEntity) ← 수정
        │   └── bootstrap/
        ├── admin/views/user_view.py
        └── worker/tasks/user_test_task.py
```

---

## 8. 목표 디렉토리 구조 (변경 후)

```
src/
├── _core/
│   ├── application/
│   │   ├── dtos/
│   │   │   ├── base_config.py      # 유지
│   │   │   ├── base_request.py     # to_entity() 제거 후 순수 ApiConfig 상속만
│   │   │   └── base_response.py    # from_entity() 제거 후 순수 ApiConfig 상속만
│   │   ├── routers/api/            # 유지
│   │   └── use_cases/
│   │       └── base_use_case.py    # TypeVar bound: Entity → BaseModel
│   ├── domain/
│   │   ├── entities/               # 삭제
│   │   ├── protocols/              # NEW: 인터페이스 정의
│   │   │   └── repository_protocol.py  # BaseRepositoryProtocol(Protocol)
│   │   ├── value_objects/          # NEW: 불변 값 객체 베이스
│   │   │   └── value_object.py
│   │   ├── events/                 # NEW: 도메인 이벤트 베이스
│   │   │   └── domain_event.py
│   │   └── services/
│   │       └── base_service.py     # Protocol import로 변경
│   ├── infrastructure/             # 유지 (변경 없음)
│   ├── middleware/                 # 유지
│   ├── exceptions/                 # 유지
│   ├── common/
│   │   ├── pagination.py           # 유지
│   │   └── dto_utils.py            # 삭제 (더 이상 불필요)
│   └── config.py                   # 유지
│
└── user/
    ├── domain/
    │   ├── dtos/                   # NEW (entities/ 대체)
    │   │   └── user_dto.py         # UserDTO, CreateUserDTO, UpdateUserDTO
    │   ├── protocols/              # NEW
    │   │   └── user_repository_protocol.py
    │   ├── exceptions/             # NEW
    │   │   └── user_exceptions.py
    │   ├── events/                 # NEW
    │   │   └── user_events.py
    │   └── services/
    │       └── user_service.py     # UserRepository → UserRepositoryProtocol
    ├── application/
    │   └── use_cases/
    │       └── user_use_case.py    # Entity → DTO
    ├── infrastructure/
    │   ├── database/models/user_model.py  # 유지
    │   ├── repositories/user_repository.py  # Entity → DTO
    │   └── di/user_container.py    # Entity → DTO
    └── interface/
        ├── server/
        │   ├── routers/user_router.py  # 인라인 변환으로 교체
        │   ├── dtos/user_dto.py    # 다중상속 제거, 명시적 필드
        │   └── bootstrap/
        ├── admin/views/user_view.py    # 유지
        └── worker/tasks/user_test_task.py  # 유지

tests/                              # NEW (이미 디렉토리 생성 완료)
├── conftest.py
├── factories/
│   └── user_factory.py
├── unit/user/{domain/, application/}
├── integration/user/infrastructure/
└── e2e/user/
```

---

## 9. 실행 계획 (단계별)

> ⚠️ Phase 1 일부 작업 완료됨 (아래 ✅ 표시)

### Phase 1: 기반 정리

| 단계 | 작업 | 상태 |
|---|---|---|
| 1.1 | `src/_core/domain/protocols/repository_protocol.py` 생성 | ✅ 완료 |
| 1.2 | `src/_core/domain/value_objects/value_object.py` 생성 | ✅ 완료 |
| 1.3 | `src/_core/domain/events/domain_event.py` 생성 | ✅ 완료 |
| 1.4 | `src/_core/application/mappers/` 삭제 (Mapper 불필요 결정) | ⏳ 미완료 |
| 1.5 | `src/user/application/mappers/` 삭제 | ⏳ 미완료 |
| 1.6 | `tests/` 디렉토리 구조 생성 | ✅ 완료 |
| 1.7 | `tests/conftest.py` 생성 | ✅ 완료 |
| 1.8 | `tests/factories/user_factory.py` 생성 | ✅ 완료 (Entity 이름으로 생성됨, DTO로 수정 필요) |
| 1.9 | `pyproject.toml` dev 의존성 추가 (pytest, pytest-asyncio, aiosqlite) | ✅ 완료 |

### Phase 2: Base 클래스 정리

| 단계 | 파일 | 변경 내용 |
|---|---|---|
| 2.1 | `src/_core/domain/entities/entity.py` | **삭제** |
| 2.2 | `src/_core/application/dtos/base_request.py` | `to_entity()` 메서드 및 Entity import 제거 |
| 2.3 | `src/_core/application/dtos/base_response.py` | `from_entity()` 메서드 및 Entity import 제거 |
| 2.4 | `src/_core/common/dto_utils.py` | **삭제** (`dtos_to_entities`, `entities_to_dtos` 불필요) |
| 2.5 | `src/_core/infrastructure/database/base_repository.py` | TypeVar bound `Entity` → `BaseModel` |
| 2.6 | `src/_core/domain/services/base_service.py` | `BaseRepository` import → `BaseRepositoryProtocol` import |
| 2.7 | `src/_core/application/use_cases/base_use_case.py` | TypeVar bound `Entity` → `BaseModel` |

### Phase 3: Domain DTO 구축 (Entity 대체)

| 단계 | 파일 | 변경 내용 |
|---|---|---|
| 3.1 | `src/user/domain/dtos/__init__.py` | **신규 생성** |
| 3.2 | `src/user/domain/dtos/user_dto.py` | **신규 생성** — UserDTO, CreateUserDTO, UpdateUserDTO |
| 3.3 | `src/user/domain/entities/` | **디렉토리 삭제** |

### Phase 4: 연결 계층 수정

| 단계 | 파일 | 변경 내용 |
|---|---|---|
| 4.1 | `src/user/infrastructure/repositories/user_repository.py` | Entity → DTO |
| 4.2 | `src/user/domain/services/user_service.py` | `UserRepository` → `UserRepositoryProtocol` 타입힌트 |
| 4.3 | `src/user/application/use_cases/user_use_case.py` | Entity → DTO |
| 4.4 | `src/user/infrastructure/di/user_container.py` | Entity → DTO |
| 4.5 | `src/user/interface/server/dtos/user_dto.py` | 다중상속 제거, 명시적 필드 선언 |
| 4.6 | `src/user/interface/server/routers/user_router.py` | `to_entity/from_entity` → 인라인 변환 |

### Phase 5: Domain 패턴 추가

| 단계 | 파일 | 변경 내용 |
|---|---|---|
| 5.1 | `src/user/domain/protocols/user_repository_protocol.py` | **신규** — 도메인 레포 계약 |
| 5.2 | `src/user/domain/exceptions/user_exceptions.py` | **신규** — UserNotFoundException 등 |
| 5.3 | `src/user/domain/events/user_events.py` | **신규** — UserCreated, UserUpdated |

### Phase 6: 테스트 작성

| 단계 | 파일 | 내용 |
|---|---|---|
| 6.1 | `tests/factories/user_factory.py` | `make_user_dto()` 등으로 이름 수정 |
| 6.2 | `tests/unit/user/domain/test_user_service.py` | Mock repo로 service 단위 테스트 |
| 6.3 | `tests/unit/user/application/test_user_use_case.py` | Mock service로 use case 단위 테스트 |
| 6.4 | `tests/integration/user/infrastructure/test_user_repository.py` | 실제 DB CRUD 테스트 |
| 6.5 | `tests/e2e/user/test_user_router.py` | HTTP 엔드포인트 전체 테스트 |

### Phase 7: 문서화

| 단계 | 작업 |
|---|---|
| 7.1 | `skill.md` 삭제 |
| 7.2 | `AIDD.md` 신규 작성 (새 아키텍처 AI 가이드) |

---

## 10. 핵심 코드 변경 예시

### base_request.py (변경 후)
```python
# Before
from src._core.domain.entities.entity import Entity
class BaseRequest(ApiConfig):
    def to_entity(self, entity_cls: type[EntityType]) -> EntityType:
        return entity_cls(**self.model_dump())

# After — Entity 의존성 완전 제거
class BaseRequest(ApiConfig):
    pass
```

### base_response.py (변경 후)
```python
# Before
class BaseResponse(ApiConfig):
    @classmethod
    def from_entity(cls: type[ReturnType], entity: Entity) -> ReturnType:
        return cls(**entity.model_dump())

# After
class BaseResponse(ApiConfig):
    pass
```

### base_service.py (변경 후)
```python
# Before
from src._core.infrastructure.database.base_repository import BaseRepository  # 계층 위반

# After
from src._core.domain.protocols.repository_protocol import BaseRepositoryProtocol

class BaseService(Generic[CreateDTO, ReturnDTO, UpdateDTO], ABC):
    def __init__(
        self,
        base_repository: BaseRepositoryProtocol,  # 인터페이스만 알면 됨
        ...
    ) -> None:
```

### user_router.py (변경 후)
```python
# Before
data = await user_use_case.create_data(entity=item.to_entity(CreateUserEntity))
return SuccessResponse(data=UserResponse.from_entity(data))

# After — 인라인 변환, Mapper 클래스 없음
data = await user_use_case.create_data(dto=CreateUserDTO(**item.model_dump()))
return SuccessResponse(data=UserResponse(**data.model_dump(exclude={'password'})))
```

### user_dto.py — API Schema (변경 후)
```python
# Before — 다중상속 (결합 문제)
class UserResponse(BaseResponse, UserEntity): pass
class CreateUserRequest(BaseRequest, CreateUserEntity): pass

# After — 명시적 필드 선언 (완전 분리)
class UserResponse(BaseResponse):
    id: int
    username: str
    full_name: str
    email: str          # password 제외 — 의도적
    created_at: datetime
    updated_at: datetime

class CreateUserRequest(BaseRequest):
    username: str
    full_name: str
    email: str
    password: str
```

---

## 11. 검증 방법

```bash
# 1. 서버 실행 확인 (회귀 없음)
uvicorn src._apps.server.app:app --reload --host 127.0.0.1 --port 8001
# → http://127.0.0.1:8001/docs 에서 /user 엔드포인트 전체 테스트

# 2. Entity import 완전 제거 확인
grep -r "from src._core.domain.entities" src/
# → 결과 없어야 함

# 3. Domain의 Infrastructure import 확인
grep -r "from src._core.infrastructure" src/_core/domain/
# → 결과 없어야 함

# 4. 전체 테스트 실행
pytest tests/ -v

# 5. Taskiq 워커 실행 확인
python run_worker_local.py --env local
```

---

## 12. AI에게 요청할 때 이 파일 활용법

다른 디바이스에서 Claude에게 아래와 같이 요청하세요:

```
이 프로젝트(/Users/coursemos/develop/fastapi-layered-architecture)의
아키텍처 재설계 작업을 이어서 진행해줘.

관련 레퍼런스 문서가 다음 위치에 있어:
~/.claude/plans/squishy-frolicking-music.md

이 문서를 먼저 읽고, 현재 완료된 작업과 남은 작업을 파악한 다음
Phase 1의 미완료 항목부터 순서대로 진행해줘.
```

또는 특정 Phase만:

```
~/.claude/plans/squishy-frolicking-music.md 를 읽고
Phase 2 (Base 클래스 정리) 작업을 진행해줘.
```

---

## 13. 설계 원칙 요약 (Do's and Don'ts)

### ✅ DO
- DTO를 모든 레이어에서 직접 사용
- Model → DTO 변환: `DTO.model_validate(model, from_attributes=True)`
- DTO → Model 변환: `Model(**dto.model_dump())`
- API 응답 민감 필드 제외: `model_dump(exclude={'password'})`
- Protocol을 DIP 도구로 사용 (Domain이 Infrastructure import 안 하도록)

### ❌ DON'T
- DTO가 Entity/DTO를 상속하는 다중상속 패턴 (`class UserResponse(BaseResponse, UserEntity)`)
- `to_entity()`, `from_entity()` 메서드 사용
- Domain 레이어에서 Infrastructure import
- Model 객체를 Repository 밖으로 노출
- Mapper 클래스 별도 생성 (인라인 변환으로 충분)
