# FastAPI 레이어드 아키텍처 프로젝트

## 📋 프로젝트 개요

이 프로젝트는 **Domain-Driven Design (DDD)**와 **Clean Architecture** 원칙을 기반으로 한 **FastAPI 백엔드 아키텍처**입니다. 엔터프라이즈급 애플리케이션에서 요구되는 확장성, 유지보수성, 테스트 용이성을 모두 갖춘 현대적인 파이썬 웹 애플리케이션 프레임워크를 제공합니다.

### 🎯 프로젝트 목적과 경위

**왜 이런 아키텍처를 선택했는가?**

1. **확장성**: 비즈니스 로직의 복잡성이 증가해도 코드 구조가 무너지지 않음
2. **유지보수성**: 각 계층의 책임이 명확히 분리되어 변경 영향도 최소화
3. **테스트 용이성**: 의존성 주입을 통한 모킹과 단위 테스트 지원
4. **도메인 중심 설계**: 비즈니스 로직이 기술적 세부사항에 의존하지 않음
5. **마이크로서비스 준비**: 모놀리식에서 마이크로서비스로 전환 가능한 구조

## 🏗️ 아키텍처 설계

### 전체 아키텍처 다이어그램

```
┌─────────────────────────────────────────────────────────────┐
│                    Presentation Layer                       │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐  │
│  │   Router    │  │    Admin    │  │     WebSocket       │  │
│  │   (REST)    │  │    (UI)     │  │      (Chat)         │  │
│  └─────────────┘  └─────────────┘  └─────────────────────┘  │
└─────────────────────┬───────────────────────────────────────┘
                      │
┌─────────────────────┴───────────────────────────────────────┐
│                  Application Layer                          │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐  │
│  │   UseCase   │  │     DTO     │  │     Messaging       │  │
│  │ (Business)  │  │ (Transfer)  │  │   (RabbitMQ)        │  │
│  └─────────────┘  └─────────────┘  └─────────────────────┘  │
└─────────────────────┬───────────────────────────────────────┘
                      │
┌─────────────────────┴───────────────────────────────────────┐
│                    Domain Layer                             │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐  │
│  │   Entity    │  │   Service   │  │       Enum          │  │
│  │ (Core Data) │  │ (Business)  │  │   (Constants)       │  │
│  └─────────────┘  └─────────────┘  └─────────────────────┘  │
└─────────────────────┬───────────────────────────────────────┘
                      │
┌─────────────────────┴───────────────────────────────────────┐
│                Infrastructure Layer                         │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐  │
│  │ Repository  │  │  Database   │  │      Storage        │  │
│  │(Data Access)│  │   (MySQL)   │  │   (MinIO/S3)        │  │
│  └─────────────┘  └─────────────┘  └─────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

### 데이터 흐름

```
HTTP Request → Router → UseCase → Service → Repository → Database
     ↓           ↓        ↓         ↓          ↓          ↓
   DTO       Entity   Entity    Entity     Entity     Model
