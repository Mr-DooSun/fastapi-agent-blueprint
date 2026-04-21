# Project Status

> Last synced: 2026-04-21 via /sync-guidelines

## Current Version Context
- Latest release: v0.3.0 (2026-04-10)
- Active domains: user (reference domain), classification (prototype), docs (RAG consumer example, #80)
- Infrastructure: RDB (PostgreSQL/MySQL/SQLite), DynamoDB, Storage (S3/MinIO), S3 Vectors, InMemory Vectors (quickstart), Embedding (PydanticAI + StubEmbedder fallback), LLM (PydanticAI Agent + TestModel stub fallback via `build_stub_llm_model`), RagPipeline (+ StubAnswerAgent), Broker (SQS/RabbitMQ/InMemory). All non-DB infras are optional via `providers.Selector` + lazy factories (ADR 042).

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
