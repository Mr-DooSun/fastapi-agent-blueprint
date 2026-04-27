# AI Infrastructure Overview

> Temporary design document for cross-session context transfer.
> Covers the full scope of issues #15 (PydanticAI core), observability (#74 split), and AI Usage Tracking (#75).
> After all three are complete, merge into project-dna.md via `/sync-guidelines` and archive this file.
>
> **2026-04-28 update**: ADR 038 (Langfuse 1st-class) superseded by ADR 046 (OTEL core + Langfuse opt-in recipe + prompt domain defer). Architecture diagram and technology table updated accordingly.

## Architecture Diagram

```
PydanticAI Agent execution
│
├─ Trace path: OTEL spans ──→ OTLP backend (backend-agnostic)
│   │   Backends: Jaeger / Grafana Tempo / Arize Phoenix / Langfuse (opt-in)
│   │
│   ├─ Base (otel extra): token usage, latency, input/output messages
│   │
│   └─ Langfuse opt-in recipe adds:
│       ├─ Prompt version → trace linkage (requires Langfuse SDK/API)
│       ├─ Evaluation scores and datasets
│       └─ A/B prompt label analysis
│
└─ Usage path: result.usage() ──→ Self DB (ai_usage_log)
    ├─ Customers: per-org AI call history
    ├─ Customers: real-time usage/cost dashboard
    ├─ Customers: billing justification
    └─ Ops team: per-org cost monitoring (NiceGUI admin)
```

## Technology Choices

| Component | Choice | Why | ADR |
|-----------|--------|-----|-----|
| Agent Framework | PydanticAI v1.0+ | Pydantic-native structured output, OTEL standard, FastAPI DI philosophy, v1.0 stable | [037](../../docs/history/037-pydanticai-agent-integration.md) |
| Trace output | OTEL (OTLP exporter) | Backend-agnostic; `Agent.instrument_all()` one line; any OTLP backend works | [046](../../docs/history/046-otel-core-langfuse-recipe-prompt-domain-defer.md) |
| Langfuse | Opt-in recipe | MIT OSS; adds prompt linking + eval + A/B analysis on top of OTEL traces; not required at quickstart | [046](../../docs/history/046-otel-core-langfuse-recipe-prompt-domain-defer.md) |
| Customer Billing | Self-owned `ai_usage` domain | Business-critical data cannot depend on external system | [046](../../docs/history/046-otel-core-langfuse-recipe-prompt-domain-defer.md) |
| Prompt domain | **Deferred** | No real demand yet (no non-developer editing, <3 prompts). `PromptSnapshot` VO defines the contract. | [046](../../docs/history/046-otel-core-langfuse-recipe-prompt-domain-defer.md) |

### OTEL Backend Comparison

Teams choosing an OTLP backend:

| Backend | Self-host | Prompt mgmt | Evaluation | Best for |
|---------|-----------|-------------|------------|----------|
| **Langfuse** | Docker Compose (5 services) | ✅ full | ✅ datasets, scores | Full LLMOps (prompt iteration + eval loop) |
| Arize Phoenix | Docker (single container) | ❌ | ✅ basic | Trace inspection + drift detection |
| Grafana Tempo | Docker | ❌ | ❌ | Existing Grafana stack |
| Jaeger | Docker (single container) | ❌ | ❌ | Simple trace inspection |

All accept OTLP — only the exporter endpoint changes. No agent code modifications required when switching.

### Rejected Alternatives

- **LangChain**: Layer architecture conflict, heavy abstraction
- **Agno**: Non-OTEL tracing, not Pydantic-native
- **Direct SDK**: No abstraction, duplicated boilerplate across 10+ domains
- **LangSmith**: LangChain-centric, $39/user/month, limited self-hosting
- **Helicone**: Shallow tracing, proxy-based architecture
- **Langfuse as mandatory** (ADR 038): 5-component quickstart stack; violates ADR 042 opt-in principle

## Issue Dependencies

```
Issue #15 (PydanticAI Core) — COMPLETED
├──→ #74-A (OTEL core setup)                         ← split from #74
│       └──→ #74-B (Langfuse opt-in recipe doc)      ← depends on #74-A
└──→ #75 (AI Usage Tracking Domain)                  ← can run parallel to #74-A/B
        └──→ #97 (simple-chatbot example)             ← depends on #75
```

Note: `#74-A` and `#74-B` are placeholder names; actual issue numbers assigned after #74 closes.

## Key Design Decisions

