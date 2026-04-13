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
</p>

<p align="center">
  <b>FastAPI 기반 AI 에이전트 백엔드 플랫폼.</b><br>
  MCP 서버 + AI 오케스트레이션 + 비동기 DDD — CRUD부터 에이전트 도구까지 하나의 코드베이스로.<br>
  사용자와 AI 에이전트 모두를 위한 백엔드를 구축하세요.
</p>

<p align="center">
  <a href="#빠른-시작">빠른 시작</a> · <a href="#아키텍처">아키텍처</a> · <a href="#ai-네이티브-개발-aidd">AI 네이티브 개발</a> · <a href="#비교">비교</a> · <a href="../README.md">English</a>
</p>

<!-- TODO: 데모 GIF 추가
![Demo](assets/demo.gif)
-->

---

## 주요 기능

### AI 에이전트 플랫폼

- **MCP 서버 인터페이스** `planned` — FastMCP를 통해 도메인 서비스를 AI 에이전트 도구로 노출
- **AI 에이전트 오케스트레이션** `planned` — 구조화된 LLM 워크플로우를 위한 PydanticAI 통합
- **벡터 검색** `planned` — 시맨틱 검색, RAG, 유사도 매칭을 위한 pgvector

### 프로덕션 레디 아키텍처

- **4가지 인터페이스** — HTTP API (FastAPI) + 비동기 Worker (Taskiq) + Admin UI (NiceGUI) + MCP Server (예정)
- **보일러플레이트 제로 CRUD** — `BaseRepository[DTO]` + `BaseService[CreateRequest, UpdateRequest, DTO]` 상속으로 핵심 비동기 CRUD와 pagination helper 즉시 제공
- **도메인 자동 발견** — 도메인 폴더를 추가하면 자동 등록. Container나 bootstrap 수정 불필요
- **비동기 우선** — DB(asyncpg)부터 HTTP(aiohttp), 태스크 큐(Taskiq)까지 진정한 async

### 개발자 경험

- **공통 규칙 + 도구별 하네스** — `AGENTS.md`, Claude 스킬, Codex CLI 설정으로 AI 협업 구조화
- **아키텍처 자동 강제** — Pre-commit hook이 커밋 시점에 `Domain -> Infrastructure` import를 차단
- **타입 안전 제네릭** — `BaseRepository[ProductDTO]`, `BaseService[CreateProductRequest, UpdateProductRequest, ProductDTO]`, `SuccessResponse[ProductResponse]`
- **DDD 레이어드 구조** — 각 도메인이 완전히 독립된 계층 보유 (Domain / Infrastructure / Interface / Application)
- **Architecture Decision Records** — 주요 설계 결정을 근거와 함께 문서화

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

# 3. MCP 도구 — AI 에이전트용 (예정)
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

## AI 네이티브 개발 (AIDD)

이 템플릿은 단독으로도 충분히 사용할 수 있습니다. 이제 AI 협업 구조는 **공통 규칙 + 공통 레퍼런스 + 도구별 하네스**로 정리되어 있습니다.

| 파일 | 역할 |
|------|------|
| `AGENTS.md` | 모든 AI 도구가 따라야 하는 공통 규칙의 canonical source |
| `docs/ai/shared/` | Claude와 Codex가 함께 읽는 공통 workflow 레퍼런스와 체크리스트 |
| `CLAUDE.md` | Claude 전용 hooks, plugins, slash skills, workflow 안내 |
| `.mcp.json` | Claude 전용 MCP 설정 |
| `.codex/config.toml` | Codex CLI 전용 프로젝트 설정, profile, feature, MCP 구성 |
| `.codex/hooks.json` | Codex 명령 훅 설정 |
| `.agents/skills/` | repo-local Codex workflow skill |

### 공통 규칙 우선

모든 도구는 먼저 `AGENTS.md`를 기준으로 다음을 따른다:
- 프로젝트 규모 전제
- 절대 금지 규칙
- 레이어 용어와 conversion pattern
- DTO 생성 기준
- 기본 run/test/lint/migration 명령
- 문서와 규칙 drift 관리 원칙

루트 `AGENTS.md`에 다 담기 어려운 workflow 세부사항은 `docs/ai/shared/`에 둡니다. 예: `project-dna.md`, planning/security/review checklist, test pattern.