```

## 📁 프로젝트 구조 상세 분석

### 🔧 Core 모듈 (`src/core/`)

핵심 인프라와 공통 컴포넌트를 제공하는 기반 모듈입니다.

```
src/core/
├── application/         # 애플리케이션 계층
│   ├── dtos/           # 데이터 전송 객체
│   │   ├── common/     # 공통 DTO (BaseRequest, BaseResponse, Pagination)
│   │   └── user/       # 사용자 관련 DTO
│   ├── messaging/      # 메시징 시스템
│   ├── routers/        # 공통 라우터 (헬스체크, 문서)
│   └── use_cases/      # 베이스 유스케이스
├── domain/             # 도메인 계층
│   ├── entities/       # 도메인 엔티티
│   │   ├── entity.py   # 베이스 엔티티 (Pydantic)
│   │   └── user/       # 사용자 엔티티
│   ├── services/       # 도메인 서비스
│   │   ├── base_service.py    # 제네릭 베이스 서비스
│   │   ├── minio_service.py   # MinIO 스토리지 서비스
│   │   └── s3_service.py      # AWS S3 서비스
│   └── enums/         # 도메인 열거형
├── infrastructure/    # 인프라 계층
│   ├── database/      # 데이터베이스 관련
│   │   ├── database.py        # MySQL 연결/세션 관리
│   │   └── models/            # SQLAlchemy 모델
│   ├── messaging/     # 메시징 인프라
│   │   └── rabbitmq_manager.py # RabbitMQ 연결 관리
│   ├── repositories/ # 베이스 리포지토리
│   └── di/           # 의존성 주입
│       └── core_container.py  # 공통 DI 컨테이너
├── middleware/       # 미들웨어
├── exceptions/       # 예외 처리
└── common/          # 공통 유틸리티
```

#### 핵심 컴포넌트 분석

**1. 제네릭 베이스 클래스들**
- `BaseUseCase`: CRUD 작업을 위한 제네릭 유스케이스
- `BaseService`: 비즈니스 로직을 위한 제네릭 서비스  
- `BaseRepository`: 데이터 액세스를 위한 제네릭 리포지토리

```python
# 모든 베이스 클래스는 3개의 제네릭 타입을 받습니다
BaseUseCase[CreateEntity, ReturnEntity, UpdateEntity]
BaseService[CreateEntity, ReturnEntity, UpdateEntity] 
BaseRepository[CreateEntity, ReturnEntity, UpdateEntity]
```

**2. 의존성 주입 컨테이너 (`CoreContainer`)**
- 데이터베이스 연결 관리
- MinIO/S3 스토리지 서비스
- RabbitMQ 메시징 시스템
- 환경별 설정 자동 로드

### 🚀 도메인별 모듈

#### User 모듈 (`src/user/`)

사용자 관리 도메인의 완전한 구현 예시입니다.

```
src/user/
├── app.py                    # User 마이크로서비스 진입점
├── domain/
│   └── services/
│       └── users_service.py  # 사용자 도메인 서비스
├── infrastructure/
│   ├── di/
│   │   ├── user_container.py    # User 도메인 DI 컨테이너
│   │   └── server_container.py  # 서버 통합 컨테이너
│   └── repositories/
│       └── users_repository.py  # 사용자 리포지토리
├── server/                   # 서버별 구현
│   ├── app.py               # 통합 서버 진입점
│   ├── application/
│   │   ├── routers/         # REST API 라우터
│   │   └── use_cases/       # 사용자 유스케이스
│   ├── admin/              # SQLAdmin 관리자 뷰
│   └── infrastructure/
│       └── bootstrap/       # 도메인 부트스트랩
└── admin/                  # 독립 관리자 모듈
```

#### Chat 모듈 (`src/chat/`)

실시간 채팅을 위한 WebSocket 기반 마이크로서비스입니다.

```
src/chat/
├── app.py          # Chat 마이크로서비스 진입점
├── domain/         # Chat 도메인 (확장 예정)
├── infrastructure/ # Chat 인프라 (확장 예정)
└── server/         # Chat 서버 (확장 예정)
```

## 🔧 기술 스택

### 핵심 프레임워크
- **FastAPI**: 고성능 비동기 웹 프레임워크
- **Pydantic**: 데이터 검증 및 시리얼라이제이션
- **SQLAlchemy**: ORM 및 데이터베이스 추상화
- **Alembic**: 데이터베이스 마이그레이션

### 데이터베이스 및 스토리지
- **MySQL**: 메인 관계형 데이터베이스
- **aiomysql**: 비동기 MySQL 드라이버
- **MinIO**: 오브젝트 스토리지 (S3 호환)
- **AWS S3**: 클라우드 스토리지 지원

### 메시징 및 의존성 주입
- **RabbitMQ**: 메시지 큐 시스템
- **pika**: RabbitMQ 파이썬 클라이언트
- **dependency-injector**: 의존성 주입 프레임워크

### 운영 및 배포
- **Docker**: 컨테이너화
- **Uvicorn**: ASGI 서버
- **Gunicorn**: 프로덕션 WSGI 서버
- **SQLAdmin**: 데이터베이스 관리 UI

## 🚀 시작하기

### 1. 프로젝트 설치

```bash
git clone <repository-url>
cd fastapi-layered-architecture
```

### 2. Python 환경 설정

```bash
# UV 패키지 매니저 사용 (권장)
uv venv --python 3.12.9
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# 의존성 설치
uv pip install -e .
```

### 3. 환경 변수 설정

```bash
# 환경 변수 파일 생성
cp _env/dev.env.example _env/dev.env

