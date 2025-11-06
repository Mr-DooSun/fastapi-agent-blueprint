# 🏗️ FastAPI Enterprise Layered Architecture

[![Python](https://img.shields.io/badge/Python-3.12.9+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-green.svg)](https://fastapi.tiangolo.com)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

## 📋 개요

**엔터프라이즈급 범용 백엔드 아키텍처 템플릿**

이 프로젝트는 **Domain-Driven Design (DDD)**, **Clean Architecture**, **Layered Architecture** 원칙을 완벽하게 구현한 **FastAPI 기반 엔터프라이즈 백엔드 아키텍처**입니다. 

확장성, 유지보수성, 테스트 용이성을 최우선으로 설계되었으며, **제네릭 베이스 클래스**와 **의존성 주입 패턴**을 통해 반복적인 코드 작성을 최소화하고 일관된 코드베이스를 유지할 수 있도록 설계되었습니다.

### 🎯 핵심 설계 철학

**"비즈니스 로직에 집중하라. 인프라는 우리가 처리한다."**

1. **제네릭 베이스 클래스**: 모든 CRUD 작업을 위한 재사용 가능한 기반 제공
2. **완전한 계층 분리**: Domain ↔ Application ↔ Infrastructure ↔ Interface
3. **의존성 역전**: 도메인이 인프라에 의존하지 않는 구조
4. **타입 안정성**: Pydantic과 TypeVar를 활용한 강력한 타입 힌팅
5. **모놀리식 ↔ 마이크로서비스**: 단일 실행 또는 독립 서비스로 유연하게 전환

## 🏗️ 아키텍처 설계

### 4계층 아키텍처 (Layered Architecture)

본 프로젝트는 **DDD의 4계층 구조**를 엄격하게 준수합니다:

```
┌──────────────────────────────────────────────────────────────────┐
│                  Interface Layer (Adapters)                      │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐  ┌────────────┐  │
│  │   Router   │  │   Admin    │  │  Consumer  │  │ Bootstrap  │  │
│  │  (REST)    │  │ (SQLAdmin) │  │  (Celery)  │  │   (Wire)   │  │
│  └────────────┘  └────────────┘  └────────────┘  └────────────┘  │
└────────────────────────┬─────────────────────────────────────────┘
                         │ DTO (Request/Response)
┌────────────────────────┴─────────────────────────────────────────┐
│                     Application Layer                            │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐  ┌────────────┐  │
│  │  UseCase   │  │    DTO     │  │ Messaging  │  │   Router   │  │
│  │ (Orchestr) │  │ (Transfer) │  │  (Celery)  │  │  (Common)  │  │
│  └────────────┘  └────────────┘  └────────────┘  └────────────┘  │
└────────────────────────┬─────────────────────────────────────────┘
                         │ Entity
┌────────────────────────┴─────────────────────────────────────────┐
│                      Domain Layer                                │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐  ┌────────────┐  │
│  │   Entity   │  │  Service   │  │    Enum    │  │ Exception  │  │
│  │ (Pydantic) │  │ (Business) │  │ (Constants)│  │  (Custom)  │  │
│  └────────────┘  └────────────┘  └────────────┘  └────────────┘  │
└────────────────────────┬─────────────────────────────────────────┘
                         │ Entity
┌────────────────────────┴─────────────────────────────────────────┐
│                   Infrastructure Layer                           │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐  ┌────────────┐  │
│  │ Repository │  │  Database  │  │    HTTP    │  │  Gateway   │  │
│  │   (CRUD)   │  │   (MySQL)  │  │  (aiohttp) │  │ (External) │  │
│  └────────────┘  └────────────┘  └────────────┘  └────────────┘  │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐                  │
│  │  Storage   │  │  Messaging │  │     DI     │                  │
│  │(MinIO/S3)  │  │  (Celery)  │  │ (Container)│                  │
│  └────────────┘  └────────────┘  └────────────┘                  │
└──────────────────────────────────────────────────────────────────┘
```

### 데이터 흐름과 의존성 방향

**요청 흐름 (Request Flow)**
```
HTTP Request 
    → Router (Interface)
        → UseCase (Application) 
            → Service (Domain)
                → Repository (Infrastructure)
                    → Database/External API
```

**응답 흐름 (Response Flow)**
```
Database Model 
    → Entity (Domain)
        → DTO (Application)
            → JSON Response (Interface)
```

**의존성 방향 (Dependency Direction)**: **내부로만 향함 (의존성 역전 원칙)**
```
Interface → Application → Domain ← Infrastructure
```

> **핵심**: Domain Layer는 어떤 외부 계층에도 의존하지 않습니다. Infrastructure는 Domain의 인터페이스를 구현합니다.

## 📁 프로젝트 구조

### 전체 디렉토리 구조

```
fastapi-layered-architecture/
├── src/
│   ├── _core/                    # 🎯 핵심 인프라 (모든 도메인이 공유)
│   │   ├── application/          # Application Layer
│   │   │   ├── dtos/            # DTO 베이스 클래스
│   │   │   │   ├── base_request.py   # BaseRequest
│   │   │   │   └── base_response.py  # SuccessResponse, ErrorResponse
│   │   │   ├── routers/         # 공통 라우터
│   │   │   │   └── api/
│   │   │   │       ├── health_check_router.py
│   │   │   │       └── docs_router.py  # 다중 문서 UI
│   │   │   └── use_cases/
│   │   │       └── base_use_case.py  # Generic CRUD UseCase
│   │   ├── domain/              # Domain Layer
│   │   │   ├── entities/
│   │   │   │   └── entity.py    # Entity 베이스 (Pydantic ABC)
│   │   │   └── services/
│   │   │       ├── base_service.py    # Generic CRUD Service
│   │   │       ├── minio_service.py   # MinIO 스토리지
│   │   │       └── s3_service.py      # AWS S3 스토리지
│   │   ├── infrastructure/      # Infrastructure Layer
│   │   │   ├── database/
│   │   │   │   └── database.py  # DB 연결/세션 관리 (aiomysql)
│   │   │   ├── http/
│   │   │   │   └── http_client.py  # HTTP 연결 풀 (aiohttp)
│   │   │   ├── messaging/
│   │   │   │   ├── celery_factory.py   # Celery 앱 생성
│   │   │   │   └── celery_manager.py   # Task 관리
│   │   │   ├── repositories/
│   │   │   │   └── base_repository.py  # Generic CRUD Repository
│   │   │   ├── gateways/
│   │   │   │   └── example_gateway.py  # 외부 API Gateway 예시
│   │   │   └── di/
│   │   │       └── core_container.py   # Core DI Container
│   │   ├── middleware/
│   │   │   └── exception_middleware.py  # 전역 예외 처리
│   │   ├── exceptions/
│   │   │   └── base_exception.py       # 커스텀 예외
│   │   ├── common/             # 유틸리티
│   │   │   ├── pagination.py
│   │   │   └── dto_utils.py
│   │   └── config.py          # 설정 관리 (Pydantic Settings)
│   │
│   ├── _shared/                 # 🔗 공유 컴포넌트
│   │   └── infrastructure/
│   │       └── di/
│   │           └── server_container.py  # 통합 DI Container
│   │
│   ├── user/                    # 👤 User 도메인 (완전한 구현 예시)
│   │   ├── domain/
│   │   │   ├── entities/
│   │   │   │   └── user_entity.py      # User Entity
│   │   │   └── services/
│   │   │       └── user_service.py     # User Service
│   │   ├── application/
│   │   │   └── use_cases/
│   │   │       └── user_use_case.py    # User UseCase
│   │   ├── infrastructure/
│   │   │   ├── database/
│   │   │   │   └── models/
│   │   │   │       └── user_model.py   # SQLAlchemy Model
│   │   │   ├── repositories/
│   │   │   │   └── user_repository.py  # User Repository
│   │   │   └── di/
│   │   │       └── user_container.py    # User DI Container
│   │   ├── interface/          # Interface Layer (Adapters)
│   │   │   ├── server/         # REST Server
│   │   │   │   ├── routers/
│   │   │   │   │   └── user_router.py
│   │   │   │   ├── dtos/
│   │   │   │   │   └── user_dto.py  # Request/Response DTO
│   │   │   │   └── bootstrap/
│   │   │   │       └── user_bootstrap.py
│   │   │   ├── admin/          # SQLAdmin Views
│   │   │   │   └── views/
│   │   │   │       └── user_view.py
│   │   │   └── consumer/       # Celery Consumers
│   │   │       └── tasks/
│   │   └── app.py              # User 마이크로서비스 진입점
│   │
│   ├── app.py                   # 🚀 모놀리식 앱 진입점
│   └── bootstrap.py             # 앱 초기화 및 설정
│
├── migrations/                  # Alembic DB 마이그레이션
│   ├── env.py
│   └── versions/
├── _docker/                     # Docker 설정
│   └── docker.Dockerfile
├── _env/                        # 환경 변수 파일
│   ├── local.env.example
│   └── local.env
├── config.yml                   # 설정 파일 (DI Container용)
├── pyproject.toml               # 의존성 관리
├── alembic.ini                  # Alembic 설정
├── docker-compose.yml           # Docker Compose
├── run_server_local.py          # 모놀리식 서버 실행
└── run_microservice.py          # 마이크로서비스 실행
```

### 핵심 아키텍처 컴포넌트

#### 1️⃣ 제네릭 베이스 클래스 시스템

모든 CRUD 작업을 자동화하는 **3계층 제네릭 시스템**:

```python
# 타입 파라미터: [CreateEntity, ReturnEntity, UpdateEntity]

BaseRepository[CreateEntity, ReturnEntity, UpdateEntity]
    ↓ 사용
BaseService[CreateEntity, ReturnEntity, UpdateEntity]
    ↓ 사용
BaseUseCase[CreateEntity, ReturnEntity, UpdateEntity]
```

**구현 예시 (User 도메인)**:
```python
# Repository
class UserRepository(
    BaseRepository[CoreCreateUserEntity, CoreUserEntity, CoreUpdateUserEntity]
):
    def __init__(self, database: Database):
        super().__init__(
            database=database,
            model=UserModel,  # SQLAlchemy Model
            create_entity=CoreCreateUserEntity,
            return_entity=CoreUserEntity,
            update_entity=CoreUpdateUserEntity,
        )
    # 추가 메서드만 구현하면 됨 (기본 CRUD는 자동)

# Service
class UserService(
    BaseService[CoreCreateUserEntity, CoreUserEntity, CoreUpdateUserEntity]
):
    def __init__(self, user_repository: UserRepository):
        super().__init__(
            base_repository=user_repository,
            create_entity=CoreCreateUserEntity,
            return_entity=CoreUserEntity,
            update_entity=CoreUpdateUserEntity,
        )
    # 비즈니스 로직 추가

# UseCase
class UserUseCase(
    BaseUseCase[CoreCreateUserEntity, CoreUserEntity, CoreUpdateUserEntity]
):
    def __init__(self, user_service: UserService):
        super().__init__(
            base_service=user_service,
            create_entity=CoreCreateUserEntity,
            return_entity=CoreUserEntity,
            update_entity=CoreUpdateUserEntity,
        )
    # 애플리케이션 로직 조율
```

**자동으로 제공되는 메서드**:
- `create_data(create_data)` - 단일 생성
- `create_datas(create_datas)` - 복수 생성
- `get_datas(page, page_size)` - 페이지네이션 조회
- `get_data_by_data_id(data_id)` - ID로 조회
- `get_datas_by_data_ids(data_ids)` - 복수 ID 조회
- `update_data_by_data_id(data_id, update_data)` - 수정
- `delete_data_by_data_id(data_id)` - 삭제

#### 2️⃣ 의존성 주입 컨테이너

**계층적 DI 구조**:
```python
ServerContainer (통합)
    ├── CoreContainer (공통 인프라)
    │   ├── Database (MySQL)
    │   ├── HttpClient (aiohttp)
    │   ├── MinioService (스토리지)
    │   ├── S3Service (AWS S3)
    │   └── CeleryManager (메시징)
    └── UserContainer (도메인별)
        ├── UserRepository
        ├── UserService
        └── UserUseCase
```

**Router에서 의존성 주입 사용**:
```python
@router.post("/user")
@inject  # dependency-injector 데코레이터
async def create_user(
    create_data: CoreCreateUserRequest,
    user_use_case: UserUseCase = Depends(
        Provide[UserContainer.user_use_case]  # 자동 주입
    ),
):
    # 모든 의존성이 자동으로 해결됨
    data = await user_use_case.create_data(...)
    return SuccessResponse(data=...)
```

## 🔧 기술 스택

### 핵심 프레임워크 & 라이브러리

| 카테고리 | 기술 | 버전 | 용도 |
|---------|------|------|------|
| **Web Framework** | FastAPI | 0.115+ | 고성능 비동기 웹 프레임워크 |
| **ASGI Server** | Uvicorn | 0.34+ | 개발 서버 |
| **WSGI Server** | Gunicorn | 23.0+ | 프로덕션 서버 |
| **Validation** | Pydantic | 2.10+ | 데이터 검증 및 설정 관리 |
| **ORM** | SQLAlchemy | 2.0+ | 데이터베이스 ORM (async 지원) |
| **Migration** | Alembic | 1.15+ | 데이터베이스 마이그레이션 |
| **DI** | dependency-injector | 4.46+ | 의존성 주입 컨테이너 |

### 데이터베이스 & 스토리지

| 카테고리 | 기술 | 용도 |
|---------|------|------|
| **RDBMS** | MySQL 8.0 | 메인 관계형 데이터베이스 |
| **Driver** | aiomysql | 비동기 MySQL 드라이버 |
| **Sync Driver** | PyMySQL | 동기 MySQL 드라이버 (마이그레이션) |
| **Object Storage** | MinIO | S3 호환 오브젝트 스토리지 |
| **Cloud Storage** | AWS S3 | 클라우드 스토리지 (선택적) |

### 비동기 & 메시징

| 카테고리 | 기술 | 용도 |
|---------|------|------|
| **HTTP Client** | aiohttp | 비동기 HTTP 클라이언트 (연결 풀) |
| **Task Queue** | Celery | 비동기 작업 큐 |
| **Message Broker** | AWS SQS | 메시지 브로커 (Celery backend) |

### 개발 도구 & 품질

| 카테고리 | 기술 | 용도 |
|---------|------|------|
| **Code Formatter** | Black | 코드 포매팅 |
| **Import Sorter** | isort | Import 정렬 |
| **Linter** | Flake8 | 코드 린팅 |
| **Type Checker** | mypy | 타입 체킹 (수동) |
| **Security** | Bandit | 보안 취약점 검사 (수동) |
| **Pre-commit** | pre-commit | Git hook 자동화 |
| **Admin Panel** | SQLAdmin | 데이터베이스 관리 UI |
| **Load Testing** | Locust | 부하 테스트 |

### 인프라 & 배포

| 카테고리 | 기술 | 용도 |
|---------|------|------|
| **Containerization** | Docker | 컨테이너화 |
| **Orchestration** | Docker Compose | 로컬 개발 환경 |
| **Package Manager** | UV | 빠른 Python 패키지 관리 |

## 🚀 빠른 시작

### 사전 요구사항

- Python 3.12.9+
- MySQL 8.0+ (또는 Docker)
- MinIO (선택적, 파일 스토리지 사용 시)
- UV 패키지 매니저 (권장) 또는 pip

### 설치 및 실행

#### 1️⃣ 프로젝트 클론

```bash
git clone <repository-url>
cd fastapi-layered-architecture
```

#### 2️⃣ Python 가상 환경 및 의존성 설치

**옵션 A: UV 사용 (권장 - 빠름)**
```bash
# UV 설치 (없는 경우)
curl -LsSf https://astral.sh/uv/install.sh | sh

# 가상환경 생성 및 활성화
uv venv --python 3.12.9
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# 의존성 설치
uv pip install -e .
```

**옵션 B: pip 사용**
```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -e .
```

#### 3️⃣ 환경 변수 설정

```bash
# 예제 파일 복사
cp _env/local.env.example _env/local.env

# 환경 변수 편집 (필수)
nano _env/local.env
```

**필수 환경 변수**:
```env
ENV=local
DATABASE_USER=root
DATABASE_PASSWORD=password
DATABASE_HOST=localhost
DATABASE_PORT=3306
DATABASE_NAME=fastapi_db
MINIO_HOST=localhost
MINIO_PORT=9000
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin
MINIO_BUCKET_NAME=test-bucket
AWS_SQS_REGION=ap-northeast-2
AWS_SQS_ACCESS_KEY=your_access_key
AWS_SQS_SECRET_KEY=your_secret_key
AWS_SQS_QUEUE=default-queue
```

#### 4️⃣ 인프라 서비스 시작 (Docker 사용)

```bash
# MySQL 시작
docker run -d \
  --name mysql \
  -e MYSQL_ROOT_PASSWORD=password \
  -e MYSQL_DATABASE=fastapi_db \
  -p 3306:3306 \
  mysql:8.0

# MinIO 시작 (선택적)
docker run -d \
  --name minio \
  -p 9000:9000 \
  -p 9001:9001 \
  -e MINIO_ROOT_USER=minioadmin \
  -e MINIO_ROOT_PASSWORD=minioadmin \
  minio/minio server /data --console-address ":9001"
```

#### 5️⃣ 데이터베이스 마이그레이션

```bash
# 최신 스키마로 마이그레이션
alembic upgrade head

# 새 마이그레이션 생성 (필요 시)
alembic revision --autogenerate -m "설명"
```

#### 6️⃣ 애플리케이션 실행

**옵션 A: 모놀리식 서버 (권장 - 개발용)**
```bash
python run_server_local.py --env local
```
- **URL**: http://localhost:8000
- **문서**: http://localhost:8000/api/docs
- **Admin**: http://localhost:8000/api/admin

**옵션 B: 마이크로서비스**
```bash
python run_microservice.py --env local
```
- **User Service**: http://localhost:8001/docs
- **Chat Service**: http://localhost:8002/docs

**옵션 C: Docker Compose**
```bash
# 빌드 및 실행
docker-compose up -d

# 로그 확인
docker-compose logs -f

# 중지
docker-compose down
```

### 🎉 성공!

서버가 실행되면 다음 URL에 접속하세요:

#### 📚 API 문서
- **메인 문서 허브**: http://localhost:8000/api/docs
- **Swagger UI**: http://localhost:8000/api/docs-swagger
- **ReDoc**: http://localhost:8000/api/docs-redoc
- **Scalar**: http://localhost:8000/api/docs-scalar

#### 🔧 관리 도구
- **SQLAdmin**: http://localhost:8000/api/admin (데이터베이스 관리)
- **MinIO Console**: http://localhost:9001 (스토리지 관리)

#### ⚡ Health Check
```bash
curl http://localhost:8000/api/health
```

### 코드 품질 관리

#### Pre-commit 설정
```bash
# pre-commit 설치
pre-commit install

# 모든 파일에 실행
pre-commit run --all-files

# 수동 체크 (mypy, bandit)
pre-commit run --hook-stage manual mypy
pre-commit run --hook-stage manual bandit
```

## 📚 API 문서

### 다중 문서 UI 지원

본 프로젝트는 **5가지 API 문서 UI**를 제공합니다:

| UI | URL | 특징 |
|----|-----|------|
| **선택 허브** | `/api/docs` | 문서 UI 선택 페이지 |
| **Swagger UI** | `/api/docs-swagger` | 가장 대중적, 인터랙티브 테스트 |
| **ReDoc** | `/api/docs-redoc` | 깔끔한 문서 중심 디자인 |
| **Scalar** | `/api/docs-scalar` | 모던하고 세련된 UI |
| **Elements** | `/api/docs-elements` | Stoplight 인터랙티브 UI |
| **RapiDoc** | `/api/docs-rapidoc` | 빠르고 가벼운 UI |

### API 엔드포인트 예시

#### User Management API

| Method | Endpoint | 설명 |
|--------|----------|------|
| `POST` | `/api/v1/user` | 사용자 생성 |
| `POST` | `/api/v1/user` | 복수 사용자 생성 |
| `GET` | `/api/v1/user?page=1&pageSize=10` | 사용자 목록 (페이지네이션) |
| `GET` | `/api/v1/user/{user_id}` | 특정 사용자 조회 |
| `POST` | `/api/v1/user/by-ids` | ID 목록으로 조회 |
| `PUT` | `/api/v1/user/{user_id}` | 사용자 정보 수정 |
| `DELETE` | `/api/v1/user/{user_id}` | 사용자 삭제 |

#### 응답 형식

**성공 응답**:
```json
{
  "success": true,
  "message": "Request processed successfully",
  "data": {
    "id": 1,
    "username": "john_doe",
    "full_name": "John Doe",
    "email": "john@example.com",
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-01T00:00:00Z"
  },
  "pagination": null
}
```

**에러 응답**:
```json
{
  "success": false,
  "message": "Request failed",
  "error_code": "USER_NOT_FOUND",
  "error_details": {
    "user_id": 999
  }
}
```

## 📈 새로운 도메인 추가 가이드

본 아키텍처는 도메인 확장이 매우 간단합니다. **User 도메인**을 참고하여 새로운 도메인을 추가하세요.

### 1단계: 도메인 디렉토리 생성

```bash
src/
└── product/              # 새로운 도메인 (예: Product)
    ├── domain/
    │   ├── entities/
    │   │   └── product_entity.py
    │   └── services/
    │       └── product_service.py
    ├── application/
    │   └── use_cases/
    │       └── product_use_case.py
    ├── infrastructure/
    │   ├── database/
    │   │   └── models/
    │   │       └── product_model.py
    │   ├── repositories/
    │   │   └── product_repository.py
    │   └── di/
    │       └── product_container.py
    ├── interface/
    │   ├── server/
    │   │   ├── routers/
    │   │   │   └── product_router.py
    │   │   ├── dtos/
    │   │   │   └── product_dto.py
    │   │   └── bootstrap/
    │   │       └── product_bootstrap.py
    │   ├── admin/
    │   │   └── views/
    │   │       └── product_view.py
    │   └── consumer/
    │       └── tasks/
    └── app.py            # 마이크로서비스 진입점 (선택)
```

### 2단계: Entity 정의

```python
# src/product/domain/entities/product_entity.py
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
    name: str = Field(..., description="제품명")
    price: int = Field(..., description="가격")

class UpdateProductEntity(Entity):
    name: str = Field(..., description="제품명")
    price: int = Field(..., description="가격")
```

### 3단계: Repository 구현

```python
# src/product/infrastructure/repositories/product_repository.py
from src._core.infrastructure.repositories.base_repository import BaseRepository
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

### 4단계: Service 구현

```python
# src/product/domain/services/product_service.py
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

### 5단계: UseCase 구현

```python
# src/product/application/use_cases/product_use_case.py
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

### 6단계: DI Container 설정

```python
# src/product/infrastructure/di/product_container.py
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

### 7단계: Router 구현

```python
# src/product/interface/server/routers/product_router.py
from fastapi import APIRouter, Depends
from dependency_injector.wiring import inject, Provide
from src._core.application.dtos.base_response import SuccessResponse
from src.product.application.use_cases.product_use_case import ProductUseCase
from src.product.infrastructure.di.product_container import ProductContainer
from src.product.interface.server.dtos.product_dto import (
    CreateProductRequest, ProductResponse
)

router = APIRouter()

@router.post("/product", response_model=SuccessResponse[ProductResponse])
@inject
async def create_product(
    create_data: CreateProductRequest,
    use_case: ProductUseCase = Depends(Provide[ProductContainer.product_use_case]),
):
    data = await use_case.create_data(create_data=create_data.to_entity(...))
    return SuccessResponse(data=ProductResponse.from_entity(data))
```

### 8단계: ServerContainer에 통합

```python
# src/_shared/infrastructure/di/server_container.py
from dependency_injector import containers, providers
from src._core.infrastructure.di.core_container import CoreContainer
from src.user.infrastructure.di.user_container import UserContainer
from src.product.infrastructure.di.product_container import ProductContainer  # 추가

class ServerContainer(containers.DeclarativeContainer):
    core_container = providers.Container(CoreContainer)
    user_container = providers.Container(UserContainer, core_container=core_container)
    product_container = providers.Container(ProductContainer, core_container=core_container)  # 추가
```

### 9단계: Bootstrap에 등록

```python
# src/bootstrap.py에 추가
from src.product.interface.server.bootstrap.product_bootstrap import bootstrap_product_domain

def bootstrap_app(app: FastAPI) -> None:
    # ... 기존 코드 ...
    
    server_container = ServerContainer()
    bootstrap_user_domain(...)
    bootstrap_product_domain(  # 추가
        app=app,
        database=server_container.core_container.database(),
        product_container=server_container.product_container,
    )
```

### ✅ 완료!

이제 새로운 도메인이 추가되었습니다. **모든 CRUD 작업은 자동으로 제공**되며, 추가 비즈니스 로직만 구현하면 됩니다.

## 🔄 아키텍처 패턴 상세

### 1. Domain-Driven Design (DDD)

**도메인이 중심**이 되는 설계 방식:

```
도메인 모델 (Entity, Service) 
    ↓ 
비즈니스 로직과 규칙 
    ↓ 
기술적 구현 (Repository, Database)
```

**핵심 원칙**:
- **도메인 순수성**: Entity와 Service는 인프라에 의존하지 않음
- **비즈니스 중심**: 도메인 언어로 코드 작성
- **계층 분리**: 각 계층의 책임을 명확히 구분

### 2. Clean Architecture (헥사고날 아키텍처)

**의존성 역전 원칙**:
```python
# ❌ 잘못된 방식: Domain이 Infrastructure에 의존
class UserService:
    def __init__(self, database: Database):  # Infrastructure 의존
        self.database = database

# ✅ 올바른 방식: Infrastructure가 Domain에 의존
class UserService:
    def __init__(self, repository: BaseRepository):  # 추상화 의존
        self.repository = repository

class UserRepository(BaseRepository):  # Infrastructure가 구현
    pass
```

### 3. Repository Pattern

**데이터 액세스 추상화**:
- Domain Layer는 Repository 인터페이스만 알고 있음
- Infrastructure Layer가 실제 구현 제공
- 테스트 시 Mock Repository로 교체 가능

### 4. CQRS (명령-조회 책임 분리)

**읽기와 쓰기 분리**:
- **Command**: `create_data`, `update_data`, `delete_data`
- **Query**: `get_data`, `get_datas` (읽기 전용, 부작용 없음)

## 🌐 모놀리식 vs 마이크로서비스

본 아키텍처는 **두 가지 실행 모드**를 지원합니다:

### 모놀리식 모드 (권장 - 개발/소규모)

```bash
python run_server_local.py --env local
```

**장점**:
- 간단한 배포 및 디버깅
- 낮은 운영 복잡도
- 트랜잭션 관리 용이

**구조**:
```
src/app.py (단일 FastAPI 앱)
    ├── User Domain
    ├── Product Domain
    └── Order Domain
```

### 마이크로서비스 모드 (프로덕션/대규모)

```bash
python run_microservice.py --env prod
```

**장점**:
- 독립적인 배포 및 확장
- 장애 격리
- 기술 스택 다양화

**구조**:
```
User Service (Port 8001)
Product Service (Port 8002)
Order Service (Port 8003)
    ↓
API Gateway (Port 8000)
```

## 🔒 보안 고려사항

### 환경 변수 관리

- **절대 하드코딩 금지**: API 키, 비밀번호 등
- **`.env` 파일 사용**: `.gitignore`에 추가 필수
- **Pydantic Settings**: 타입 안전한 설정 관리

### 예정된 보안 기능

- **JWT 인증**: 토큰 기반 인증
- **RBAC**: 역할 기반 접근 제어
- **Rate Limiting**: API 호출 제한
- **CORS**: Cross-Origin 설정
- **SQL Injection 방지**: Parameterized Query (SQLAlchemy)

## 🚀 성능 최적화

### 데이터베이스

- **비동기 처리**: `aiomysql`로 논블로킹 I/O
- **연결 풀**: `pool_size=10`, `max_overflow=20`
- **인덱스 최적화**: ID, 외래 키 자동 인덱싱
- **세션 관리**: Context Manager로 자동 close

### HTTP 클라이언트

- **연결 풀**: `aiohttp.TCPConnector`로 재사용
- **타임아웃**: Connect/Read 타임아웃 설정
- **DNS 캐싱**: TTL 300초

### 캐싱 (향후 계획)

- **Redis 통합**: 자주 조회되는 데이터 캐싱
- **Application Level**: `functools.lru_cache`

## 🧪 테스트 전략

### 단위 테스트

```python
# Repository 테스트 (Mock Database)
async def test_create_user():
    mock_db = Mock(spec=Database)
    repo = UserRepository(database=mock_db)
    # ...
```

### 통합 테스트

```python
# FastAPI TestClient
from fastapi.testclient import TestClient

client = TestClient(app)
response = client.post("/api/v1/user", json={...})
assert response.status_code == 200
```

## 📊 모니터링 및 로깅 (향후 계획)

- **구조화된 로깅**: JSON 형식 로그
- **Prometheus**: 메트릭 수집
- **Grafana**: 시각화 대시보드
- **Sentry**: 에러 트래킹

## 🤝 기여 가이드

### 코딩 규칙

1. **Black**: 자동 포매팅 (88자 제한)
2. **isort**: Import 정렬
3. **Type Hints**: 모든 함수에 타입 명시
4. **Docstring**: 복잡한 로직에 설명 추가

### Commit 규칙

```
feat: 새로운 기능 추가
fix: 버그 수정
docs: 문서 수정
style: 코드 포맷팅
refactor: 리팩토링
test: 테스트 추가
chore: 빌드 또는 도구 변경
```

## 🎓 학습 자료

### 추천 읽을거리

- **Domain-Driven Design** - Eric Evans
- **Clean Architecture** - Robert C. Martin
- **Implementing Domain-Driven Design** - Vaughn Vernon

### 관련 패턴

- **Repository Pattern**: 데이터 액세스 추상화
- **Dependency Injection**: 의존성 역전
- **Factory Pattern**: 객체 생성 캡슐화
- **Strategy Pattern**: 알고리즘 교체 가능

## 📝 라이선스

이 프로젝트는 교육 및 참고 목적으로 제공됩니다.

## 🙏 감사의 말

이 아키텍처는 다음 원칙들을 기반으로 합니다:
- **SOLID 원칙**
- **Clean Code**
- **Domain-Driven Design**
- **Hexagonal Architecture**

---

**💡 이 프로젝트는 엔터프라이즈급 애플리케이션을 위한 범용 백엔드 아키텍처 템플릿입니다.**

비즈니스 로직에 집중하고, 인프라는 우리가 제공하는 견고한 기반을 활용하세요.