### Claude Code

#### 러닝 커브 제로

복잡한 아키텍처? `/onboard`를 입력하세요 -- 당신의 수준에 맞춰 모든 것을 설명해줍니다.

`/onboard` 스킬은 경험 수준에 따라 적응합니다:
- **초급**: DDD 개념을 쉬운 비유로 설명
- **중급**: 이 프로젝트 고유의 패턴에 집중
- **고급**: 아키텍처 규칙과 컨벤션으로 바로 이동

#### 14개 내장 스킬

| 명령어 | 기능 |
|--------|------|
| `/onboard` | 대화형 온보딩 -- 경험 수준에 맞춰 적응 |
| `/new-domain {name}` | 도메인 전체 스캐폴딩 (21개 이상 소스 파일 + 테스트) |
| `/add-api {description}` | 기존 도메인에 API 엔드포인트 추가 |
| `/add-worker-task {domain} {task}` | 비동기 Taskiq 백그라운드 태스크 추가 |
| `/add-admin-page {domain}` | 기존 도메인에 NiceGUI admin 페이지 추가 |
| `/add-cross-domain from:{a} to:{b}` | Protocol DIP를 통한 도메인 간 의존성 연결 |
| `/plan-feature {description}` | 요구사항 인터뷰 -> 아키텍처 -> 보안 -> 태스크 분해 |
| `/review-architecture {domain}` | 아키텍처 컴플라이언스 감사 (20개 이상 검사) |
| `/security-review {domain}` | OWASP 기반 보안 감사 |
| `/test-domain {domain}` | 도메인 테스트 생성 또는 실행 |
| `/fix-bug {description}` | 구조화된 버그 수정 워크플로우 |
| `/review-pr {number}` | 아키텍처 인식 PR 리뷰 |
| `/sync-guidelines` | 설계 변경 후 문서 동기화 |
| `/migrate-domain {command}` | Alembic 마이그레이션 관리 |

#### 플러그인 설정 (필수)

코드 인텔리전스(심볼 탐색, 참조 추적, 진단)를 위해 pyright-lsp 플러그인을 설치하세요:

```bash
uv sync                              # pyright 바이너리 설치 (dev 의존성)
claude plugin install pyright-lsp    # Claude Code 플러그인 설치
```

> `.claude/settings.json`의 `enabledPlugins`가 첫 실행 시 자동으로 설치를 안내합니다.

#### MCP 서버 설정 (`.mcp.json`)

**context7** -- 라이브러리 최신 문서 조회
```json
{
  "mcpServers": {
    "context7": {
      "url": "https://mcp.context7.com/mcp"
    }
  }
}
```

> `.mcp.json`은 Claude 측 MCP 진입점입니다. MCP 서버 없이도 프로젝트 자체는 정상 동작하지만, Claude 스킬은 이 설정을 기대합니다.

### Codex CLI

Codex는 `.codex/config.toml`의 project-shared 설정을 사용합니다:

```toml
sandbox_mode = "workspace-write"
approval_policy = "on-request"
web_search = "disabled"

[features]
codex_hooks = true

[profiles.research]
web_search = "live"

[mcp_servers.context7]
url = "https://mcp.context7.com/mcp"
```

> Codex는 원격 Context7 MCP 엔드포인트를 사용합니다. 로컬 stdio 서버(npx) 방식은 샌드박스 네트워크 제한에 의해 차단되므로, HTTP 전송 방식을 사용합니다.

Codex의 레포 workflow layer는 다음으로 나뉩니다:
- `.codex/config.toml` — base config와 profile
- `.codex/hooks.json` + `.codex/hooks/` — command hook
- `.agents/skills/` — `$onboard`, `$plan-feature`, `$review-pr` 같은 repo-local workflow
- `docs/ai/shared/` — Claude/Codex 공통 reference

권장 검증 흐름:
1. Codex에서 이 프로젝트를 trusted 상태로 만든다.
2. `codex mcp list`, `codex mcp get context7`를 실행한다.
3. `codex debug prompt-input -c 'project_doc_max_bytes=400' "healthcheck" | rg "Shared Collaboration Rules|AGENTS\\.md"`로 `AGENTS.md`가 실제 prompt input에 포함되는지 확인한다.
4. 최신 외부 정보가 정말 필요할 때만 `codex -p research` 또는 `codex --search`를 사용한다.
5. Codex memories는 개인/세션 최적화용으로만 보고, 팀 규칙 저장소로 쓰지 않는다.

