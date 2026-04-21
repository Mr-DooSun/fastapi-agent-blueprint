# 042. Optional Infrastructure — Selector + Lazy Factory Pattern in CoreContainer

- Status: Accepted
- Date: 2026-04-21
- Related issue: #101 (Make CoreContainer infra truly optional)
- Precursor to: #82 (`fab init` CLI — unblocked by this ADR)
- Extends: [ADR 029](archive/029-broker-abstraction-selector.md) (broker Selector was the first instance of this pattern)

## Summary

Every non-DB infrastructure in `CoreContainer` (storage, DynamoDB, S3 Vectors, embedding, LLM) now follows a single pattern:

1. A module-scope `_<infra>_selector()` function reads `settings` at resolution time and returns `"enabled"` or `"disabled"`.
2. A module-scope `_build_<infra>()` factory does a **lazy import** of the real client inside its body, so removing an optional extra (`pydantic-ai-slim`, etc.) does not break app boot when the infra is not configured.
3. The container exposes the provider as `providers.Selector(_selector, enabled=..., disabled=...)`.
4. The **disabled branch** is per-infra:
   - Stub instance for infras where consumer domains need graceful degradation (`embedding_client` → `StubEmbedder`; `llm_model` → `StubLLMModel` once #101 Part B lands).
   - `providers.Object(None)` for data-storage infras (`storage_client`, `storage`, `dynamodb_client`, `s3vector_client`) where a fake client would mislead.

Broker continues to use its three-way Selector (`sqs` / `rabbitmq` / `inmemory`) as the original template.

## Background

Before this ADR, `core_container.py` imported every optional infra client at module top and instantiated each as an unconditional `providers.Singleton(...)`, regardless of whether the user had configured that infra. Two real-world failures followed:

1. **`pyproject.toml` optional extras were a lie.** Even though `pydantic-ai-slim`, `taskiq-aws`, `taskiq-aio-pika` were listed under `[project.optional-dependencies]`, uninstalling them caused `ImportError` at app boot. Users could not opt out.
2. **Disabled-but-instantiated dead clients.** `LLMConfig(model_name="")` and friends were constructed with empty credentials when `LLM_*` was unset. The first call down the chain (e.g. `Agent(model="")` inside `ClassificationService`) raised a deep PydanticAI error rather than a clear "this infra is not enabled" signal.

The broker already had the right shape (see [ADR 029](archive/029-broker-abstraction-selector.md)). This ADR generalises that shape to the remaining five optional infras and records the per-infra disabled-branch rule so future additions don't re-litigate.

`#82` (interactive `fab init` CLI) was blocked on this: a CLI that "removes DynamoDB" would otherwise have to physically rewrite `core_container.py`. After this ADR lands, the CLI becomes a thin `.env` scaffolder (or is unnecessary — see #82 re-evaluation).

## Decision

### 1. Pattern shape (all five infras)

```python
# module scope
def _dynamodb_selector() -> str:
    return "enabled" if settings.dynamodb_access_key else "disabled"


def _build_dynamodb_client(access_key, secret_access_key, region_name, endpoint_url):
    # Lazy import — removing the matching optional extra (boto3 in this case,
    # pydantic-ai-slim for llm/embedding) does not break import of this module.
    from src._core.infrastructure.persistence.nosql.dynamodb.dynamodb_client import (
        DynamoDBClient,
    )
    return DynamoDBClient(
        access_key=access_key or "",
        secret_access_key=secret_access_key or "",
        region_name=region_name or "ap-northeast-2",
        endpoint_url=endpoint_url,
    )


# in CoreContainer class body
dynamodb_client = providers.Selector(
    _dynamodb_selector,
    enabled=providers.Singleton(
        _build_dynamodb_client,
        access_key=settings.dynamodb_access_key,
        secret_access_key=settings.dynamodb_secret_key,
        region_name=settings.dynamodb_region,
        endpoint_url=settings.dynamodb_endpoint_url,
    ),
    disabled=providers.Object(None),
)
```

Key discipline:

- Selector functions read `settings` **at call time**, not at import time, so tests can monkeypatch a settings field to flip the branch.
- Factory imports live **inside the function body**, never at module top. `try/except ImportError` with an install hint is used only where the dependency itself might be missing (`pydantic-ai` for embedding/LLM — see `broker.py` for the original template).
- Factory signatures type settings fields as `str | None` (their real type) and use `value or default` fallbacks, since pyright cannot see the Selector invariant that guarantees non-None in the enabled branch.

### 2. Per-infra disabled-branch strategy

| Infra | Disabled branch | Reason |
|---|---|---|
| `storage_client`, `storage` | `providers.Object(None)` | No current consumer; fake storage would make saved uploads silently vanish. Future consumers must guard or declare storage mandatory. |
| `dynamodb_client` | `providers.Object(None)` | A fake DynamoDB client would accept writes that never persist; user debugging would blame the wrong layer. |
| `s3vector_client` | `providers.Object(None)` | Same as DynamoDB. The `docs` domain already falls back to in-memory via its own `chunk_vector_store` selector, so the S3 client genuinely goes unused when disabled. |
| `embedding_client` | `Singleton(StubEmbedder, dimension=...)` | Consumer domains (`docs`) need to answer questions even without an embedding provider. `StubEmbedder` already exists (keyword bag-of-words). |
| `llm_model` | `providers.Object(None)` in this PR; `Singleton(StubLLMModel)` after #101 Part B | `classification` / `docs` need graceful degradation once `StubLLMModel` exists. Intermediate None does not regress: today's empty-string path also fails at request time. |

The rule of thumb: **stub when the disabled path must still serve traffic; None when the disabled path should never be touched.** Data stores fall in the second bucket because a fake that accepts writes is worse than a `NoneType` error at the call site.

### 3. Drop `llm_config` / `embedding_config` as standalone providers

Previously each infra exposed both a config VO (`LLMConfig` / `EmbeddingConfig`) and the client it configured. Nothing outside `core_container.py` referenced the config providers. The new build functions construct the VO locally and return the client directly, removing two unused entries from the container's public surface. The VO classes themselves are unchanged and still used inside the infra layer.

### 4. Selector functions read computed Settings properties

`settings.llm_model_name` and `settings.embedding_model_name` are `str | None` computed properties that already return `None` when provider + model are not both set. Selectors use these (not raw `llm_provider` fields) as the single source of truth for "is this infra enabled?", matching the semantics already established by the `docs` domain's embedder selector.

## Alternatives Considered

### A.1 — `providers.Selector` + `providers.Object(None)` with top-level imports kept

Replace the unconditional `providers.Singleton` with a Selector, but keep the `from ... import DynamoDBClient` at module top. Rejected: acceptance criterion for #101 was "boot with optional extras uninstalled → no ImportError". Top-level imports survive that uninstall and violate it. This is the minimum-viable rewrite and it does not satisfy the goal.

### A.2 — Lazy factory without Selector (bare `providers.Singleton(_factory)` that returns `None` when disabled)

```python
def _build_dynamodb_client():
    if not settings.dynamodb_access_key:
        return None
    from ... import DynamoDBClient
    return DynamoDBClient(...)

dynamodb_client = providers.Singleton(_build_dynamodb_client)
```

Rejected: dependency-injector introspection (`.provided`, `.override`, `.reset`) becomes awkward when the Singleton can return `None` — `.provided.<attr>` on `None` fails silently. Selector encodes the branch choice in the DI graph, which is what downstream overrides expect. Also, having the disabled path be a `providers.Object(None)` (not a Singleton call) means zero allocation — the `None` literal is returned directly.

### A.3 — Selector + lazy factory (chosen)

Combines (1) lazy import inside the factory with (2) Selector for branch encoding. Satisfies acceptance criterion and keeps DI introspection honest. Mirrors the existing `broker` pattern (ADR 029) and the lazy imports already present in `build_llm_model` / `broker.create_sqs_broker`.

### B — Single StubClient class per infra (`StubDynamoDBClient`, `StubS3VectorClient`)

Considered and rejected for data stores. Stubs for "write-then-read" data stores must decide whether to persist in memory or to silently drop — both mislead. A user who writes a row and queries it back, receiving it intact, will not suspect that real DynamoDB was never touched. `None` plus an explicit guard at the call site ("this domain requires DYNAMODB to be configured") is honest. Stubs make sense only where the consumer's workflow is still meaningful without a real backend — currently that's embedding (similarity over random vectors approximates keyword overlap) and LLM (templated response from retrieved chunks).

## Consequences

- **Boot-time guarantee:** with only `DATABASE_ENGINE=sqlite` set and all optional extras uninstalled (`pydantic-ai-slim`, `taskiq-aws`, `taskiq-aio-pika`), the app imports cleanly and `/docs` serves OpenAPI. Regression-guarded by `tests/integration/test_optional_infra.py`.
- **Domain degradation is localised.** `docs` already degrades via its domain-level Selector (kept in place as a self-contained example). `classification` still fails at request time when `LLM_*` is unset — #101 Part B replaces the `llm_model` disabled branch with `StubLLMModel` to close that gap.
- **Every new optional infra uses this pattern by default.** The `/new-domain` skill templates (`/claude/skills/new-domain/`, `.codex/new-domain`) will be updated in #101 Part B so scaffolded domains ship with Selector + stub where they declare an LLM or Embedding dependency.
- **`#82` unblocked.** Any future CLI that offers "remove DynamoDB" only needs to unset `DYNAMODB_*` in the scaffolded `.env`; no source rewriting. `#82` scope may shrink to "thin `.env` scaffolder" or be closed entirely — decision deferred to post-merge re-evaluation.
- **`pyproject.toml` cleanup (nicegui, boto3 → optional extras) is out of scope** for this ADR. Filed as a separate follow-up issue; it is a user-facing UX change (admin dashboard mount decision, aws-installation matrix) and deserves its own design pass.