1. **No BaseAgentProtocol** — PydanticAI Agent IS the abstraction. Double-wrapping adds complexity without value.
2. **No providers.Selector for LLM** — PydanticAI handles model switching internally via `model="provider:model-name"` string.
3. **No BaseAIService** — AI services are heterogeneous (classify, generate, query). No common CRUD interface to factor out.
4. **Hybrid DI** — dependency-injector for singletons (LLMConfig, database) + PydanticAI RunContext for per-request data (org_id, user_id).
5. **LLMConfig value object** — Domain layer cannot import Settings (infrastructure). `LLMConfig(model_name, api_key)` carries only what agents need.
6. **OTEL path independence** — OTEL→backend failure does not affect customer billing. Self DB failure does not affect tracing.
7. **Optional infrastructure** — `OTEL_ENABLED=false` (default) means zero overhead at quickstart. `uv sync --extra otel` enables tracing.
8. **Prompt domain deferred** — `PromptSnapshot(name, version, content, source, external_ref, metadata)` VO defines the consumer contract. Build the domain when: non-developer live edit is required, OR 3+ prompts need simultaneous version management.
9. **prompt_version is metadata, not a registry** — Nullable `prompt_version` in `ai_usage_log` is a billing/analytics label. Labels can move; it is not a reproducible prompt reference. Exact reproduction requires the deferred prompt domain.

## File Map by Issue

### Issue #15: PydanticAI Core (COMPLETED)

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
- `docs/history/archive/038-llm-observability-dual-path.md` ← superseded by ADR 046

### Issue #74-A / #136: OTEL Core Setup (SHIPPED — PR #136)

**Modified**:
- `src/_core/config.py` — `otel_enabled`, `otel_exporter_otlp_endpoint` fields + partial-config validator
- `src/_apps/server/bootstrap.py` — `_maybe_configure_otel(service_name)` call
- `src/_apps/worker/bootstrap.py` — `_maybe_configure_otel(service_name)` call
- `pyproject.toml` — `otel` optional extra (`opentelemetry-api/sdk/exporter-otlp-proto-grpc >=1.40.0`)

**New**:
- `src/_core/infrastructure/observability/otel_setup.py` — `configure_otel(settings, service_name)` + `Agent.instrument_all()`
- `_env/local.env.example` + `_env/quickstart.env.example` — `OTEL_ENABLED`, `OTEL_EXPORTER_OTLP_ENDPOINT`
- `docs/operations/observability-otel.md` — Jaeger/Tempo/Phoenix quickstart + HTTP exporter swap

### Issue #74-B: Langfuse Opt-in Recipe (PENDING, depends on #74-A)

**New**:
- `docker-compose.langfuse.yml` — Langfuse stack (PG:5433, ClickHouse, Redis:6380, MinIO:9090, web:3000)
- `Makefile` — `observability-langfuse` target
- `docs/operations/observability-langfuse.md` — OTLP endpoint config + note: prompt linking requires Langfuse SDK in addition to OTLP

### Issue #75: AI Usage Tracking Domain (PENDING)

**New**:
- `src/ai_usage/` — Full domain (auto-discovered):
  - `domain/dtos/ai_usage_dto.py` — AiUsageDTO
  - `domain/protocols/ai_usage_repository_protocol.py` — Extended with aggregate queries
  - `domain/services/ai_usage_service.py` — BaseService + custom summary/org queries
  - `infrastructure/database/models/ai_usage_model.py` — ai_usage_log table (nullable prompt ref columns, no FK)
  - `interface/server/routers/ai_usage_router.py` — GET /v1/usage, /usage/summary, /usage/{id}
  - `interface/admin/` — BaseAdminPage config + pages
- `src/_core/common/usage_tracker.py` — `track_agent_usage` async context manager
- `src/_core/domain/value_objects/prompt_snapshot.py` — `PromptSnapshot` Pydantic ValueObject
- Alembic migration for `ai_usage_log` table (with nullable prompt_name/version/source/external_prompt_ref)

**ai_usage_log schema changes vs ADR 038**:

| ADR 038 (removed) | ADR 046 (replaced with) | Reason |
|-------------------|-------------------------|--------|
| `prompt_id` FK | `prompt_name String(200) nullable` | No FK lock-in before prompt domain exists |
| — | `prompt_version String(50) nullable` | Langfuse-compatible label string (not integer) |
| — | `prompt_source String(20) nullable` | `"inline"` / `"langfuse"` / `"self"` / None |
| — | `external_prompt_ref String(500) nullable` | Langfuse prompt UUID or other external ref |

### Issue #97: simple-chatbot Example (PENDING, depends on #75)

- Inline `SYSTEM_PROMPT` constant — no prompt domain dependency
- `tokens_used` in response for educational purposes
- Comment: "Production usage tracking: see ai_usage domain (#75)"

## Patterns to Follow

| Pattern | Reference Implementation | Key File |
|---------|--------------------------|----------|
| Optional infra (Settings + Selector) | Embedding provider | `src/_core/config.py` + `core_container.py` |
| Lazy import for optional extras | OpenAI embedding client | `src/_core/infrastructure/embedding/openai_embedding_client.py` |
| Bootstrap conditional init | `_maybe_bootstrap_admin()` | `src/_apps/server/bootstrap.py` |
| Pydantic ValueObject (frozen, validated) | EmbeddingConfig or VectorQuery | `src/_core/domain/value_objects/` |
| Domain auto-discovery | discover_domains() | `src/_core/infrastructure/discovery.py` |
| Admin page (BaseAdminPage) | User admin | `src/user/interface/admin/` |