> `.codex/config.toml`은 Codex 측 하네스 진입점입니다. 웹 검색은 기본 비활성화되어 있으므로, 최신 외부 정보가 필요할 때만 명시적으로 활성화하세요.

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

## 새 도메인 추가하기

Product 도메인을 예로 들면:

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

> Claude Code를 사용하면 `/new-domain product` 한 줄로 위 모든 파일을 자동 생성할 수 있습니다.

---

## 4가지 인터페이스

각 도메인은 여러 인터페이스를 통해 기능을 노출할 수 있습니다:

| 인터페이스 | 기술 | 상태 | 용도 |
|-----------|------|------|------|
| **HTTP API** | FastAPI | Stable | REST API 엔드포인트 |
| **비동기 Worker** | Taskiq + SQS/RabbitMQ/InMemory | Stable | 백그라운드 태스크 처리 |
| **Admin UI** | NiceGUI | Stable | 자동 발견 기반 admin CRUD 대시보드 |
| **MCP Server** | FastMCP | Planned | AI 에이전트 도구 인터페이스 |

모든 인터페이스는 동일한 Domain/Infrastructure 계층을 공유합니다 -- 비즈니스 로직을 한 번 작성하고, 어디서든 노출하세요.

---

## Tech Stack

### AI & Agent `planned`

| 기술 | 용도 |
|------|------|
| **FastMCP** | MCP 서버 — 도메인 서비스를 AI 에이전트 도구로 노출 |
| **PydanticAI** | Pydantic 네이티브 출력의 구조화된 LLM 오케스트레이션 |
| **pgvector** | 벡터 유사도 검색 (PostgreSQL 확장) |

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
| **aioboto3** | S3/MinIO 스토리지 |
| **Alembic** | DB 마이그레이션 |

### DevOps

| 기술 | 용도 |
|------|------|
| **Ruff** | 린팅 + 포맷팅 ([6개 도구 통합](../docs/history/012-ruff-migration.md)) |
| **pre-commit** | Git hook 자동화 + 아키텍처 강제 |
| **UV** | Python 패키지 관리 ([왜 Poetry가 아닌가?](../docs/history/005-poetry-to-uv.md)) |
| **NiceGUI** | Admin 대시보드 UI |

---

## 프로젝트 구조

