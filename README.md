# 🏗️ FastAPI Layered Architecture

[![Python](https://img.shields.io/badge/Python-3.12.9+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-green.svg)](https://fastapi.tiangolo.com)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

> **"반복되는 코드 작성을 멈추고, 비즈니스 로직에만 집중하세요."**

Domain-Driven Design(DDD) 기반의 **제네릭 4계층 아키텍처**로 구현한 FastAPI 엔터프라이즈 백엔드 템플릿입니다.

---

## 📖 목차

- [왜 이 프로젝트를 만들었나?](#-왜-이-프로젝트를-만들었나)
- [핵심 문제와 해결책](#-핵심-문제와-해결책)
- [주요 특징](#-주요-특징)
- [아키텍처 개요](#-아키텍처-개요)
- [빠른 시작](#-빠른-시작)
- [새 도메인 추가하기](#-새-도메인-추가하기)
- [활용 방법 및 모범 사례](#-활용-방법-및-모범-사례)
- [기술 스택](#-기술-스택)
- [프로젝트 구조](#-프로젝트-구조)
- [라이선스](#-라이선스)

---

## 💡 왜 이 프로젝트를 만들었나?

### 문제: FastAPI 프로젝트의 현실

FastAPI는 빠르고 강력한 프레임워크지만, 실제 엔터프라이즈 프로젝트에서는 다음과 같은 문제들이 반복됩니다:

```python
# ❌ 전형적인 FastAPI 코드 - 반복되는 패턴
@app.post("/user")
async def create_user(user: UserCreate):
    try:
        db = get_db()
        new_user = User(**user.dict())
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return {"success": True, "data": new_user}
    except Exception as e:
        db.rollback()
        return {"success": False, "error": str(e)}
    finally:
        db.close()

@app.post("/product")  # 똑같은 패턴 반복!
async def create_product(product: ProductCreate):
    try:
        db = get_db()
        new_product = Product(**product.dict())
        db.add(new_product)
        db.commit()
        db.refresh(new_product)
        return {"success": True, "data": new_product}
    except Exception as e:
        db.rollback()
        return {"success": False, "error": str(e)}
    finally:
        db.close()

# 계속 반복... 😫
```

**이런 문제들이 있었습니다:**

1. **반복되는 CRUD 코드** - 도메인마다 동일한 코드를 100줄씩 작성
2. **일관성 없는 구조** - 팀원마다 다른 스타일로 작성
3. **테스트의 어려움** - 강결합으로 인한 Mock 생성의 어려움
4. **확장성 문제** - 프로젝트가 커질수록 유지보수 비용 폭증
5. **비즈니스 로직과 인프라의 혼재** - 관심사 분리 실패

### 해결책: 제네릭 베이스 클래스 + 계층형 아키텍처

이 프로젝트는 **"한 번만 작성하고, 계속 재사용하자"**는 철학으로 만들어졌습니다.

```python
# ✅ 이 프로젝트의 접근 방식 - 제네릭으로 추상화
class BaseRepository(Generic[CreateEntity, ReturnEntity, UpdateEntity]):
    async def insert_data(self, entity: CreateEntity) -> ReturnEntity:
        # 모든 CRUD 로직이 여기에 한 번만 작성됨
        ...

# 새 도메인 추가는 단 5줄!
class UserRepository(BaseRepository[CreateUserEntity, UserEntity, UpdateUserEntity]):
    def __init__(self, database: Database):
        super().__init__(database=database, model=UserModel, ...)
    # 끝! 모든 CRUD가 자동으로 제공됨
```

---

## 🎯 핵심 문제와 해결책

| 문제 | 일반 FastAPI | 이 프로젝트 (해결책) |
|------|-------------|-------------------|
| **CRUD 반복** | 도메인마다 100줄+ 작성 | 제네릭 베이스 클래스 상속 (5줄) |
| **일관성** | 팀원마다 다른 스타일 | 강제된 계층 구조 |
| **테스트** | Mock 생성 어려움 | 의존성 주입으로 쉬운 Mock |
| **확장성** | 스파게티 코드 | 도메인 독립성 보장 |
| **유지보수** | 수정 시 전체 영향 | 계층 분리로 영향 최소화 |
| **학습 곡선** | 낮음 (빠른 시작) | 높음 (하지만 장기적 이득) |

---

## ✨ 주요 특징

### 1️⃣ **제네릭 베이스 클래스 시스템** (핵심!)

3계층 제네릭으로 **모든 CRUD를 자동화**:

```python
BaseRepository[CreateEntity, ReturnEntity, UpdateEntity]
    ↓ 사용
BaseService[CreateEntity, ReturnEntity, UpdateEntity]
    ↓ 사용
BaseUseCase[CreateEntity, ReturnEntity, UpdateEntity]
```

**새 도메인 추가 비용**:
- 일반 FastAPI: **100+ 줄** (CRUD, 예외처리, 페이지네이션 등)
- 이 프로젝트: **~45줄** (Entity, Repository, Service, UseCase, Router)

**자동 제공되는 메서드**:
- ✅ `create_data` - 단일 생성
- ✅ `create_datas` - 복수 생성
- ✅ `get_datas` - 페이지네이션 조회
- ✅ `get_data_by_data_id` - ID 조회
- ✅ `get_datas_by_data_ids` - 복수 ID 조회
- ✅ `update_data_by_data_id` - 수정
- ✅ `delete_data_by_data_id` - 삭제

### 2️⃣ **DDD 기반 4계층 아키텍처**

```
┌─────────────────────────────────────────────────┐
│  Interface Layer (REST API, Admin, Consumer)    │  ← 외부와의 접점
├─────────────────────────────────────────────────┤
│  Application Layer (UseCase - 조율)             │  ← 비즈니스 흐름
├─────────────────────────────────────────────────┤
│  Domain Layer (Entity + Service - 핵심 로직)    │  ← 비즈니스 규칙
├─────────────────────────────────────────────────┤
│  Infrastructure Layer (Repository, DB, HTTP)    │  ← 기술 구현
└─────────────────────────────────────────────────┘

의존성 방향: Interface → Application → Domain ← Infrastructure
                                        ↑
                                   (의존성 역전)
```

**계층별 책임**:
- **Interface**: REST API 라우터, DTO 변환, Admin 뷰, Celery Consumer
- **Application**: UseCase (여러 Service 조율), 페이지네이션 처리
- **Domain**: Entity (Pydantic), Service (비즈니스 로직)
- **Infrastructure**: Repository (데이터 액세스), Database, HTTP Client, Storage

### 3️⃣ **의존성 주입 (DI) 컨테이너**

```python
ServerContainer (통합)
 ├── CoreContainer
 │   ├── Database (MySQL 비동기)
 │   ├── HttpClient (aiohttp 연결 풀)
 │   ├── ObjectStorage (S3/MinIO)
 │   └── CeleryManager (메시징)
 └── UserContainer (도메인별)
     ├── UserRepository
     ├── UserService
     └── UserUseCase
```

**장점**:
- 의존성 자동 해결
- 테스트 시 Mock 교체 용이
- 순환 의존성 방지

### 4️⃣ **모놀리식 ↔ 마이크로서비스 전환**

```bash
# 개발: 모놀리식 (간단한 디버깅)
python run_server_local.py --env local

# 프로덕션: 마이크로서비스 (독립 배포/확장)
python run_microservice.py --env prod
```

**코드 변경 없이** 실행 방식만 변경 가능!

### 5️⃣ **비동기 처리 + 연결 풀 최적화**

- **Database**: aiomysql (비동기) + 연결 풀 (pool_size=10)
- **HTTP Client**: aiohttp + TCPConnector (재사용)
- **Storage**: aioboto3 (비동기 S3/MinIO)

### 6️⃣ **타입 안정성 + 자동 문서화**

- Pydantic 2.10+ 기반 Entity/DTO
- TypeVar를 활용한 제네릭 타입 힌팅
- FastAPI 자동 OpenAPI 문서 (5가지 UI 제공)

---

## 🏗️ 아키텍처 개요

### 데이터 흐름 (Request → Response)

```
HTTP Request (JSON)
    ↓
Router (Interface Layer)
    ↓ DTO → Entity 변환
UseCase (Application Layer)
    ↓ 비즈니스 조율
Service (Domain Layer)
    ↓ 비즈니스 로직
Repository (Infrastructure Layer)
    ↓ SQL 실행
Database (MySQL)
    ↓
SQLAlchemy Model
    ↓ Entity 변환
Service → UseCase → Router
    ↓ Entity → DTO 변환
HTTP Response (JSON)
```

### 예제: User 생성 흐름

```python
# 1. Router (Interface)
@router.post("/user")
@inject
async def create_user(
    item: CreateUserRequest,  # DTO
    user_use_case: UserUseCase = Depends(Provide[UserContainer.user_use_case]),
):
    # 2. DTO → Entity
    entity = item.to_entity(CreateUserEntity)
    
    # 3. UseCase 호출
    data = await user_use_case.create_data(entity=entity)
    
    # 4. Entity → DTO
    return SuccessResponse(data=UserResponse.from_entity(data))

# UseCase → Service → Repository → Database 자동 처리!
```

---

## 🚀 빠른 시작

### 사전 요구사항

- Python 3.12.9+
- MySQL 8.0+
- UV (권장) 또는 pip

### 1️⃣ 프로젝트 클론 및 설치

```bash
# 클론
git clone <repository-url>
cd fastapi-layered-architecture

# 가상환경 생성 (UV 사용)
uv venv --python 3.12.9
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# 의존성 설치
uv pip install -e .
```

### 2️⃣ 환경변수 설정

```bash
# 예제 파일 복사
cp _env/local.env.example _env/local.env

# 환경변수 편집
nano _env/local.env
```

**필수 환경변수**:
```env
ENV=local
DATABASE_USER=root
DATABASE_PASSWORD=password
DATABASE_HOST=localhost
DATABASE_PORT=3306
DATABASE_NAME=fastapi_db
```

### 3️⃣ MySQL 실행 (Docker)

```bash
docker run -d \
  --name mysql \
  -e MYSQL_ROOT_PASSWORD=password \
  -e MYSQL_DATABASE=fastapi_db \
  -p 3306:3306 \
  mysql:8.0
```

### 4️⃣ 데이터베이스 마이그레이션

```bash
alembic upgrade head
```

### 5️⃣ 서버 실행

```bash
python run_server_local.py --env local
```

### 6️⃣ 접속 확인

- **API 문서**: http://localhost:8000/api/docs
- **Swagger UI**: http://localhost:8000/api/docs-swagger
- **ReDoc**: http://localhost:8000/api/docs-redoc
- **SQLAdmin**: http://localhost:8000/api/admin
- **Health Check**: http://localhost:8000/api/health

---

## 📈 새 도메인 추가하기

**Product 도메인을 예로 들어 7단계로 설명합니다.**

### 1단계: Entity 정의 (`src/product/domain/entities/product_entity.py`)

```python
from datetime import datetime
from pydantic import Field
from src._core.domain.entities.entity import Entity

class ProductEntity(Entity):
    id: int = Field(..., description="제품 ID")
    name: str = Field(..., description="제품명")
    price: int = Field(..., description="가격")
    created_at: datetime
    updated_at: datetime

class CreateProductEntity(Entity):
    name: str
    price: int

class UpdateProductEntity(Entity):
    name: str
    price: int
```

### 2단계: SQLAlchemy Model (`src/product/infrastructure/database/models/product_model.py`)

```python
from sqlalchemy import Integer, String, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column
from src._core.infrastructure.database.database import Base

class ProductModel(Base):
    __tablename__ = "product"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    price: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[DateTime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[DateTime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())
```

### 3단계: Repository (`src/product/infrastructure/repositories/product_repository.py`)

```python
from src._core.infrastructure.database.base_repository import BaseRepository
from src._core.infrastructure.database.database import Database
from src.product.domain.entities.product_entity import (
    CreateProductEntity, ProductEntity, UpdateProductEntity
)
from src.product.infrastructure.database.models.product_model import ProductModel

class ProductRepository(
    BaseRepository[CreateProductEntity, ProductEntity, UpdateProductEntity]
):
    def __init__(self, database: Database):
        super().__init__(
            database=database,
            model=ProductModel,
            create_entity=CreateProductEntity,
            return_entity=ProductEntity,
            update_entity=UpdateProductEntity,
        )
    # 추가 메서드가 필요하면 여기에 구현
```

### 4단계: Service (`src/product/domain/services/product_service.py`)

```python
from src._core.domain.services.base_service import BaseService
from src.product.domain.entities.product_entity import (
    CreateProductEntity, ProductEntity, UpdateProductEntity
)
from src.product.infrastructure.repositories.product_repository import ProductRepository

class ProductService(
    BaseService[CreateProductEntity, ProductEntity, UpdateProductEntity]
):
    def __init__(self, product_repository: ProductRepository):
        super().__init__(
            base_repository=product_repository,
            create_entity=CreateProductEntity,
            return_entity=ProductEntity,
            update_entity=UpdateProductEntity,
        )
    # 비즈니스 로직 추가
```

### 5단계: UseCase (`src/product/application/use_cases/product_use_case.py`)

```python
from src._core.application.use_cases.base_use_case import BaseUseCase
from src.product.domain.entities.product_entity import (
    CreateProductEntity, ProductEntity, UpdateProductEntity
)
from src.product.domain.services.product_service import ProductService

class ProductUseCase(
    BaseUseCase[CreateProductEntity, ProductEntity, UpdateProductEntity]
):
    def __init__(self, product_service: ProductService):
        super().__init__(
            base_service=product_service,
            create_entity=CreateProductEntity,
            return_entity=ProductEntity,
            update_entity=UpdateProductEntity,
        )
```

### 6단계: DI Container (`src/product/infrastructure/di/product_container.py`)

```python
from dependency_injector import containers, providers
from src.product.infrastructure.repositories.product_repository import ProductRepository
from src.product.domain.services.product_service import ProductService
from src.product.application.use_cases.product_use_case import ProductUseCase

class ProductContainer(containers.DeclarativeContainer):
    core_container = providers.DependenciesContainer()

    product_repository = providers.Singleton(
        ProductRepository,
        database=core_container.database,
    )

    product_service = providers.Factory(
        ProductService,
        product_repository=product_repository,
    )

    product_use_case = providers.Factory(
        ProductUseCase,
        product_service=product_service,
    )
```

### 7단계: Router + Bootstrap

**Router** (`src/product/interface/server/routers/product_router.py`):
```python
from fastapi import APIRouter, Depends, Query
from dependency_injector.wiring import inject, Provide
from src._core.application.dtos.base_response import SuccessResponse
from src.product.application.use_cases.product_use_case import ProductUseCase
from src.product.infrastructure.di.product_container import ProductContainer

router = APIRouter()

@router.post("/product", response_model=SuccessResponse[ProductResponse])
@inject
async def create_product(
    item: CreateProductRequest,
    use_case: ProductUseCase = Depends(Provide[ProductContainer.product_use_case]),
):
    data = await use_case.create_data(entity=item.to_entity(CreateProductEntity))
    return SuccessResponse(data=ProductResponse.from_entity(data))

# 나머지 CRUD 엔드포인트도 동일한 패턴
```

**ServerContainer에 등록** (`src/_shared/infrastructure/di/server_container.py`):
```python
from src.product.infrastructure.di.product_container import ProductContainer

class ServerContainer(containers.DeclarativeContainer):
    core_container = providers.Container(CoreContainer)
    user_container = providers.Container(UserContainer, core_container=core_container)
    product_container = providers.Container(ProductContainer, core_container=core_container)  # 추가
```

**Bootstrap 등록** (`src/bootstrap.py`):
```python
from src.product.interface.server.bootstrap.product_bootstrap import bootstrap_product_domain

def bootstrap_app(app: FastAPI) -> None:
    # ...
    server_container = ServerContainer()
    bootstrap_user_domain(...)
    bootstrap_product_domain(...)  # 추가
```

### ✅ 완료!

이제 다음 엔드포인트가 자동으로 제공됩니다:
- `POST /api/v1/product` - 생성
- `GET /api/v1/products?page=1&pageSize=10` - 목록 (페이지네이션)
- `GET /api/v1/product/{id}` - 조회
- `PUT /api/v1/product/{id}` - 수정
- `DELETE /api/v1/product/{id}` - 삭제

---

## 📘 활용 방법 및 모범 사례

### 1️⃣ 언제 이 아키텍처를 사용해야 하나?

**✅ 추천하는 경우:**
- 10개 이상의 엔드포인트를 가진 중대형 프로젝트
- 팀 단위 협업 프로젝트 (일관된 코드 스타일 필요)
- 장기 운영 예정인 프로젝트 (유지보수성 중요)
- 도메인이 명확하게 분리되는 프로젝트

**❌ 권장하지 않는 경우:**
- 5개 미만의 간단한 API (Over-engineering)
- 빠른 프로토타입/PoC
- 혼자서 단기간 개발하는 프로젝트

### 2️⃣ BaseRepository 확장하기

**커스텀 쿼리 추가**:
```python
class UserRepository(BaseRepository[...]):
    async def find_by_email(self, email: str) -> UserEntity | None:
        async with self.database.session() as session:
            result = await session.execute(
                select(self.model).filter(self.model.email == email)
            )
            data = result.scalar_one_or_none()
            if not data:
                return None
            return self.return_entity.model_validate(data, from_attributes=True)
```

### 3️⃣ Service에 비즈니스 로직 추가

```python
class UserService(BaseService[...]):
    async def register_user(self, entity: CreateUserEntity) -> UserEntity:
        # 1. 이메일 중복 체크
        existing = await self.base_repository.find_by_email(entity.email)
        if existing:
            raise BaseCustomException(status_code=400, message="Email already exists")
        
        # 2. 비밀번호 해싱
        entity.password = hash_password(entity.password)
        
        # 3. 사용자 생성
        return await self.base_repository.insert_data(entity)
```

### 4️⃣ UseCase에서 여러 Service 조율

```python
class OrderUseCase(BaseUseCase[...]):
    def __init__(
        self,
        order_service: OrderService,
        product_service: ProductService,
        user_service: UserService,
    ):
        super().__init__(base_service=order_service, ...)
        self.product_service = product_service
        self.user_service = user_service
    
    async def create_order(self, entity: CreateOrderEntity) -> OrderEntity:
        # 1. 사용자 존재 확인
        await self.user_service.get_data_by_data_id(entity.user_id)
        
        # 2. 제품 재고 확인
        product = await self.product_service.get_data_by_data_id(entity.product_id)
        if product.stock < entity.quantity:
            raise BaseCustomException(status_code=400, message="Out of stock")
        
        # 3. 주문 생성
        return await self.base_service.create_data(entity)
```

### 5️⃣ 외부 API 호출 (BaseHttpGateway 활용)

```python
class PaymentGateway(BaseHttpGateway):
    def __init__(self, http_client: HttpClient, api_key: str):
        super().__init__(http_client, base_url="https://api.payment.com")
        self.api_key = api_key
    
    def _get_headers(self) -> dict[str, str]:
        return {"Authorization": f"Bearer {self.api_key}"}
    
    async def process_payment(self, amount: int, card_token: str) -> dict:
        return await self._post("/payments", json={
            "amount": amount,
            "card_token": card_token
        })
```

### 6️⃣ 테스트 작성 (Mock 활용)

```python
import pytest
from unittest.mock import AsyncMock

@pytest.mark.asyncio
async def test_create_user():
    # Mock Repository
    mock_repo = AsyncMock(spec=UserRepository)
    mock_repo.insert_data.return_value = UserEntity(id=1, username="test", ...)
    
    # Service 생성 (Mock 주입)
    service = UserService(user_repository=mock_repo)
    
    # 테스트 실행
    result = await service.create_data(CreateUserEntity(...))
    
    # 검증
    assert result.id == 1
    mock_repo.insert_data.assert_called_once()
```

### 7️⃣ 에러 처리

**커스텀 예외 정의**:
```python
class UserNotFoundException(BaseCustomException):
    def __init__(self, user_id: int):
        super().__init__(
            status_code=404,
            message=f"User with ID {user_id} not found",
            error_code="USER_NOT_FOUND",
            details={"user_id": user_id}
        )
```

**ExceptionMiddleware가 자동으로 처리**:
```json
{
  "success": false,
  "message": "User with ID 123 not found",
  "error_code": "USER_NOT_FOUND",
  "error_details": {
    "user_id": 123
  }
}
```

---

## 🔧 기술 스택

### 핵심 프레임워크

| 기술 | 버전 | 용도 |
|------|------|------|
| **FastAPI** | 0.115+ | 고성능 비동기 웹 프레임워크 |
| **Pydantic** | 2.10+ | 데이터 검증 및 설정 관리 |
| **SQLAlchemy** | 2.0+ | 비동기 ORM |
| **Alembic** | 1.15+ | 데이터베이스 마이그레이션 |
| **dependency-injector** | 4.46+ | 의존성 주입 컨테이너 |

### 데이터베이스 & 드라이버

| 기술 | 용도 |
|------|------|
| **MySQL** | 8.0+ 메인 RDBMS |
| **aiomysql** | 비동기 MySQL 드라이버 |
| **PyMySQL** | 동기 MySQL 드라이버 (마이그레이션용) |

### 비동기 & 인프라

| 기술 | 용도 |
|------|------|
| **aiohttp** | 비동기 HTTP 클라이언트 (연결 풀) |
| **aioboto3** | 비동기 S3/MinIO 클라이언트 |
| **Celery** | 비동기 작업 큐 |
| **AWS SQS** | Celery 메시지 브로커 |

### 개발 도구

| 기술 | 용도 |
|------|------|
| **Black** | 코드 포매팅 |
| **isort** | Import 정렬 |
| **Flake8** | 린팅 |
| **pre-commit** | Git hook 자동화 |
| **SQLAdmin** | 데이터베이스 관리 UI |
| **UV** | 빠른 Python 패키지 관리 |

---

## 📁 프로젝트 구조

```
fastapi-layered-architecture/
├── src/
│   ├── _core/                      # 🎯 핵심 공통 인프라
│   │   ├── application/            # Application Layer
│   │   │   ├── dtos/              # BaseRequest, BaseResponse
│   │   │   ├── routers/           # Health Check, Docs
│   │   │   └── use_cases/         # BaseUseCase (Generic)
│   │   ├── domain/                # Domain Layer
│   │   │   ├── entities/          # Entity (Pydantic ABC)
│   │   │   └── services/          # BaseService (Generic)
│   │   ├── infrastructure/        # Infrastructure Layer
│   │   │   ├── database/          # Database, BaseRepository
│   │   │   ├── http/              # HttpClient, BaseHttpGateway
│   │   │   ├── messaging/         # Celery
│   │   │   ├── storage/           # S3/MinIO
│   │   │   └── di/                # CoreContainer (DI)
│   │   ├── middleware/            # ExceptionMiddleware
│   │   ├── exceptions/            # BaseCustomException
│   │   ├── common/                # Pagination, DTO Utils
│   │   └── config.py              # Settings (Pydantic)
│   │
│   ├── _shared/                   # 🔗 공유 컴포넌트
│   │   └── infrastructure/
│   │       └── di/
│   │           └── server_container.py  # 통합 DI Container
│   │
│   ├── user/                      # 👤 User 도메인 (예시)
│   │   ├── domain/
│   │   │   ├── entities/          # UserEntity
│   │   │   └── services/          # UserService
│   │   ├── application/
│   │   │   └── use_cases/         # UserUseCase
│   │   ├── infrastructure/
│   │   │   ├── database/
│   │   │   │   └── models/        # UserModel (SQLAlchemy)
│   │   │   ├── repositories/      # UserRepository
│   │   │   └── di/                # UserContainer (DI)
│   │   ├── interface/
│   │   │   ├── server/            # REST API
│   │   │   │   ├── routers/       # user_router.py
│   │   │   │   ├── dtos/          # user_dto.py
│   │   │   │   └── bootstrap/     # user_bootstrap.py
│   │   │   ├── admin/             # SQLAdmin Views
│   │   │   └── consumer/          # Celery Tasks
│   │   └── app.py                 # User 마이크로서비스 진입점
│   │
│   ├── app.py                     # 🚀 모놀리식 앱 진입점
│   └── bootstrap.py               # 앱 초기화
│
├── migrations/                    # Alembic 마이그레이션
├── _docker/                       # Docker 설정
├── _env/                          # 환경변수 파일
├── config.yml                     # DI 설정
├── pyproject.toml                 # 의존성 관리
├── alembic.ini                    # Alembic 설정
├── docker-compose.yml             # Docker Compose
├── run_server_local.py            # 모놀리식 실행
├── run_microservice.py            # 마이크로서비스 실행
└── LICENSE                        # MIT License
```

---

## 🎓 학습 자료

### 이 프로젝트가 사용하는 디자인 패턴

1. **Layered Architecture (계층형)** - 관심사 분리
2. **Domain-Driven Design (DDD)** - 도메인 중심 설계
3. **Repository Pattern** - 데이터 액세스 추상화
4. **Dependency Injection** - 의존성 역전
5. **Generic Programming** - 코드 재사용성
6. **DTO Pattern** - 계층 간 데이터 전송

### 추천 도서

- **Domain-Driven Design** - Eric Evans
- **Clean Architecture** - Robert C. Martin
- **Implementing Domain-Driven Design** - Vaughn Vernon

---

## 🤝 기여 가이드

### 코딩 규칙

- **Black**: 코드 포매팅 (88자 제한)
- **isort**: Import 정렬
- **Type Hints**: 모든 함수/메서드에 타입 명시
- **Docstring**: 복잡한 로직에 설명 추가

### Commit 메시지 규칙

```
feat: 새로운 기능 추가
fix: 버그 수정
docs: 문서 수정
style: 코드 포맷팅
refactor: 리팩토링
test: 테스트 추가
chore: 빌드/도구 변경
```

### Pre-commit 설정

```bash
# pre-commit 설치
pre-commit install

# 모든 파일에 실행
pre-commit run --all-files
```

---

## ❓ FAQ

### Q1. "보일러플레이트 코드가 너무 많지 않나요?"

**A**: 이것은 **"보일러플레이트를 제거하기 위한 아키텍처 템플릿"**입니다.

- 일반 FastAPI: 도메인마다 100줄+ 반복 작성
- 이 프로젝트: BaseRepository/Service/UseCase를 한 번만 작성하고 재사용

### Q2. "작은 프로젝트에도 적합한가요?"

**A**: 아니요. 5개 미만의 엔드포인트라면 일반 FastAPI가 더 적합합니다.

- 작은 프로젝트: Over-engineering
- 중대형 프로젝트: 생산성 10배 향상

### Q3. "Clean Architecture와 다른 점은?"

**A**: 이 프로젝트는 **Layered Architecture**입니다.

- Clean Architecture: 모든 것을 인터페이스로 추상화 (순수주의)
- Layered Architecture: 실용적인 계층 분리 (이 프로젝트)

### Q4. "마이그레이션 없이 사용할 수 있나요?"

**A**: 네, `alembic upgrade head` 대신 `Base.metadata.create_all()`을 사용하세요.

```python
# 개발 환경에서만 사용
async with database.async_engine.begin() as conn:
    await conn.run_sync(Base.metadata.create_all)
```

---

## 📝 라이선스

이 프로젝트는 [MIT License](LICENSE) 하에 배포됩니다.

```
Copyright (c) 2025 FastAPI Layered Architecture Contributors

상업적 사용, 수정, 배포, 사적 사용이 자유롭습니다.
단, 저작권 표시와 라이선스 고지를 포함해야 합니다.
```

---

## 🙏 감사의 말

이 아키텍처는 다음 원칙들을 기반으로 합니다:

- **SOLID 원칙** (단일 책임, 개방-폐쇄, 리스코프 치환, 인터페이스 분리, 의존성 역전)
- **DDD (Domain-Driven Design)** - Eric Evans
- **Layered Architecture** - 전통적인 엔터프라이즈 패턴
- **Repository Pattern** - Martin Fowler

---

## 📞 문의 및 지원

- **Issues**: GitHub Issues에 버그 리포트 및 기능 제안
- **Discussions**: 아키텍처 관련 질문 및 토론

---

**💡 이 프로젝트는 엔터프라이즈급 FastAPI 애플리케이션을 위한 실용적인 아키텍처 템플릿입니다.**

**비즈니스 로직에 집중하고, 반복적인 인프라 코드는 우리가 제공하는 견고한 기반을 활용하세요.** 🚀