# 환경 변수 설정 예시
ENV=dev
DATABASE_USER=your_db_user
DATABASE_PASSWORD=your_db_password
DATABASE_HOST=localhost
DATABASE_PORT=3306
DATABASE_NAME=your_db_name
MINIO_HOST=localhost
MINIO_PORT=9000
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin
MINIO_BUCKET_NAME=test-bucket
RABBITMQ_HOST=localhost
RABBITMQ_PORT=5672
```

### 4. 외부 서비스 설정

#### MySQL 설정
```bash
# Docker로 MySQL 실행
docker run -d \
  --name mysql \
  -e MYSQL_ROOT_PASSWORD=password \
  -e MYSQL_DATABASE=your_db_name \
  -p 3306:3306 \
  mysql:8.0
```

#### MinIO 설정
```bash
# Docker로 MinIO 실행
docker run -d \
  --name minio \
  -p 9000:9000 \
  -p 9001:9001 \
  -e MINIO_ROOT_USER=minioadmin \
  -e MINIO_ROOT_PASSWORD=minioadmin \
  minio/minio server /data --console-address ":9001"
```

#### RabbitMQ 설정
```bash
# Docker로 RabbitMQ 실행
docker run -d \
  --name rabbitmq \
  -p 5672:5672 \
  -p 15672:15672 \
  rabbitmq:3-management
```

### 5. 데이터베이스 마이그레이션

```bash
# 마이그레이션 실행
alembic upgrade head
```

### 6. 프로젝트 실행

#### 모놀리식 서버 실행
```bash
python run_server_local.py --env dev
```

#### 마이크로서비스 실행
```bash
python run_microservice.py --env dev
```

#### Docker 실행
```bash
# 이미지 빌드
docker build -f _docker/docker.Dockerfile -t fastapi-layered .

# 컨테이너 실행
docker-compose up -d
```

## 📚 API 문서

### API 문서 접근 방법

서버 실행 후 다음 URL에서 API 문서를 확인할 수 있습니다:

#### 🎯 통합 문서 허브
- **📚 API 문서 선택기**: http://localhost:8000/api/docs
  - 다양한 스타일의 API 문서 중에서 선택할 수 있는 메인 페이지
  - Swagger UI, ReDoc, Scalar, Elements, RapiDoc 등 5가지 문서 형태 제공

#### 📋 개별 문서 페이지 (모놀리식 서버)
- **Swagger UI**: http://localhost:8000/api/docs-swagger *(가장 많이 사용)*
- **ReDoc**: http://localhost:8000/api/docs-redoc *(깔끔한 읽기 중심)*
- **Scalar**: http://localhost:8000/api/docs-scalar *(모던한 디자인)*
- **Elements**: http://localhost:8000/api/docs-elements *(인터랙티브)*
- **RapiDoc**: http://localhost:8000/api/docs-rapidoc *(빠르고 가벼움)*
- **관리자 페이지**: http://localhost:8000/api/admin *(데이터베이스 관리)*

#### 🚀 마이크로서비스별 문서
- **User Service**: http://localhost:8001/docs *(사용자 관리)*
- **Chat Service**: http://localhost:8002/docs *(실시간 채팅)*
- **Gateway** (옵션): http://localhost:8000/docs *(API 게이트웨이)*

> **💡 추천**: `/api/docs`에서 시작하여 원하는 문서 스타일을 선택하세요!

### API 설계 원칙

#### 1. RESTful API 설계
```
GET    /api/v1/users       # 사용자 목록 조회 (페이지네이션)
POST   /api/v1/user        # 사용자 생성
GET    /api/v1/user/{id}   # 특정 사용자 조회
PUT    /api/v1/user/{id}   # 사용자 정보 수정
DELETE /api/v1/user/{id}   # 사용자 삭제
POST   /api/v1/users       # 다수 사용자 생성
POST   /api/v1/users/by-ids # ID 목록으로 사용자 조회
```

#### 2. 일관된 응답 구조
모든 API는 표준화된 응답 구조를 사용합니다:

**성공 응답 (SuccessResponse)**:
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

**페이지네이션이 포함된 응답**:
```json
{
  "success": true,
  "message": "Request processed successfully",
  "data": [
    {
      "id": 1,
      "username": "john_doe",
      "full_name": "John Doe",
      "email": "john@example.com",
      "created_at": "2024-01-01T00:00:00Z",
      "updated_at": "2024-01-01T00:00:00Z"
    }
  ],
  "pagination": {
    "current_page": 1,
    "page_size": 10,
    "total_items": 100,
    "total_pages": 10,
    "has_previous": false,
    "has_next": true,
    "next_page": 2,
    "previous_page": null
  }
}
```

**오류 응답 (ErrorResponse)**:
```json
{
  "success": false,
  "message": "Request failed",
  "error_code": "USER_NOT_FOUND",
  "error_details": {
    "user_id": 999,
    "timestamp": "2024-01-01T00:00:00Z"
  }
}
```

#### 3. Request/Response DTO 시스템

**요청 DTO 예시**:
```json
{
  "username": "john_doe",
  "full_name": "John Doe", 
  "email": "john@example.com",
  "password": "secure_password"
}
```

**일괄 작업 요청**:
```json
{
  "ids": [1, 2, 3, 4, 5]
}
```

### API 엔드포인트 상세

#### User Management API

##### 1. 사용자 생성
```http
POST /api/v1/user
Content-Type: application/json

