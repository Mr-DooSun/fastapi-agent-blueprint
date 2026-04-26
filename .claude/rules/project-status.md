# Project Status

> Last synced: 2026-04-26 via /sync-guidelines (ADR 045 hybrid harness target architecture + Default Coding Flow + Phase 1 14×3 skill wrapper sync; examples/todo + examples profile + plan-feature approach options)

## Current Version Context
- Latest release: v0.4.0 (2026-04-21)
- Active domains: user (reference domain), classification (prototype), docs (RAG consumer example, #80)
- Contributor examples: `examples/todo/` (minimal CRUD, mirrors `src/user/` layout, copy into `src/` to run — see [`examples/README.md`](../../examples/README.md))
- Infrastructure: RDB (PostgreSQL/MySQL/SQLite), DynamoDB, Storage (S3/MinIO), S3 Vectors, InMemory Vectors (quickstart), Embedding (PydanticAI + StubEmbedder fallback), LLM (PydanticAI Agent + TestModel stub fallback via `build_stub_llm_model`), RagPipeline (+ StubAnswerAgent), Broker (SQS/RabbitMQ/InMemory), Structured logging (structlog + asgi-correlation-id). All non-DB infras are optional via `providers.Selector` + lazy factories (ADR 042). `nicegui`는 `admin` extra, `boto3`/`aioboto3`는 `aws` extra (#104).

## Recent Major Changes (since v0.3.0)
| Feature | Issue | Impact |
|---------|-------|--------|
| NiceGUI Admin Dashboard | #14 | New interface layer: admin/ (configs + pages) |
| Environment Config Validation | #53 | Settings model_validator, strict mode for stg/prod |
| Flexible RDB Config | #7 | DatabaseConfig.from_env(), multi-engine support |
| DynamoDB Support | #13 | BaseDynamoRepository, DynamoModel, DynamoDBClient |
| Broker Abstraction | #8 | providers.Selector for SQS/RabbitMQ/InMemory |
| BaseService 3-TypeVar | ADR 011 | Generic[CreateDTO, UpdateDTO, ReturnDTO] restoration |
| Password Hashing | - | hash_password/verify_password in _core.common.security |
| Serena Removal & Pyright Adoption | #63 | pyright-lsp 기본 코드 인텔리전스, PostToolUse 포맷팅 훅, tool-agnostic 스킬 전환 |
| Codex CLI Harness & Hybrid C Skills | #66 | Shared AGENTS.md, docs/ai/shared/ reference layer, 14 Hybrid C skill migrations |
| S3 Vectors Support | #70 | BaseS3VectorStore, VectorModel, S3VectorClient, VectorQuery/VectorSearchResult |
| Embedding Service Abstraction | #69 | Selector pattern (OpenAI/Bedrock), BaseEmbeddingProtocol, auto-dimension |
| Text Chunking | #69 | semantic-text-splitter, chunk_text/chunk_text_by_tokens |
| ADR 035/036 | #69 | Embedding abstraction + text chunking design decisions |
| Storage Abstraction | #58 | STORAGE_TYPE env var, S3/MinIO parameter switching, Settings computed properties |
| PydanticAI Agent Integration | #15 | Agent structured output, classification prototype, LLMConfig + build_llm_model |
| PydanticAI Embedder Transition | ADR 039 | PydanticAIEmbeddingAdapter replaces per-provider clients, EmbeddingConfig VO |
| Bedrock Credential Support | #15 | LLMConfig with per-service AWS credential injection, model_factory |
| Zero-config Quickstart | #78 | `make quickstart` + `make demo`, ENV=quickstart with SQLite + InMemory broker + auto create_all, Settings defaults for zero-infra boot |
| RAG Pattern + docs Domain | #80 | `_core/domain/services/rag_pipeline.py` (Generic[TChunk] orchestrator), `_core/domain/dtos/rag.py` (BaseChunkDTO, CitationDTO, QueryAnswerDTO), `_core/domain/protocols/answer_agent_protocol.py`, `_core/infrastructure/rag/` (StubEmbedder, StubAnswerAgent, PydanticAIAnswerAgent), `_core/infrastructure/vectors/` (BaseInMemoryVectorStore), `src/docs/` consumer (document CRUD + query), `make demo-rag`, VECTOR_STORE_TYPE env var, [ADR 040](../../docs/history/040-rag-as-reusable-pattern.md) |
| ADR Consolidation | #83 | 40 ADRs → 14 core + 29 archived under `docs/history/archive/`, new `docs/history/README.md` core-reading-order guide |
| Optional Infrastructure (CoreContainer) — Part A | #101 | `providers.Selector` + lazy factories for all 5 non-broker optional infras (storage, DynamoDB, S3 Vectors, embedding, LLM). Disabled branches: `providers.Object(None)` for data stores, `StubEmbedder` for embedding. `llm_config` / `embedding_config` dropped from public container surface. [ADR 042](../../docs/history/042-optional-infrastructure-di-pattern.md), AGENTS.md "Optional Infrastructure" reference section |
| Optional Infrastructure — Part B | #101 | `build_stub_llm_model()` factory returns PydanticAI `TestModel` (or `None` if `pydantic-ai` extra not installed). `ClassificationService` now degrades gracefully when `LLM_*` unset. `docs/ai/shared/scaffolding-layers.md` gains "Optional AI Infra Variant" section teaching the domain-level Selector+stub pattern for new-domain scaffolding |
| Structured Logging | #9 | `structlog` + `asgi-correlation-id` 파이프라인을 server/worker bootstrap에 통합. `configure_logging()`, `RequestLogMiddleware` + `CorrelationIdMiddleware` (server), `StructlogContextMiddleware` (worker)로 task/correlation id contextvars 바인딩. `LOG_LEVEL` / `LOG_JSON_FORMAT` env var (dev/local/quickstart → console, stg/prod → JSON). `DATABASE_ECHO` → `logging.getLogger("sqlalchemy.engine").setLevel(INFO)`로 변환해 double-emit 제거. `generic_exception_handler`가 `print(traceback)` 대신 `logger.exception("unhandled_exception", ...)` 구조화 기록 |
| Admin extra split | #104 | `nicegui` → `[admin]` extra 이동. `_maybe_bootstrap_admin()`이 `ImportError` 시 `admin_mount_skipped` 구조화 로그만 남기고 skip, 서버는 계속 boot. `make setup`이 `--extra admin` 기본 설치. CI `minimal-install` 잡이 extras 미설치 시 `/admin` 라우트 비마운트 회귀를 가드 |
| AWS extra split | #104 Part 2 | `boto3` / `aioboto3` / `types-aiobotocore-*` → `[aws]` extra 이동. 4개 AWS client 모듈 (`ObjectStorageClient`, `ObjectStorage`, `DynamoDBClient`, `S3VectorClient`)은 `__init__` / lazy singleton에서 `aioboto3` / `boto3`를 lazy import. CoreContainer Selector가 disabled 분기에서 `None`을 반환하므로 `aws` extra 미설치 + 관련 env var 미설정 시 lazy import가 아예 발화하지 않음. `make setup`이 `--extra aws` 기본 설치 |
| Responsibility-Driven Refactor | ADR 043 (pre-v0.5.0) | 12개 책임 혼동 지점 정리 (9 Phases). 주요 변경: (1) `error_mapper.py` infra ACL 확립 — domain service 예외 전파, FastAPI handler에서 매핑; (2) `ClassifierProtocol` + `PydanticAIClassifier` + `StubClassifier` — ADR 040 패턴 전면 정렬; (3) `_core/infrastructure/ai/providers.py` 신규 — parse_model_name + provider builder 단일화; (4) `AdminCrudServiceProtocol` + `extra_services_config` — admin 타입 안정성 + `_resolve_query_service` workaround 제거; (5) Bootstrap conductor 분해 (private functions); (6) `BaseEmbeddingProtocol` / `BaseVectorStoreProtocol` → `typing.Protocol`; (7) `src/_apps/server/testing.py` — 테스트 DI override 공개 API |
| Quality Gate Skill Restructure | #113 | `/review-pr` / `/review-architecture` / `/security-review` 통합 review flow + 공통 review contract (`Scope / Sources Loaded / Findings / Drift Candidates / Next Actions / Completion State / Sync Required`). `/sync-guidelines`는 review follow-up 또는 standalone 모드 둘 다 지원하는 closure 단계로 명시 |
| Plan-feature Approach Options | #116 | `/plan-feature` workflow에 Phase 1 "Approach Options" 추가 (2-3개 후보 제시 + trade-off + 추천). 기존 Phase 0(Requirements)→1(Architecture)→2(Security)→3(Tasks)이 0→1(Approach)→2(Architecture)→3(Security)→4(Tasks)로 재번호 |
| examples/todo + Examples Profile | #112, #119 | `examples/{name}/`는 `src/{domain}/` 레이아웃을 그대로 미러링하지만 production test baseline(factories/integration/e2e)을 강제하지 않는 contributor reference. `/review-architecture`가 examples profile을 인식해 §5 Test Coverage(단일 unit test 허용)와 §2 Auth(생략 허용) 항목을 완화. 자동 발견 대상이 아니므로 `cp -r examples/todo src/todo` 후 `make quickstart`로 시연 |
| Hybrid Harness Target Architecture | #117 (ADR 045) | 7-step Default Coding Flow (`framing → approach options → plan → implement → verify → self-review → completion gate`)을 AGENTS.md § 신설. exception token vocabulary (`[trivial]`/`[hotfix]`/`[exploration]`/`[자명]`/`[긴급]`/`[탐색]`)으로 trivial work에만 escape. Default Flow는 sandbox/approval/`.codex/rules`/safety hook/Absolute Prohibitions 보다 하위. Phase 0+1: 4 design doc (matrix/operating-model/migration-strategy + ADR) + 14×3 skill wrapper에 Default Flow Position section 추가. Phase 2~5는 별도 issue (UserPromptSubmit token parser / Claude PostToolUse Edit\|Write + Codex Stop changed-files / Stop completion gate / shared governor module). |

## Architecture Violation Status
- Domain → Infrastructure import: CLEAN
- Mapper class: CLEAN
- Entity pattern: CLEAN

## Not Yet Implemented
- JWT/Authentication
- RBAC/Permissions
- File Upload (UploadFile)
- Rate Limiting (slowapi)
- WebSocket