```
src/
├── _apps/                        # App-level 진입점
│   ├── server/                  # FastAPI HTTP 서버
│   ├── worker/                  # Taskiq 비동기 워커
│   └── admin/                   # NiceGUI admin 앱
│
├── _core/                        # 공통 인프라
│   ├── domain/
│   │   ├── protocols/           # BaseRepositoryProtocol[ReturnDTO]
│   │   └── services/            # BaseService[CreateDTO, UpdateDTO, ReturnDTO]
│   ├── infrastructure/
│   │   ├── database/            # Database, BaseRepository[ReturnDTO]
│   │   ├── http/                # HttpClient, BaseHttpGateway
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

---

## 비교

| 기능 | FastAPI Agent Blueprint | [tiangolo/full-stack](https://github.com/fastapi/full-stack-fastapi-template) | [s3rius/template](https://github.com/s3rius/FastAPI-template) | [teamhide/boilerplate](https://github.com/teamhide/fastapi-boilerplate) |
|------|:-:|:-:|:-:|:-:|
| MCP 서버 인터페이스 | **Planned** | No | No | No |
| AI 오케스트레이션 (PydanticAI) | **Planned** | No | No | No |
| 벡터 검색 (pgvector) | **Planned** | No | No | No |
| 보일러플레이트 제로 CRUD (7개 메서드) | **Yes** | No | No | No |
| 도메인 자동 발견 | **Yes** | No | No | No |
| 아키텍처 자동 강제 (pre-commit) | **Yes** | No | No | No |
| AI 개발 스킬 | **14** | 0 | 0 | 0 |
| 적응형 온보딩 (`/onboard`) | **Yes** | No | No | No |
| 멀티 인터페이스 (API+Worker+Admin+MCP) | **4종** | 2 | 1 | 1 |
| Architecture Decision Records | **32** | 0 | 0 | 0 |
| 전 계층 타입 안전 제네릭 | **Yes** | 부분 | 부분 | No |
| IoC Container DI | **Yes** | No | No | No |

---

## Architecture Decisions

이 프로젝트의 모든 기술 선택은 ADR(Architecture Decision Record)로 기록되어 있습니다.

| # | 제목 |
|---|------|
| [004](../docs/history/004-dto-entity-responsibility.md) | DTO/Entity 책임 재정의 |
| [006](../docs/history/006-ddd-layered-architecture.md) | 도메인별 레이어드 아키텍처 전환 |
| [007](../docs/history/007-di-container-and-app-separation.md) | DI 컨테이너 계층화와 앱 분리 |
| [011](../docs/history/011-3tier-hybrid-architecture.md) | 3-Tier 하이브리드 아키텍처 전환 |
| [012](../docs/history/012-ruff-migration.md) | Ruff 도입 |
| [013](../docs/history/013-why-ioc-container.md) | 상속 대신 IoC Container를 선택한 이유 |

[ADR 인덱스 보기](../docs/history/README.md)

---

## Roadmap

### Phase 1: AI Agent Foundation
- [ ] FastMCP 인터페이스 ([#18](https://github.com/Mr-DooSun/fastapi-agent-blueprint/issues/18))
- [ ] PydanticAI 통합 ([#15](https://github.com/Mr-DooSun/fastapi-agent-blueprint/issues/15))
- [ ] pgvector 지원 ([#11](https://github.com/Mr-DooSun/fastapi-agent-blueprint/issues/11))
- [ ] JWT 인증 ([#4](https://github.com/Mr-DooSun/fastapi-agent-blueprint/issues/4))

### Phase 2: Production Readiness
- [ ] 구조화된 로깅 — structlog ([#9](https://github.com/Mr-DooSun/fastapi-agent-blueprint/issues/9))
- [ ] 환경별 설정 분리 ([#7](https://github.com/Mr-DooSun/fastapi-agent-blueprint/issues/7), [#8](https://github.com/Mr-DooSun/fastapi-agent-blueprint/issues/8), [#16](https://github.com/Mr-DooSun/fastapi-agent-blueprint/issues/16))
- [ ] 에러 알림 ([#17](https://github.com/Mr-DooSun/fastapi-agent-blueprint/issues/17))
- [ ] 워커 페이로드 스키마 ([#37](https://github.com/Mr-DooSun/fastapi-agent-blueprint/issues/37))
- [ ] CRUD 데이터 검증 ([#10](https://github.com/Mr-DooSun/fastapi-agent-blueprint/issues/10))

### Phase 3: Ecosystem
- [ ] 테스트 커버리지 확대 ([#2](https://github.com/Mr-DooSun/fastapi-agent-blueprint/issues/2))
- [ ] 성능 테스트 — Locust ([#3](https://github.com/Mr-DooSun/fastapi-agent-blueprint/issues/3))
- [ ] 서버리스 배포 ([#6](https://github.com/Mr-DooSun/fastapi-agent-blueprint/issues/6))
- [ ] WebSocket 문서 ([#1](https://github.com/Mr-DooSun/fastapi-agent-blueprint/issues/1))
- [ ] CHANGELOG ([#41](https://github.com/Mr-DooSun/fastapi-agent-blueprint/issues/41))

### Completed
- [x] 헬스 체크 엔드포인트
- [x] 도메인 자동 발견
- [x] 아키텍처 강제 (pre-commit)
- [x] 14개 Claude Code 스킬
- [x] Codex CLI workflow layer (`.codex/config.toml`, `.codex/hooks.json`, `.agents/skills/`)

스타를 눌러 진행 상황을 팔로우하세요!

---

## Contributing

개발 환경 설정, 코딩 가이드라인, PR 프로세스는 [CONTRIBUTING.md](../CONTRIBUTING.md)를 참고하세요.

---

## License

[MIT License](../LICENSE) -- 상업적 사용, 수정, 배포 자유.