{
  "username": "john_doe",
  "full_name": "John Doe",
  "email": "john@example.com", 
  "password": "secure_password"
}
```

**응답**:
- **200 OK**: 사용자 생성 성공
- **400 Bad Request**: 잘못된 요청 데이터
- **409 Conflict**: 이미 존재하는 사용자명/이메일

##### 2. 사용자 목록 조회
```http
GET /api/v1/users?page=1&pageSize=10
```

**쿼리 파라미터**:
- `page`: 페이지 번호 (기본값: 1)
- `pageSize`: 페이지 크기 (기본값: 10)

**응답**: 페이지네이션이 포함된 사용자 목록

##### 3. 특정 사용자 조회
```http
GET /api/v1/user/{user_id}
```

**경로 파라미터**:
- `user_id`: 사용자 ID (정수)

**응답**:
- **200 OK**: 사용자 정보
- **404 Not Found**: 사용자를 찾을 수 없음

##### 4. 사용자 정보 수정
```http
PUT /api/v1/user/{user_id}
Content-Type: application/json

{
  "username": "updated_username",
  "full_name": "Updated Name",
  "email": "updated@example.com",
  "password": "new_password"
}
```

##### 5. 사용자 삭제
```http
DELETE /api/v1/user/{user_id}
```

**응답**:
- **200 OK**: 삭제 성공 (`success: true`)
- **404 Not Found**: 사용자를 찾을 수 없음

##### 6. 다수 사용자 생성
```http
POST /api/v1/users
Content-Type: application/json

[
  {
    "username": "user1",
    "full_name": "User One",
    "email": "user1@example.com",
    "password": "password1"
  },
  {
    "username": "user2", 
    "full_name": "User Two",
    "email": "user2@example.com",
    "password": "password2"
  }
]
```

##### 7. ID 목록으로 사용자 조회
```http
POST /api/v1/users/by-ids
Content-Type: application/json

{
  "ids": [1, 2, 3, 4, 5]
}
```

#### Health Check API

##### 시스템 상태 확인
```http
GET /api/status/health
```

**응답**:
```json
{
  "status": "healthy",
  "timestamp": "2024-01-01T00:00:00Z",
  "services": {
    "database": "connected",
    "rabbitmq": "connected", 
    "minio": "connected"
  }
}
```

### API 테스트 가이드

#### 1. cURL을 사용한 테스트

**사용자 생성**:
```bash
curl -X POST "http://localhost:8000/api/v1/user" \
     -H "Content-Type: application/json" \
     -d '{
       "username": "test_user",
       "full_name": "Test User",
       "email": "test@example.com",
       "password": "test_password"
     }'
```

**사용자 목록 조회**:
```bash
curl -X GET "http://localhost:8000/api/v1/users?page=1&pageSize=5"
```

**특정 사용자 조회**:
```bash
curl -X GET "http://localhost:8000/api/v1/user/1"
```

#### 2. Python requests를 사용한 테스트

```python
import requests

# 기본 URL
BASE_URL = "http://localhost:8000/api/v1"

# 사용자 생성
user_data = {
    "username": "test_user",
    "full_name": "Test User", 
    "email": "test@example.com",
    "password": "test_password"
}

response = requests.post(f"{BASE_URL}/user", json=user_data)
print(f"Status: {response.status_code}")
print(f"Response: {response.json()}")

# 사용자 목록 조회
response = requests.get(f"{BASE_URL}/users", params={"page": 1, "pageSize": 10})
users = response.json()
print(f"Users count: {len(users['data'])}")
print(f"Pagination: {users['pagination']}")
```

#### 3. 자동화된 API 테스트

**pytest를 사용한 테스트 예시**:
```python
import pytest
from fastapi.testclient import TestClient
from src.app import app

