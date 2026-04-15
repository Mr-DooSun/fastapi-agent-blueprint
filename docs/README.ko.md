<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="assets/logo-dark.png">
    <source media="(prefers-color-scheme: light)" srcset="assets/logo-light.png">
    <img alt="FastAPI Agent Blueprint" src="assets/logo-light.png" width="200">
  </picture>
</p>

<h1 align="center">FastAPI Agent Blueprint</h1>

<p align="center">
  <a href="https://github.com/Mr-DooSun/fastapi-agent-blueprint/actions/workflows/ci.yml"><img src="https://github.com/Mr-DooSun/fastapi-agent-blueprint/actions/workflows/ci.yml/badge.svg" alt="CI"></a>
  <a href="https://www.python.org/downloads/"><img src="https://img.shields.io/badge/Python-3.12.9+-blue.svg" alt="Python"></a>
  <a href="https://fastapi.tiangolo.com"><img src="https://img.shields.io/badge/FastAPI-0.115+-green.svg" alt="FastAPI"></a>
  <a href="../LICENSE"><img src="https://img.shields.io/badge/License-MIT-yellow.svg" alt="License"></a>
  <a href="https://github.com/astral-sh/ruff"><img src="https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json" alt="Ruff"></a>
  <a href="https://github.com/Mr-DooSun/fastapi-agent-blueprint/stargazers"><img src="https://img.shields.io/github/stars/Mr-DooSun/fastapi-agent-blueprint?style=social" alt="GitHub Stars"></a>
</p>

<p align="center">
  <b>FastAPI DDD 템플릿, AI 에이전트 백엔드를 위해 설계.</b><br>
  보일러플레이트 제로 CRUD + 자동 도메인 발견 + 벡터 검색 인프라. MCP 서버 + AI 오케스트레이션 곧 출시.<br>
  Claude Code &amp; Codex CLI용 14+ AI 개발 스킬 내장.
</p>

<p align="center">
  <a href="#빠른-시작">빠른 시작</a> · <a href="#이-프로젝트는-누구를-위한-것인가요">누구를 위한 것?</a> · <a href="#아키텍처">아키텍처</a> · <a href="#비교">비교</a> · <a href="../README.md">English</a>
</p>

<p align="center">
  <a href="https://github.com/Mr-DooSun/fastapi-agent-blueprint/generate">
    <img src="https://img.shields.io/badge/-Use%20this%20template-2ea44f?style=for-the-badge" alt="Use this template">
  </a>
</p>

---

## 이 프로젝트는 누구를 위한 것인가요?

- **FastAPI 개발자** — 튜토리얼 수준을 넘어 프로덕션 프로젝트 구조가 필요한 분 (DDD 레이어, DI 컨테이너, 전면 async, 아키텍처 자동 강제)
- **백엔드 팀** — REST API + 백그라운드 워커 + 어드민 UI가 동일한 도메인 로직을 공유해야 하는 시스템을 만드는 분
- **AI 에이전트 빌더** — 벡터 검색과 임베딩 인프라가 즉시 사용 가능하고, MCP 서버와 PydanticAI 오케스트레이션이 곧 추가될 기반이 필요한 분
- **AI 기반 개발자** — Claude Code나 Codex CLI를 사용하며 두 도구 모두에서 작동하는 14+개의 내장 AI 개발 스킬이 있는 코드베이스를 원하는 분

---

## 제공 기능

