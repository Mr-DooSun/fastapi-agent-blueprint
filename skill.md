# 🧬 Project DNA: FastAPI Layered Architecture Skill Guide

> **Last Updated**: 2026-01-29  
> **Purpose**: 이 문서는 프로젝트의 기술적 자산, 코드 스타일, 암묵적 규칙을 정의하여 AI 모델이 기존 코드와 일관된 코드를 생성할 수 있도록 합니다.

---

## 📋 Table of Contents

1. [Capabilities (기능적 역량)](#1-capabilities-기능적-역량)
2. [Technical Implementation (구현 상세)](#2-technical-implementation-구현-상세)
3. [Implicit Rules (암묵적 규칙)](#3-implicit-rules-암묵적-규칙)
4. [AI Instructions (AI를 위한 가이드라인)](#4-ai-instructions-ai를-위한-가이드라인)

---

## 1. Capabilities (기능적 역량)

### 1.1 핵심 아키텍처 패턴

#### **제네릭 3계층 베이스 시스템**

프로젝트의 가장 중요한 자산은 **Generic TypeVar 기반 3계층 베이스 클래스**입니다.

```python
# 계층별 제네릭 타입 정의
CreateEntity = TypeVar("CreateEntity", bound=Entity)
ReturnEntity = TypeVar("ReturnEntity", bound=Entity)  
UpdateEntity = TypeVar("UpdateEntity", bound=Entity)

# 3계층 상속 체인
BaseRepository[CreateEntity, ReturnEntity, UpdateEntity]
    ↓ 사용
BaseService[CreateEntity, ReturnEntity, UpdateEntity]
    ↓ 사용
BaseUseCase[CreateEntity, ReturnEntity, UpdateEntity]
```

**제공되는 자동화 메서드**:
- `insert_data(entity)` / `insert_datas(entities)` - 단일/복수 생성
- `select_datas(page, page_size)` - 페이지네이션 조회
- `select_data_by_id(data_id)` - ID 조회
- `select_datas_by_ids(data_ids)` - 복수 ID 조회
- `select_datas_with_count(page, page_size)` - 데이터 + 카운트 (최적화)
- `update_data_by_data_id(data_id, entity)` - 수정
- `delete_data_by_data_id(data_id)` - 삭제
- `count_datas()` - 전체 카운트

#### **DDD 기반 4계층 아키텍처**

```
┌─────────────────────────────────────────────────┐
│  Interface Layer (REST API, Admin, Consumer)    │
│  - Routers: FastAPI 엔드포인트                     │
│  - DTOs: Request/Response 변환                   │
│  - Bootstrap: 도메인별 초기화                       │
├─────────────────────────────────────────────────┤
│  Application Layer (UseCase)                    │
│  - 여러 Service 조율                              │
│  - 페이지네이션 처리 (PaginationInfo 생성)            │
│  - 트랜잭션 경계 정의                                │
├─────────────────────────────────────────────────┤
│  Domain Layer (Entity + Service)                │
│  - Entity: Pydantic 기반 불변 데이터 모델            │
│  - Service: 비즈니스 로직 구현                       │
│  - 인프라 의존성 없음 (순수 비즈니스)                   │
├─────────────────────────────────────────────────┤
│  Infrastructure Layer (Repository, DB, HTTP)    │
│  - Repository: 데이터 액세스 (SQLAlchemy)          │
│  - Database: 비동기 연결 풀 관리                     │
│  - HttpClient: 외부 API 호출                       │
│  - ObjectStorage: S3/MinIO 파일 관리               │
│  - TaskiqManager: 비동기 작업 큐                    │
└─────────────────────────────────────────────────┘

의존성 방향: Interface → Application → Domain ← Infrastructure
```

### 1.2 모듈별 핵심 기능

#### **_core (공통 인프라)**

**Database 모듈**:
- PostgreSQL + asyncpg 비동기 드라이버
- SQLAlchemy 2.0 ORM (Mapped 타입 힌팅)
- 연결 풀 관리 (환경별 설정: dev=5, prod=10)
- Context Manager 기반 세션 관리 (`async with database.session()`)
- 자동 롤백 및 예외 처리 (IntegrityError → DatabaseException)

**HTTP Client 모듈**:
- aiohttp 기반 비동기 HTTP 클라이언트
- TCPConnector 연결 풀 재사용 (환경별: dev=50, prod=100)
- 이벤트 루프 변경 감지 및 세션 재생성
- BaseHttpGateway 추상 클래스 (외부 API 통합용)

**Storage 모듈**:
- aioboto3 기반 비동기 S3/MinIO 클라이언트
- 파일 업로드/다운로드/삭제/존재확인
- Presigned URL 생성 (기본 3600초)

**Exception 시스템**:
- `BaseCustomException`: 모든 커스텀 예외의 부모 (status_code, message, error_code, details)
- `ExceptionMiddleware`: 전역 예외 핸들러 (BaseCustomException → ErrorResponse 자동 변환)

**DTO 시스템**:
- `BaseRequest`: `to_entity(entity_cls)` 메서드로 Entity 변환
- `BaseResponse`: `from_entity(entity)` 클래스 메서드로 Entity → DTO 변환
- `SuccessResponse[T]`: Generic 응답 래퍼 (data, pagination, message)
- `ErrorResponse`: 에러 응답 (message, error_code, error_details)

---

## 2. Technical Implementation (구현 상세)

### 2.1 코드 작성 스타일

#### **타입 힌팅 규칙**

**필수 타입 힌팅**:
```python
# ✅ 모든 함수/메서드 시그니처
async def create_data(self, entity: CreateEntity) -> ReturnEntity:
    ...

# ✅ 클래스 속성
class Database:
    engine: Engine
    async_engine: AsyncEngine
    async_session_factory: sessionmaker

# ✅ Optional/Union 명시
s3_access_key: str | None = Field(default=None)
```

**Generic TypeVar 사용**:
```python
# 계층별 동일한 TypeVar 이름 사용
CreateEntity = TypeVar("CreateEntity", bound=Entity)
ReturnEntity = TypeVar("ReturnEntity", bound=Entity)
UpdateEntity = TypeVar("UpdateEntity", bound=Entity)

# Generic 클래스 정의
class BaseRepository(Generic[CreateEntity, ReturnEntity, UpdateEntity], ABC):
    ...
```

#### **Pydantic 모델 설계**

**Entity (도메인 모델)**:
```python
class Entity(ABC, BaseModel):
    class Config:
        use_enum_values = True  # Enum을 값으로 직렬화
```

**API Config (DTO용)**:
```python
API_CONFIG = ConfigDict(
    extra="ignore",              # 추가 필드 무시
    frozen=True,                 # 불변 객체
    populate_by_name=True,       # 별칭/원래 이름 모두 허용
    loc_by_alias=True,           # 에러 위치를 별칭으로 표시
    alias_generator=to_camel,    # snake_case → camelCase 자동 변환
    ser_json_timedelta="iso8601",
    ser_json_bytes="utf8",
)
```

#### **SQLAlchemy 2.0 스타일**

**Model 정의**:
```python
from sqlalchemy.orm import Mapped, mapped_column

class UserModel(Base):
    __tablename__ = "user"
    
    # Mapped 타입 힌팅 필수
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(20), nullable=False)
    
    # 타임스탬프: server_default 사용
    created_at: Mapped[DateTime] = mapped_column(
        DateTime, server_default=func.now(), nullable=True
    )
    updated_at: Mapped[DateTime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now(), nullable=True
    )
```

**쿼리 패턴**:
```python
# select() 사용 (2.0 스타일)
result = await session.execute(
    select(self.model).filter(self.model.id == data_id)
)
data = result.scalar_one_or_none()

# Entity 변환
return self.return_entity.model_validate(data, from_attributes=True)
```

#### **의존성 주입 패턴**

**Container 정의**:
```python
class UserContainer(containers.DeclarativeContainer):
    core_container = providers.DependenciesContainer()
    
    # Singleton: 인프라 계층 (연결 풀 재사용)
    user_repository = providers.Singleton(
        UserRepository,
        database=core_container.database,
    )
    
    # Factory: 비즈니스 계층 (요청마다 새 인스턴스)
    user_service = providers.Factory(
        UserService,
        user_repository=user_repository,
    )
```

**Router에서 주입**:
```python
@router.post("/user")
@inject  # 데코레이터 필수
async def create_user(
    item: CreateUserRequest,
    user_use_case: UserUseCase = Depends(Provide[UserContainer.user_use_case]),
):
    ...
```

#### **비동기 Context Manager 패턴**

```python
@asynccontextmanager
async def session(self) -> AsyncGenerator[AsyncSession, None]:
    session = None
    try:
        session = self.async_session_factory()
        yield session
    except IntegrityError:
        if session:
            await session.rollback()
        raise DatabaseException(...)
    finally:
        if session:
            await session.close()
```

### 2.2 환경별 설정 전략

**DatabaseConfig**:
```python
@classmethod
def from_env(cls, env: str) -> "DatabaseConfig":
    if env == "prod":
        return cls(echo=False, pool_size=10, max_overflow=20, ...)
    return cls(echo=True, pool_size=5, max_overflow=10, ...)
```

### 2.3 코드 품질 도구

**Pre-commit Hooks (자동 실행)**:
1. `pyupgrade` - Python 3.12+ 구문 현대화
2. `autoflake` - 미사용 import/변수 제거
3. `isort` - Import 정렬 (black profile)
4. `black` - 코드 포매팅 (88자)
5. `flake8` - 린팅

**수동 실행 도구**:
- `mypy` - 타입 체킹
- `bandit` - 보안 체크

---

## 3. Implicit Rules (암묵적 규칙)

### 3.1 파일 및 디렉토리 네이밍

#### **도메인 모듈 구조**

```
{domain}/
├── domain/
│   ├── entities/{domain}_entity.py
│   └── services/{domain}_service.py
├── application/
│   └── use_cases/{domain}_use_case.py
├── infrastructure/
│   ├── database/models/{domain}_model.py
│   ├── repositories/{domain}_repository.py
│   └── di/{domain}_container.py
└── interface/
    └── server/
        ├── routers/{domain}_router.py
        ├── dtos/{domain}_dto.py
        └── bootstrap/{domain}_bootstrap.py
```

#### **파일 네이밍 패턴**

- Entity: `{domain}_entity.py` → `UserEntity`, `CreateUserEntity`, `UpdateUserEntity`
- Repository: `{domain}_repository.py` → `UserRepository`
- Service: `{domain}_service.py` → `UserService`
- UseCase: `{domain}_use_case.py` → `UserUseCase`
- Router: `{domain}_router.py` → `router = APIRouter()`
- DTO: `{domain}_dto.py` → `UserResponse`, `CreateUserRequest`
- Model: `{domain}_model.py` → `UserModel`, `__tablename__ = "user"`

### 3.2 클래스 및 메서드 네이밍

#### **CRUD 메서드 (일관된 네이밍)**

- Repository: `insert_data`, `select_data_by_id`, `update_data_by_data_id`, `delete_data_by_data_id`
- Service: `create_data`, `get_data_by_data_id`, `update_data_by_data_id`, `delete_data_by_data_id`
- UseCase: 동일

**복수형 메서드**: `insert_datas`, `select_datas`, `select_datas_by_ids`

### 3.3 Import 순서 규칙

```python
# 1. 표준 라이브러리
from abc import ABC
from typing import Generic, TypeVar

# 2. 외부 라이브러리
from fastapi import APIRouter, Depends
from pydantic import Field
from sqlalchemy import Integer, String

# 3. 로컬 모듈 (절대 경로)
from src._core.domain.entities.entity import Entity
from src.user.domain.entities.user_entity import UserEntity
```

**절대 경로 사용**:
- ✅ `from src._core.domain.entities.entity import Entity`
- ❌ `from ...domain.entities.entity import Entity` (상대 경로 금지)

### 3.4 Router 및 API 설계 규칙

**Endpoint 네이밍**:
- 단일 리소스: `/user/{user_id}` (GET, PUT, DELETE)
- 복수 리소스: `/users` (GET, POST)

**Response Model 설정**:
```python
@router.post(
    "/user",
    response_model=SuccessResponse[UserResponse],
    response_model_exclude={"pagination"},  # pagination 필드 제외
)
```

---

## 4. AI Instructions (AI를 위한 가이드라인)

### 4.1 새 도메인 추가 체크리스트

#### **Step 1-3: Entity, Model, Repository**

```python
# 1. Entity 정의
class UserEntity(Entity):
    id: int = Field(..., description="유저 고유 식별자")
    username: str
    created_at: datetime
    updated_at: datetime

class CreateUserEntity(Entity):
    username: str  # id, timestamp 제외

class UpdateUserEntity(Entity):
    username: str  # id, timestamp 제외

# 2. SQLAlchemy Model
class UserModel(Base):
    __tablename__ = "user"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(20), nullable=False)

# 3. Repository
class UserRepository(BaseRepository[CreateUserEntity, UserEntity, UpdateUserEntity]):
    def __init__(self, database: Database) -> None:
        super().__init__(
            database=database,
            model=UserModel,
            create_entity=CreateUserEntity,
            return_entity=UserEntity,
            update_entity=UpdateUserEntity,
        )
```

#### **Step 4-6: Service, UseCase, DTO**

```python
# 4. Service
class UserService(BaseService[CreateUserEntity, UserEntity, UpdateUserEntity]):
    def __init__(self, user_repository: UserRepository) -> None:
        super().__init__(
            base_repository=user_repository,
            create_entity=CreateUserEntity,
            return_entity=UserEntity,
            update_entity=UpdateUserEntity,
        )

# 5. UseCase
class UserUseCase(BaseUseCase[CreateUserEntity, UserEntity, UpdateUserEntity]):
    def __init__(self, user_service: UserService) -> None:
        super().__init__(
            base_service=user_service,
            create_entity=CreateUserEntity,
            return_entity=UserEntity,
            update_entity=UpdateUserEntity,
        )

# 6. DTO
class UserResponse(BaseResponse, UserEntity):
    pass

class CreateUserRequest(BaseRequest, CreateUserEntity):
    pass
```

#### **Step 7-9: Router, Container, Bootstrap**

```python
# 7. Router
router = APIRouter()

@router.post("/user", response_model=SuccessResponse[UserResponse])
@inject
async def create_user(
    item: CreateUserRequest,
    user_use_case: UserUseCase = Depends(Provide[UserContainer.user_use_case]),
):
    data = await user_use_case.create_data(entity=item.to_entity(CreateUserEntity))
    return SuccessResponse(data=UserResponse.from_entity(data))

# 8. Container
class UserContainer(containers.DeclarativeContainer):
    core_container = providers.DependenciesContainer()
    user_repository = providers.Singleton(UserRepository, database=core_container.database)
    user_service = providers.Factory(UserService, user_repository=user_repository)
    user_use_case = providers.Factory(UserUseCase, user_service=user_service)

# 9. Bootstrap
def bootstrap_user_domain(app: FastAPI, database: Database, user_container: UserContainer):
    user_container.wire(packages=["src.user.interface.server.routers"])
    app.include_router(router=user_router.router, prefix="/v1", tags=["사용자"])
```

### 4.2 코드 수정 시 주의사항

#### **❌ 절대 하지 말아야 할 것**

1. **Base 클래스 수정 금지** - `BaseRepository`, `BaseService`, `BaseUseCase`는 모든 도메인이 의존
2. **상대 경로 import 금지** - 항상 절대 경로 사용
3. **TypeVar 이름 변경 금지** - 항상 `CreateEntity`, `ReturnEntity`, `UpdateEntity`
4. **Generic 타입 순서 변경 금지** - 항상 `[CreateEntity, ReturnEntity, UpdateEntity]`

#### **✅ 권장 사항**

1. **커스텀 메서드는 하위 클래스에 추가**
2. **비즈니스 로직은 Service에 추가**
3. **여러 Service 조율은 UseCase에 추가**
4. **환경별 설정은 `from_env` 패턴 사용**

### 4.3 성능 최적화 가이드

**연결 풀 최적화**:
- Database: 환경별 pool_size 조정 (dev=5, prod=10)
- HTTP Client: 환경별 limit 조정 (dev=50, prod=100)

**쿼리 최적화**:
```python
async def select_datas_with_count(self, page: int, page_size: int):
    """데이터 조회와 카운트를 하나의 세션에서 처리"""
    async with self.database.session() as session:
        result = await session.execute(...)
        count_result = await session.execute(...)
        return datas, total_count
```

---

## 📚 Quick Reference

### **기술 스택**
- Python 3.12.9+
- FastAPI 0.115+
- Pydantic 2.10+
- SQLAlchemy 2.0+ (asyncpg)
- dependency-injector
- aiohttp, aioboto3, taskiq

### **핵심 원칙**
1. 모든 비즈니스 로직은 `async def`
2. TypeVar 기반 Generic 프로그래밍
3. 절대 경로 import만 사용
4. Context Manager 패턴 (`async with`)
5. DTO ↔ Entity 명확한 변환 (`to_entity`, `from_entity`)

---

**End of Document**
