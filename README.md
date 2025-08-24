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

서버 실행 후 다음 URL에서 API 문서를 확인할 수 있습니다:

### 모놀리식 서버
- **Swagger UI**: http://localhost:8000/api/docs-swagger
- **ReDoc**: http://localhost:8000/api/docs-redoc
- **관리자 페이지**: http://localhost:8000/admin

### 마이크로서비스
- **User Service**: http://localhost:8001/docs-swagger
- **Chat Service**: http://localhost:8002/docs-swagger
- **Gateway** (옵션): http://localhost:8000/docs-swagger

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