client = TestClient(app)

def test_create_user():
    user_data = {
        "username": "test_user",
        "full_name": "Test User",
        "email": "test@example.com", 
        "password": "test_password"
    }
    
    response = client.post("/api/v1/user", json=user_data)
    assert response.status_code == 200
    
    data = response.json()
    assert data["success"] is True
    assert data["data"]["username"] == "test_user"

def test_get_users():
    response = client.get("/api/v1/users?page=1&pageSize=10")
    assert response.status_code == 200
    
    data = response.json()
    assert data["success"] is True
    assert "pagination" in data
```

### OpenAPI/Swagger 사용자 정의

#### 1. API 메타데이터 설정

```python
app = FastAPI(
    title="FastAPI Layered Architecture",
    description="DDD 기반 모놀리식 아키텍처",
    version="1.0.0",
    root_path="/api",
    docs_url="/docs-swagger",
    redoc_url="/docs-redoc",
    openapi_tags=[
        {"name": "사용자", "description": "사용자 관리 관련 API"},
        {"name": "status", "description": "시스템 상태 확인"},
        {"name": "docs", "description": "API 문서"},
    ]
)
```

#### 2. 응답 모델 문서화

```python
@router.post(
    "/user",
    summary="유저 생성",
    description="새로운 사용자를 생성합니다.",
    response_model=SuccessResponse[CoreUsersResponse],
    response_model_exclude={"pagination"},
    responses={
        200: {"description": "사용자 생성 성공"},
        400: {"description": "잘못된 요청 데이터"},
        409: {"description": "이미 존재하는 사용자명 또는 이메일"},
    }
)
```

### API 보안

#### 1. 인증 (향후 구현 예정)
```python
# JWT 토큰 기반 인증
@router.get("/user/me")
async def get_current_user(
    token: str = Depends(oauth2_scheme)
):
    # 토큰 검증 로직
    pass
```

#### 2. 권한 (향후 구현 예정)
```python
# Role-based Access Control
@router.delete("/user/{user_id}")
async def delete_user(
    user_id: int,
    current_user: User = Depends(get_current_admin_user)
):
    # 관리자만 사용자 삭제 가능
    pass
```

#### 3. Rate Limiting (향후 구현 예정)
```python
# API 호출 제한
@router.post("/user")
@rate_limit("10/minute")
async def create_user(...):
    pass
```

### API 문서 활용 팁

1. **Swagger UI에서 직접 테스트**: Try it out 기능으로 실시간 API 테스트
2. **ReDoc**: 더 읽기 쉬운 문서 형태로 API 스펙 확인
3. **OpenAPI 스펙 다운로드**: `/openapi.json`에서 스펙 파일 다운로드
4. **코드 생성**: OpenAPI 스펙을 사용하여 클라이언트 SDK 자동 생성
5. **API 테스트 도구**: Postman, Insomnia 등에서 OpenAPI 스펙 import

## 🔄 아키텍처 패턴 상세

### 1. Domain-Driven Design (DDD)

**Entity**: 도메인의 핵심 객체
```python
class CoreUsersEntity(Entity):
    id: int
    username: str
    full_name: str
    email: str
    # 비즈니스 로직과 데이터가 함께 위치
```

**Service**: 도메인 비즈니스 로직
```python
class UsersService(BaseService):
    # 복잡한 비즈니스 규칙과 로직 구현
    # 여러 Entity와 Repository 조합
```

### 2. Clean Architecture

**의존성 방향**: 외부 → 내부 (Infrastructure → Domain)
```
Infrastructure → Application → Domain
```

**의존성 역전**: 인터페이스를 통한 추상화
```python
# Domain이 Infrastructure에 의존하지 않음
class BaseService:  # Domain Layer
    def __init__(self, base_repository: BaseRepository):
        self.base_repository = base_repository
```

### 3. CQRS (Command Query Responsibility Segregation)

**명령과 조회의 분리**:
- Create/Update/Delete → Command
- Read → Query

### 4. Repository Pattern

**데이터 액세스 추상화**:
```python
class BaseRepository:
    async def create_data(self, create_data: CreateEntity) -> ReturnEntity
    async def get_data_by_data_id(self, data_id: int) -> ReturnEntity
    # 데이터베이스 세부사항 숨김
