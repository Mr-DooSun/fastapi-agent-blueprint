# AI Infrastructure Overview

> Temporary design document for cross-session context transfer.
> Covers the full scope of issues #15, Langfuse integration, and AI Usage Tracking.
> After all three issues are complete, merge into project-dna.md via `/sync-guidelines` and archive this file.

## Architecture Diagram

```
PydanticAI Agent execution
│
├─ Path 1: OTEL spans ──→ Langfuse (self-hosted)
│   ├─ Ops team: step-by-step tracing (span waterfall)
│   ├─ Prompt designers: live edit, version control, SDK fetch
│   └─ Ops team: model-level cost analysis
│
└─ Path 2: result.usage() ──→ Self DB (ai_usage_log)
    ├─ Customers: per-org AI call history
    ├─ Customers: real-time usage/cost dashboard
    ├─ Customers: billing justification
    └─ Ops team: per-org cost monitoring (NiceGUI admin)
```

## Technology Choices

| Component | Choice | Why | ADR |
|-----------|--------|-----|-----|
| Agent Framework | PydanticAI v1.0+ | Pydantic-native structured output, OTEL standard, FastAPI DI philosophy, v1.0 stable | [037](../../docs/history/037-pydanticai-agent-integration.md) |
| Observability | Langfuse (self-hosted) | MIT full OSS, tracing + prompt mgmt + cost API — only tool covering all three | [038](../../docs/history/archive/038-llm-observability-dual-path.md) |
| Customer Billing | Self-owned `ai_usage` domain | Business-critical data cannot depend on external system | [038](../../docs/history/archive/038-llm-observability-dual-path.md) |

### Rejected Alternatives

- **LangChain**: Layer architecture conflict, heavy abstraction
- **Agno**: Non-OTEL tracing, not Pydantic-native
- **Direct SDK**: No abstraction, duplicated boilerplate across 10+ domains
- **LangSmith**: LangChain-centric, $39/user/month, limited self-hosting
- **Arize Phoenix**: No prompt management
- **Helicone**: Shallow tracing, proxy-based architecture

## Issue Dependencies

```
Issue #15 (PydanticAI Core)
├──→ Issue A (Langfuse OTEL + Prompt Management)    ← can start after #15
└──→ Issue B (AI Usage Tracking Domain)              ← can start after #15
                                                      A ∥ B (parallel)
```

## Key Design Decisions

1. **No BaseAgentProtocol** — PydanticAI Agent IS the abstraction. Double-wrapping adds complexity without value.
2. **No providers.Selector for LLM** — PydanticAI handles model switching internally via `model="provider:model-name"` string. This is "same class, different params" (like S3/MinIO), not "different classes, different signatures" (like Broker).
3. **No BaseAIService** — AI services are heterogeneous (classify, generate, query). No common CRUD interface to factor out.
4. **Hybrid DI** — dependency-injector for singletons (LLMConfig, database) + PydanticAI RunContext for per-request data (org_id, user_id).
5. **LLMConfig value object** — Domain layer cannot import Settings (infrastructure). `LLMConfig(model_name, api_key)` carries only what agents need.
6. **Dual-path independence** — OTEL→Langfuse failure does not affect customer billing. Self DB failure does not affect ops tracing.
7. **Optional infrastructure** — `LANGFUSE_ENABLED=false` disables tracing. PydanticAI is an optional dependency (`uv sync --extra pydantic-ai`).

## File Map by Issue

### Issue #15: PydanticAI Core

**Modified**:
- `src/_core/config.py` — LLM_PROVIDER, LLM_MODEL, LLM_API_KEY, LLM_BEDROCK_* fields + validation
- `src/_core/infrastructure/di/core_container.py` — `llm_config` Singleton provider
- `pyproject.toml` — `pydantic-ai` optional dependency group
- `_env/local.env.example` — LLM environment variables

**New**:
- `src/_core/domain/value_objects/llm_config.py` — `LLMConfig` frozen dataclass
- `src/_core/infrastructure/llm/exceptions.py` — `LLMException` hierarchy
- `src/classification/` — Prototype AI domain (full domain scaffold)
- `docs/history/037-pydanticai-agent-integration.md`
- `docs/history/archive/038-llm-observability-dual-path.md`

### Issue A: Langfuse OTEL + Prompt Management

**Modified**:
- `src/_core/config.py` — LANGFUSE_ENABLED, LANGFUSE_PUBLIC_KEY, LANGFUSE_SECRET_KEY, LANGFUSE_HOST + validation
- `src/_core/infrastructure/di/core_container.py` — `langfuse_client`, `prompt_service` providers
- `src/_apps/server/bootstrap.py` — OTEL initialization at startup
- `src/_apps/worker/bootstrap.py` — OTEL initialization at startup
- `pyproject.toml` — `langfuse` optional dependency group (langfuse, opentelemetry-*)

**New**:
- `src/_core/infrastructure/langfuse/langfuse_client.py` — SDK wrapper (lazy import)
- `src/_core/infrastructure/langfuse/otel_setup.py` — OTEL TracerProvider + Langfuse OTLP exporter
- `src/_core/infrastructure/langfuse/prompt_service.py` — Prompt fetch + cache + fallback
- `src/_core/infrastructure/langfuse/exceptions.py` — LangfuseException hierarchy
- `docker-compose.langfuse.yml` — Self-hosted Langfuse stack (PG:5433, ClickHouse, Redis:6380, MinIO:9090, web:3000)

### Issue B: AI Usage Tracking Domain

**New**:
- `src/ai_usage/` — Full domain (auto-discovered):
  - `domain/dtos/ai_usage_dto.py` — AiUsageDTO
  - `domain/protocols/ai_usage_repository_protocol.py` — Extended with aggregate queries
  - `domain/services/ai_usage_service.py` — BaseService + custom summary/org queries
  - `infrastructure/database/models/ai_usage_model.py` — ai_usage_log table (BigInteger PK, indexed org_id)
  - `infrastructure/repositories/ai_usage_repository.py` — Custom `select_usage_summary`, `select_usage_by_org`
  - `interface/server/routers/ai_usage_router.py` — GET /v1/usage, /usage/summary, /usage/{id}
  - `interface/admin/` — BaseAdminPage config + pages
- `src/_core/common/usage_tracker.py` — `track_agent_usage` async context manager
- Alembic migration for `ai_usage_log` table

## Patterns to Follow

| Pattern | Reference Implementation | Key File |
|---------|--------------------------|----------|
| Settings validation (partial config group) | Embedding provider validation | `src/_core/config.py:339-366` |
| Lazy import for optional deps | OpenAI embedding client | `src/_core/infrastructure/embedding/openai_embedding_client.py` |
| Exception hierarchy | EmbeddingException family | `src/_core/infrastructure/embedding/exceptions.py` |
| CoreContainer provider registration | Embedding Selector | `src/_core/infrastructure/di/core_container.py:105-119` |
| Domain auto-discovery | discover_domains() | `src/_core/infrastructure/discovery.py` |
| Admin page (BaseAdminPage) | User admin | `src/user/interface/admin/` |
| Domain scaffold (reference) | User domain | `src/user/` |