- **보일러플레이트 제로 CRUD** — `BaseRepository[DTO]` + `BaseService[Create, Update, DTO]` 상속으로 7개 비동기 메서드 즉시 제공
- **도메인 자동 발견** — 도메인 폴더를 추가하면 자동 등록. Container나 bootstrap 수정 불필요
- **3가지 인터페이스** — HTTP API (FastAPI) + 비동기 Worker (Taskiq) + Admin UI (NiceGUI), 하나의 도메인 레이어 공유
- **교체 가능한 인프라** — PostgreSQL/MySQL/SQLite, DynamoDB, S3/MinIO, SQS/RabbitMQ, OpenAI/Bedrock — 환경변수로 전환
- **벡터 인프라** — S3 Vectors + OpenAI/Bedrock 임베딩 + 시맨틱 chunking 유틸리티
- **타입 안전 제네릭** — `BaseRepository[ProductDTO]`, `BaseService[CreateProductRequest, UpdateProductRequest, ProductDTO]`, `SuccessResponse[ProductResponse]`
- **아키텍처 자동 강제** — Pre-commit hook이 커밋 시점에 `Domain → Infrastructure` import 차단
- **DynamoDB 지원** — 커서 기반 pagination의 `BaseDynamoRepository`, PostgreSQL과 병행 사용
- **14+ AI 개발 스킬** — Claude Code와 Codex CLI 모두 지원: `new-domain`, `add-api`, `onboard`, `review-architecture` 등 ([상세](#ai-네이티브-개발))
- **비동기 우선** — DB(asyncpg)부터 HTTP(aiohttp), 태스크 큐(Taskiq)까지
- **37개 ADR** — 모든 기술 선택을 근거와 함께 문서화 ([인덱스 보기](../docs/history/README.md))

<details>
<summary><b>Coming soon</b></summary>

- **MCP 서버 인터페이스** — FastMCP를 통해 도메인 서비스를 AI 에이전트 도구로 노출 ([#18](https://github.com/Mr-DooSun/fastapi-agent-blueprint/issues/18))
- **PydanticAI 통합** — Pydantic 네이티브 출력의 구조화된 LLM 오케스트레이션 ([#15](https://github.com/Mr-DooSun/fastapi-agent-blueprint/issues/15))
- **pgvector** — 추가 벡터 백엔드 ([#11](https://github.com/Mr-DooSun/fastapi-agent-blueprint/issues/11))

</details>

---

## 빠른 시작

```bash
# 1. Clone
git clone https://github.com/Mr-DooSun/fastapi-agent-blueprint.git
cd fastapi-agent-blueprint

# 2. 셋업 (uv 필요)
make setup

# 3. 환경변수 설정
cp _env/local.env.example _env/local.env

# 4. PostgreSQL 실행 + 마이그레이션 + 서버 시작
make dev
```

http://localhost:8000/docs-swagger 에서 API를 확인하세요.

<details>
<summary>수동 설정 (Make 미사용)</summary>

```bash
# 2. 가상환경 + 의존성 설치
uv venv --python 3.12
source .venv/bin/activate
uv sync --group dev

# 3. 환경변수 설정
cp _env/local.env.example _env/local.env

# 4. PostgreSQL 실행 (Docker)
docker compose -f docker-compose.local.yml up -d postgres

# 5. 마이그레이션 + 서버 실행
alembic upgrade head
python run_server_local.py --env local
```
</details>

---

## Why?

### 도메인 로직 — 어디서든 접근 가능

비즈니스 로직을 한 번 작성하고, REST API, 백그라운드 작업, 어드민 뷰, AI 에이전트 도구로 노출하세요.

```python
# 1. 서비스 정의
class DocumentService(
    BaseService[CreateDocumentRequest, UpdateDocumentRequest, DocumentDTO]
):
    async def analyze(self, document_id: int) -> AnalysisDTO:
        ...  # 비즈니스 로직

# 2. REST API — 프론트엔드용
@router.post("/documents/{document_id}/analyze")
async def analyze_document(document_id: int, service=Depends(...)):
    return await service.analyze(document_id)

# 3. MCP 도구 — AI 에이전트용 (coming soon)
@mcp.tool()
async def analyze_document(document_id: int) -> AnalysisResult:
    return await document_service.analyze(document_id)

# 4. 백그라운드 작업 — 배치 처리용
@broker.task()
async def batch_analyze(project_id: int):
    for doc in await service.get_by_project(project_id):
        await service.analyze(doc.id)
```

### 보일러플레이트 제로 CRUD

```python
# Before: 도메인마다 동일한 CRUD 반복
@router.post("/user")
async def create_user(user: UserCreate):
    db = get_db()
    new_user = User(**user.dict())
    db.add(new_user)
    db.commit()
    return new_user

@router.post("/product")  # 또 반복...
async def create_product(product: ProductCreate):
    db = get_db()
    new_product = Product(**product.dict())
    db.add(new_product)
    db.commit()
    return new_product
```

```python
# After: 베이스 클래스 상속 한 줄로 CRUD 완료
class ProductRepository(BaseRepository[ProductDTO]):
    def __init__(self, database: Database):
        super().__init__(database=database, model=ProductModel, return_entity=ProductDTO)

class ProductService(BaseService[CreateProductRequest, UpdateProductRequest, ProductDTO]):
    def __init__(self, product_repository: ProductRepositoryProtocol):
        super().__init__(repository=product_repository)

# 핵심 CRUD 메서드와 pagination helper 자동 제공 — 커스텀 로직만 추가하면 됨
```

---

## 아키텍처

```
Router -> Service(BaseService) -> Repository(BaseRepository) -> DB
               ^ 단순 CRUD는 이것만으로 충분

Router -> UseCase -> Service -> Repository -> DB
               ^ 복잡한 비즈니스 로직이 필요할 때만 추가
```

### 계층별 책임

| 계층 | 역할 | Base 클래스 |
|------|------|------------|
| **Interface** | Router, Request/Response, Admin, Worker Task, MCP Tool | - |
| **Domain** | Service (비즈니스 로직), Protocol, DTO, Exception | `BaseService[CreateDTO, UpdateDTO, ReturnDTO]` |
| **Infrastructure** | Repository (DB 접근), Model, DI Container | `BaseRepository[ReturnDTO]` |
| **Application** | UseCase (복합 로직 조율) -- **선택적** | - |

### 데이터 흐름

```
Write: Request --> Service --> Repository --> Model -> DB
Read:  Response <-- Service <-- Repository <-- DTO <-- Model
```

- Request를 Service에 직접 전달 (별도 변환 불필요)
- Repository가 Model -> DTO 변환 (`model_validate(model, from_attributes=True)`)
- Router가 DTO -> Response 변환 (`Response(**dto.model_dump(exclude={...}))`)

### 데이터 객체

| 객체 | 역할 | 위치 |
|------|------|------|
| **Request/Response** | API 통신 규격 | `interface/server/schemas/` |
| **DTO** | 내부 레이어 간 데이터 운반 | `domain/dtos/` |
| **Model** | DB 테이블 매핑 (Repository 밖으로 노출 금지) | `infrastructure/database/models/` |

---

## 인터페이스 타입

각 도메인은 여러 인터페이스를 통해 기능을 노출할 수 있습니다:

| 인터페이스 | 기술 | 상태 | 용도 |
|-----------|------|------|------|
| **HTTP API** | FastAPI | Stable | REST API 엔드포인트 |
| **비동기 Worker** | Taskiq + SQS/RabbitMQ/InMemory | Stable | 백그라운드 태스크 처리 |
| **Admin UI** | NiceGUI | Stable | 자동 발견 기반 admin CRUD 대시보드 |
| **MCP Server** | FastMCP | Planned | AI 에이전트 도구 인터페이스 |

모든 인터페이스는 동일한 Domain/Infrastructure 계층을 공유합니다 -- 비즈니스 로직을 한 번 작성하고, 어디서든 노출하세요.

---

## AI 네이티브 개발

이 템플릿은 **Claude Code**와 **OpenAI Codex CLI**를 위한 AI 협업 지원이 내장되어 있습니다. 두 도구 모두 동일한 아키텍처 규칙(`AGENTS.md`)과 workflow 레퍼런스(`docs/ai/shared/`)를 공유하며, 도구별 하네스가 그 위에 레이어됩니다.

| 레이어 | Claude Code | Codex CLI |
|--------|------------|-----------|
| **공통 규칙** | `AGENTS.md` | `AGENTS.md` |
| **공통 레퍼런스** | `docs/ai/shared/` | `docs/ai/shared/` |
| **도구 설정** | `CLAUDE.md` + `.mcp.json` | `.codex/config.toml` + `.codex/hooks.json` |
| **스킬** | 14개 slash 명령 (`.claude/skills/`) | 15개 workflow 스킬 (`.agents/skills/`) |
| **훅** | PostToolUse 자동 포맷 | 6개 훅 (format, security, session-start, ...) |

### 러닝 커브 제로

복잡한 아키텍처? `/onboard` (Claude) 또는 `$onboard` (Codex)를 입력하세요 -- 당신의 수준에 맞춰 모든 것을 설명해줍니다.

onboard 스킬은 경험 수준에 따라 적응합니다:
- **초급 / 중급 / 고급** -- 수준에 맞게 깊이 조절
- **가이드** -- Phase별 구조화된 안내
- **Q&A** -- 토픽 맵 제공, 질문으로 탐색
- **탐험** -- 자유롭게 코드를 살펴보고, 놓친 핵심은 마지막에 정리

### 내장 스킬

모든 스킬은 Claude Code (`/` 접두사)와 Codex CLI (`$` 접두사) 모두에서 사용 가능합니다:

| 스킬 | 기능 |
|------|------|
| `onboard` | 대화형 온보딩 -- 경험 수준에 맞춰 적응 |
| `new-domain {name}` | 도메인 전체 스캐폴딩 (21개 이상 소스 파일 + 테스트) |
| `add-api {description}` | 기존 도메인에 API 엔드포인트 추가 |
| `add-worker-task {domain} {task}` | 비동기 Taskiq 백그라운드 태스크 추가 |
| `add-admin-page {domain}` | 기존 도메인에 NiceGUI admin 페이지 추가 |
| `add-cross-domain from:{a} to:{b}` | Protocol DIP를 통한 도메인 간 의존성 연결 |
| `plan-feature {description}` | 요구사항 인터뷰 -> 아키텍처 -> 보안 -> 태스크 분해 |
| `review-architecture {domain}` | 아키텍처 컴플라이언스 감사 (20개 이상 검사) |
| `security-review {domain}` | OWASP 기반 보안 감사 |
| `test-domain {domain}` | 도메인 테스트 생성 또는 실행 |
| `fix-bug {description}` | 구조화된 버그 수정 워크플로우 |
| `review-pr {number}` | 아키텍처 인식 PR 리뷰 |
| `sync-guidelines` | 설계 변경 후 문서 동기화 |
| `migrate-domain {command}` | Alembic 마이그레이션 관리 |

> 플러그인 설정, MCP 서버 구성, Codex CLI 상세는 [AI 개발 가이드](ai-development.ko.md)를 참고하세요.

---

## 비교

| 기능 | FastAPI Agent Blueprint | [tiangolo/full-stack](https://github.com/fastapi/full-stack-fastapi-template) | [s3rius/template](https://github.com/s3rius/FastAPI-template) | [teamhide/boilerplate](https://github.com/teamhide/fastapi-boilerplate) |
|------|:-:|:-:|:-:|:-:|
| 보일러플레이트 제로 CRUD (7개 메서드) | **Yes** | No | No | No |
| 도메인 자동 발견 | **Yes** | No | No | No |
| 아키텍처 자동 강제 (pre-commit) | **Yes** | No | No | No |
| AI 개발 스킬 (Claude + Codex) | **14+** | 0 | 0 | 0 |
| 벡터 인프라 (S3 Vectors) | **Yes** | No | No | No |
| 적응형 온보딩 (`/onboard`) | **Yes** | No | No | No |
| 멀티 인터페이스 (API+Worker+Admin+MCP) | **3+1 예정** | 2 | 1 | 1 |
| Architecture Decision Records | **37** | 0 | 0 | 0 |
| 전 계층 타입 안전 제네릭 | **Yes** | 부분 | 부분 | No |
| IoC Container DI | **Yes** | No | No | No |
| MCP 서버 인터페이스 | **Planned** | No | No | No |
| AI 오케스트레이션 (PydanticAI) | **Planned** | No | No | No |

---

## 새 도메인 추가하기

> Claude Code를 사용하면 `/new-domain product` 한 줄로 위 모든 파일을 자동 생성할 수 있습니다.

<details>
<summary>수동 추가 방법 (Product 도메인 예시)</summary>

### 1. Domain Layer

```python
# src/product/domain/dtos/product_dto.py
class ProductDTO(BaseModel):
    id: int = Field(..., description="제품 ID")
    name: str = Field(..., description="제품명")
    price: int = Field(..., description="가격")
    created_at: datetime
    updated_at: datetime

# src/product/domain/protocols/product_repository_protocol.py
class ProductRepositoryProtocol(BaseRepositoryProtocol[ProductDTO]):
    pass

# src/product/domain/services/product_service.py
class ProductService(
    BaseService[CreateProductRequest, UpdateProductRequest, ProductDTO]
):
    def __init__(self, product_repository: ProductRepositoryProtocol):
        super().__init__(repository=product_repository)
    # CRUD 자동 제공. 커스텀 로직만 추가.
```

### 2. Infrastructure Layer

```python
# src/product/infrastructure/database/models/product_model.py
class ProductModel(Base):
    __tablename__ = "product"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    price: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, onupdate=func.now())

# src/product/infrastructure/repositories/product_repository.py
class ProductRepository(BaseRepository[ProductDTO]):
    def __init__(self, database: Database):
        super().__init__(database=database, model=ProductModel, return_entity=ProductDTO)

# src/product/infrastructure/di/product_container.py
class ProductContainer(containers.DeclarativeContainer):
    core_container = providers.DependenciesContainer()
    product_repository = providers.Singleton(ProductRepository, database=core_container.database)
    product_service = providers.Factory(ProductService, product_repository=product_repository)
```

### 3. Interface Layer

```python
# src/product/interface/server/routers/product_router.py
@router.post("/product", response_model=SuccessResponse[ProductResponse])
@inject
async def create_product(
    item: CreateProductRequest,
    product_service: ProductService = Depends(Provide[ProductContainer.product_service]),
) -> SuccessResponse[ProductResponse]:
    data = await product_service.create_data(entity=item)
    return SuccessResponse(data=ProductResponse(**data.model_dump()))
```

### 자동 등록

`discover_domains()`가 새 도메인을 자동 탐지합니다.
`_apps/` 내 container나 bootstrap을 **수정할 필요 없습니다**.

자동 발견 조건:
- `src/{name}/__init__.py` 존재
- `src/{name}/infrastructure/di/{name}_container.py` 존재

</details>

---

## Tech Stack

FastAPI + SQLAlchemy 2.0 + Pydantic 2.x + dependency-injector + Taskiq + NiceGUI + asyncpg + aioboto3

<details>
<summary>상세 스택</summary>

### AI & Agent

| 기술 | 용도 | 상태 |
|------|------|------|
| **AWS S3 Vectors** | 시맨틱 검색 인프라를 위한 관리형 벡터 인덱스 백엔드 | Available |
| **OpenAI / Bedrock Embeddings** | 설정으로 선택하는 플러그형 임베딩 백엔드 | Available |
| **FastMCP** | MCP 서버 — 도메인 서비스를 AI 에이전트 도구로 노출 | Planned |
| **PydanticAI** | Pydantic 네이티브 출력의 구조화된 LLM 오케스트레이션 | Planned |

### Core

| 기술 | 용도 |
|------|------|
| **FastAPI** | 비동기 웹 프레임워크 |
| **Pydantic** 2.x | 데이터 검증, Settings |
| **SQLAlchemy** 2.0 | 비동기 ORM |
| **dependency-injector** | IoC Container ([왜?](../docs/history/013-why-ioc-container.md)) |

### Infrastructure

| 기술 | 용도 |
|------|------|
| **PostgreSQL** + asyncpg | 메인 RDBMS |
| **Taskiq** + AWS SQS | 비동기 태스크 큐 ([왜 Celery가 아닌가?](../docs/history/001-celery-to-taskiq.md)) |
| **aiohttp** | 비동기 HTTP 클라이언트 |
| **aioboto3** | DynamoDB, S3/MinIO, S3 Vectors, Bedrock 클라이언트 |
| **semantic-text-splitter** | 임베딩 전처리를 위한 문자/토큰 chunking 유틸리티 |
| **Alembic** | DB 마이그레이션 |

### DevOps

| 기술 | 용도 |
|------|------|
| **Ruff** | 린팅 + 포맷팅 ([6개 도구 통합](../docs/history/012-ruff-migration.md)) |
| **pre-commit** | Git hook 자동화 + 아키텍처 강제 |
| **UV** | Python 패키지 관리 ([왜 Poetry가 아닌가?](../docs/history/005-poetry-to-uv.md)) |
| **NiceGUI** | Admin 대시보드 UI |

</details>

---

## 프로젝트 구조

<details>
<summary>전체 프로젝트 트리 보기</summary>

```
src/
├── _apps/                        # App-level 진입점
│   ├── server/                  # FastAPI HTTP 서버
│   ├── worker/                  # Taskiq 비동기 워커
│   └── admin/                   # NiceGUI admin 앱
│
├── _core/                        # 공통 인프라
│   ├── common/                  # Pagination, security, text utils, UUID helper
│   ├── domain/
│   │   ├── protocols/           # BaseRepositoryProtocol[ReturnDTO]
│   │   └── services/            # BaseService[CreateDTO, UpdateDTO, ReturnDTO]
│   ├── infrastructure/
│   │   ├── database/            # Database, BaseRepository[ReturnDTO]
│   │   ├── dynamodb/            # DynamoDBClient, BaseDynamoRepository
│   │   ├── embedding/           # OpenAI/Bedrock embedding client
│   │   ├── http/                # HttpClient, BaseHttpGateway
│   │   ├── s3vectors/           # S3VectorClient, BaseS3VectorStore
│   │   ├── taskiq/              # Broker adapter, TaskiqManager
│   │   ├── storage/             # S3/MinIO
│   │   ├── di/                  # CoreContainer
│   │   └── discovery.py         # 도메인 자동 발견
│   ├── application/dtos/        # BaseRequest, BaseResponse, SuccessResponse
│   ├── exceptions/              # Exception handlers, BaseCustomException
│   └── config.py                # Settings (pydantic-settings)
│
├── user/                         # 예시 도메인
│   ├── domain/
│   │   ├── dtos/                # UserDTO
│   │   ├── protocols/           # UserRepositoryProtocol
│   │   ├── services/            # UserService(BaseService[CreateUserRequest, UpdateUserRequest, UserDTO])
│   │   ├── exceptions/          # UserNotFoundException
│   ├── infrastructure/
│   │   ├── database/models/     # UserModel
│   │   ├── repositories/        # UserRepository(BaseRepository[UserDTO])
│   │   └── di/                  # UserContainer
│   └── interface/
│       ├── server/              # routers/, schemas/, bootstrap/
│       ├── worker/              # payloads/, tasks/, bootstrap/
│       └── admin/               # configs/, pages/ (NiceGUI)
│
├── migrations/                   # Alembic
├── _env/                         # 환경변수
└── docs/history/                 # Architecture Decision Records
```

</details>

---

## Architecture Decisions

이 프로젝트의 모든 기술 선택은 ADR(Architecture Decision Record)로 기록되어 있습니다. [37개 전체 ADR 보기 →](../docs/history/README.md)

<details>
<summary>주요 결정</summary>

| # | 제목 |
|---|------|
| [004](../docs/history/004-dto-entity-responsibility.md) | DTO/Entity 책임 재정의 |
| [006](../docs/history/006-ddd-layered-architecture.md) | 도메인별 레이어드 아키텍처 전환 |
| [007](../docs/history/007-di-container-and-app-separation.md) | DI 컨테이너 계층화와 앱 분리 |
| [011](../docs/history/011-3tier-hybrid-architecture.md) | 3-Tier 하이브리드 아키텍처 전환 |
| [012](../docs/history/012-ruff-migration.md) | Ruff 도입 |
| [013](../docs/history/013-why-ioc-container.md) | 상속 대신 IoC Container를 선택한 이유 |

</details>

---

## Roadmap

### Phase 1: AI Agent Foundation
- [ ] FastMCP 인터페이스 ([#18](https://github.com/Mr-DooSun/fastapi-agent-blueprint/issues/18))
- [ ] PydanticAI 통합 ([#15](https://github.com/Mr-DooSun/fastapi-agent-blueprint/issues/15))
- [ ] 추가 벡터 백엔드: pgvector ([#11](https://github.com/Mr-DooSun/fastapi-agent-blueprint/issues/11))
- [ ] JWT 인증 ([#4](https://github.com/Mr-DooSun/fastapi-agent-blueprint/issues/4))

### Phase 2: Production Readiness
- [ ] 구조화된 로깅 — structlog ([#9](https://github.com/Mr-DooSun/fastapi-agent-blueprint/issues/9))
- [ ] 에러 알림 ([#17](https://github.com/Mr-DooSun/fastapi-agent-blueprint/issues/17))
- [ ] CRUD 데이터 검증 ([#10](https://github.com/Mr-DooSun/fastapi-agent-blueprint/issues/10))

### Phase 3: Ecosystem
- [ ] 테스트 커버리지 확대 ([#2](https://github.com/Mr-DooSun/fastapi-agent-blueprint/issues/2))
- [ ] 성능 테스트 — Locust ([#3](https://github.com/Mr-DooSun/fastapi-agent-blueprint/issues/3))
- [ ] 서버리스 배포 ([#6](https://github.com/Mr-DooSun/fastapi-agent-blueprint/issues/6))
- [ ] WebSocket 문서 ([#1](https://github.com/Mr-DooSun/fastapi-agent-blueprint/issues/1))

### Completed
- [x] Storage 추상화 — S3/MinIO 환경변수 전환 ([#58](https://github.com/Mr-DooSun/fastapi-agent-blueprint/issues/58))
- [x] Embedding 서비스 — OpenAI/Bedrock 전환 ([#69](https://github.com/Mr-DooSun/fastapi-agent-blueprint/issues/69))
- [x] S3 Vectors 지원 ([#11](https://github.com/Mr-DooSun/fastapi-agent-blueprint/issues/11))
- [x] DynamoDB 지원 ([#13](https://github.com/Mr-DooSun/fastapi-agent-blueprint/issues/13))
- [x] Broker 추상화 — SQS/RabbitMQ/InMemory ([#8](https://github.com/Mr-DooSun/fastapi-agent-blueprint/issues/8))
- [x] Admin 대시보드 — NiceGUI ([#14](https://github.com/Mr-DooSun/fastapi-agent-blueprint/issues/14))
- [x] 환경별 설정 분리 ([#7](https://github.com/Mr-DooSun/fastapi-agent-blueprint/issues/7), [#16](https://github.com/Mr-DooSun/fastapi-agent-blueprint/issues/16), [#53](https://github.com/Mr-DooSun/fastapi-agent-blueprint/issues/53))
- [x] 워커 페이로드 스키마 ([#37](https://github.com/Mr-DooSun/fastapi-agent-blueprint/issues/37))
- [x] CHANGELOG ([#41](https://github.com/Mr-DooSun/fastapi-agent-blueprint/issues/41))
- [x] Claude Code + Codex CLI용 14+개 AI 개발 스킬
- [x] Codex CLI workflow layer
- [x] 헬스 체크 엔드포인트
- [x] 도메인 자동 발견
- [x] 아키텍처 강제 (pre-commit)

스타를 눌러 진행 상황을 팔로우하세요!

---

## Contributing

개발 환경 설정, 코딩 가이드라인, PR 프로세스는 [CONTRIBUTING.md](../CONTRIBUTING.md)를 참고하세요.

---

## License

[MIT License](../LICENSE) -- 상업적 사용, 수정, 배포 자유.

---

## Star History

<a href="https://star-history.com/#Mr-DooSun/fastapi-agent-blueprint&Date">
 <picture>
   <source media="(prefers-color-scheme: dark)" srcset="https://api.star-history.com/svg?repos=Mr-DooSun/fastapi-agent-blueprint&type=Date&theme=dark" />
   <source media="(prefers-color-scheme: light)" srcset="https://api.star-history.com/svg?repos=Mr-DooSun/fastapi-agent-blueprint&type=Date" />
   <img alt="Star History Chart" src="https://api.star-history.com/svg?repos=Mr-DooSun/fastapi-agent-blueprint&type=Date" width="600" />
 </picture>
</a>