```

## 🏭 의존성 주입 시스템

### Container 계층 구조

```
ServerContainer
├── CoreContainer (공통 인프라)
│   ├── Database
│   ├── MinIO Service
│   ├── S3 Service
│   └── RabbitMQ Manager
└── UserContainer (도메인별)
    ├── UsersRepository
    ├── UsersService
    └── UsersUseCase
```

### 의존성 주입 활용

```python
@router.post("/user")
@inject
async def create_user(
    create_data: CoreCreateUsersRequest,
    user_use_case: UsersUseCase = Depends(
        Provide[ServerContainer.user_container.users_use_case]
    ),
):
    # UseCase는 자동으로 모든 의존성과 함께 주입됨
```

## 🧪 테스트 전략

### 1. 단위 테스트
- 각 계층별 독립 테스트
- Mock을 통한 의존성 격리

### 2. 통합 테스트  
- 전체 흐름 테스트
- 실제 데이터베이스 사용

### 3. API 테스트
- FastAPI TestClient 활용
- 엔드포인트별 테스트

## 📈 확장 가이드

### 새로운 도메인 추가

1. **도메인 구조 생성**
```bash
src/new_domain/
├── domain/
│   ├── entities/
│   └── services/
├── infrastructure/
│   ├── repositories/
│   └── di/
└── server/
    ├── application/
    └── admin/
```

2. **베이스 클래스 상속**
```python
class NewDomainService(BaseService[CreateEntity, ReturnEntity, UpdateEntity]):
    pass

class NewDomainRepository(BaseRepository[CreateEntity, ReturnEntity, UpdateEntity]):
    pass
```

3. **DI 컨테이너 등록**
```python
class NewDomainContainer(containers.DeclarativeContainer):
    # 의존성 정의
```

4. **라우터 등록**
```python
# 새로운 API 엔드포인트 추가
```

### 마이크로서비스 분리

1. **도메인별 독립 실행**
```bash
# 각 도메인이 독립된 FastAPI 앱으로 실행 가능
python -m src.user.app
python -m src.chat.app
```

2. **Gateway 패턴**
```python
# API Gateway를 통한 라우팅
# 서비스 디스커버리 적용
```

## 🔒 보안 고려사항

### 1. 인증/인가
- JWT 토큰 기반 인증
- Role-based Access Control (RBAC)

### 2. 데이터 보호
- 비밀번호 해싱
- 민감 데이터 암호화

### 3. API 보안
- Rate Limiting
- CORS 설정
- Input Validation

## 🚀 성능 최적화

### 1. 데이터베이스
- 비동기 세션 관리
- 연결 풀링
- 인덱스 최적화

### 2. 캐싱
- Redis 통합 (확장 예정)
- 애플리케이션 레벨 캐싱

### 3. 비동기 처리
- FastAPI 비동기 지원
- 백그라운드 태스크

## 📊 모니터링 및 로깅

### 1. 로깅
- 구조화된 로깅
- 레벨별 로그 관리

### 2. 메트릭 (확장 예정)
- Prometheus 통합
- 성능 메트릭 수집

### 3. 추적 (확장 예정)
- 분산 추적
- 요청 흐름 추적

## 🤝 기여하기

### 개발 워크플로우

1. **Fork the Project**
2. **Create your Feature Branch** (`git checkout -b feature/AmazingFeature`)
3. **Commit your Changes** (`git commit -m 'Add some AmazingFeature'`)
4. **Push to the Branch** (`git push origin feature/AmazingFeature`)
5. **Open a Pull Request**

### 코딩 스타일

- **Black**: 코드 포매팅
- **isort**: Import 정렬
- **flake8**: 린팅
- **mypy**: 타입 체킹

### 커밋 컨벤션

```
feat: 새로운 기능 추가
fix: 버그 수정
docs: 문서 수정
style: 코드 포매팅
refactor: 코드 리팩토링
test: 테스트 추가
chore: 빌드 프로세스 또는 보조 도구 변경
```

## 📞 지원 및 문의

- **이슈 제보**: GitHub Issues를 통해 버그 리포트나 기능 요청
- **토론**: GitHub Discussions에서 아이디어 공유
- **보안 문제**: 보안 관련 이슈는 비공개로 연락

---

이 프로젝트는 현대적인 파이썬 백엔드 개발의 모범 사례를 구현한 템플릿입니다. 
엔터프라이즈급 애플리케이션 개발에 필요한 모든 패턴과 구조를 제공하며, 
개발자들이 비즈니스 로직에 집중할 수 있도록 견고한 기반을 제공합니다.