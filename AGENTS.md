# FastAPI Agent Blueprint — Shared Collaboration Rules

This file is the canonical source for project-shared AI collaboration rules.
Tool-specific harness files must reference this document instead of duplicating its contents.

## Tool-Specific Harnesses

- `CLAUDE.md` — Claude-specific hooks, plugins, slash skills, and tool usage guidance
- `.codex/config.toml` — Codex CLI project settings, profiles, feature flags, and MCP configuration
- `.codex/hooks.json` — Codex command-hook configuration
- `.agents/skills/` — repo-local Codex workflow skills
- `docs/ai/shared/` — shared workflow references consumed by both Claude and Codex
- `.mcp.json` — Claude-only MCP server configuration

### Process Governor Reference Documents

Issue #117 introduced a hybrid local process governor. The four documents below, indexed from [ADR 045](docs/history/045-hybrid-harness-target-architecture.md), define how default coding work is routed:

- [`docs/history/045-hybrid-harness-target-architecture.md`](docs/history/045-hybrid-harness-target-architecture.md) — top-level decisions + design-question resolutions
- [`docs/ai/shared/harness-asset-matrix.md`](docs/ai/shared/harness-asset-matrix.md) — living inventory of every harness asset and its bucket (Keep / Replace / Overlay / Drop)
- [`docs/ai/shared/target-operating-model.md`](docs/ai/shared/target-operating-model.md) — the target workflow, exception model, Claude/Codex alignment, and sample-workflow traces
- [`docs/ai/shared/migration-strategy.md`](docs/ai/shared/migration-strategy.md) — phased migration plan, rollback rules, and the asset-move ordering

Status (2026-04-27): Phase 5 (#124) ships the **Hybrid Harness v1** milestone. Governor *policy* now lives in a single shared package at [`.agents/shared/governor/`](.agents/shared/governor/); Claude / Codex hook scripts under `.claude/hooks/` and `.codex/hooks/` operate as thin shims that import from it. The hybrid governance model itself — escape-token vocabulary, dual-tool adapters, governor-review-log discipline — remains permanent (target-operating-model §3 / §7). Future governor changes belong in the shared package, not in per-tool inline copies (`tests/unit/agents_shared/test_governor_boundary.py` enforces this).

## Project Scale

This project is an AI Agent Backend Platform targeting enterprise-grade services with 10+ domains and 5+ team members.
All proposals and designs must consider scalability, maintainability, and team collaboration at this scale.

## Absolute Prohibitions

- No Infrastructure imports from the Domain layer
- No exposing Model objects outside the Repository
- No separate Mapper classes (inline conversion is sufficient)
- No Entity pattern — unified to DTO (background: [ADR 004](docs/history/004-dto-entity-responsibility.md))
- No modifying or deleting shared rule sources without cross-reference verification
  - Shared rule sources: `AGENTS.md`, `docs/ai/shared/`, `.claude/`, `.codex/`, and `.agents/`
  - Before changing them, verify no dependent tool configs or skills reference the changed content

Note: Domain → Interface **schema** imports (Request/Response types) are permitted.
When fields match, Request is passed directly to Service — creating a separate DTO is prohibited per ADR 004.

## Language Policy

The repository is contributor-facing for both internal teammates and external OSS contributors. Shared rule sources, harness configuration, and AI-governance artefacts must be readable by any contributor regardless of language environment.

The driving failure mode is Korean prose leaking into Tier 1 files via AI sessions running in Korean conversational mode. Other-language leaks have not been observed in this repository, so the **machine-enforced scope today is Korean (Hangul) prose**. The intent of the policy is broader — Tier 1 paths should be English-only — but only Korean is currently detected and blocked. Other-language detection (Chinese, Japanese, etc.) and encoded payloads (base64, HTML entities) are tracked as out-of-scope for this PR; if leaks of those forms appear, expand the checker first, then update this policy text to match.

### Tier 1 paths (Korean prose blocked; English encouraged for everything else)

All new prose, comments, docstrings, log strings, and user-facing terminal output under the following paths should be written in English; **Korean prose is blocked by the pre-commit hook**:

- `AGENTS.md`, `CLAUDE.md`, `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`, `SECURITY.md`
- `docs/ai/shared/**` (including `governor-review-log/**`)
- `docs/history/**` (every ADR and archive entry)
- `.claude/rules/**`, `.claude/hooks/**`, `.claude/skills/**`
- `.codex/rules/**`, `.codex/hooks/**`
- `.agents/**` (skills and the shared governor package)
- `.github/pull_request_template.md` and `.github/workflows/**`

The path list above is the **canonical scope of the language-policy checker** (`tools/check_language_policy.py::TIER1_GLOBS`). It overlaps with — but is not identical to — Tier A + Tier B of [`governor-paths.md`](docs/ai/shared/governor-paths.md). The governor-paths file controls cross-tool review triggers (every file under `.claude/**`, `.codex/**`, `.agents/**` triggers); the language-policy checker scopes to *files where prose is realistic* — Markdown, Python, shell, and the PR template / CI workflows. Config files like `.codex/hooks.json`, `.claude/settings.json`, and `.codex/config.toml` are intentionally outside the language-policy scope today; if Korean leaks into a settings string, treat it as a checker-extension follow-up rather than a policy violation.

### Two narrowly-scoped exceptions

The escape-token vocabulary `[trivial]/[자명]`, `[hotfix]/[긴급]`, `[exploration]/[탐색]` (see § Default Coding Flow → Exception Tokens) is machine-parseable and pinned by `^\s*\[(trivial|hotfix|exploration|자명|긴급|탐색)\](?:\s|$)`. The Korean half of each token, and references to that vocabulary in parser source, docstrings, and the token table itself, are permitted in Tier 1 paths under this token-scoped allowlist. The allowlist is scoped per-file in `tools/check_language_policy.py::TOKEN_LITERALS_BY_FILE` so a token literal cannot launder Korean prose elsewhere.

A second, narrowly-scoped carve-out covers **locale data files** explicitly listed in `tools/check_language_policy.py::LOCALE_DATA_FILES` (currently only `.agents/shared/governor/locale.py`). These files are the canonical runtime source for translated terminal output and may contain Korean (and future other-language) translation strings by design — see § Exemptions below for invariants.

### Two specific prohibitions

1. **No hidden Korean rationale** in Tier 1 paths — Korean text inside HTML comments, backtick-quoted attribute values, or hand-written metadata is **blocked by the line-grep checker**. Korean smuggled through base64 / HTML entities / other encodings is **not** detected today; the policy intent rejects them, but enforcement is best-effort. Hidden Korean rationale recreates information asymmetry between Korean-reading and non-Korean-reading contributors — the exact failure mode this policy exists to prevent.
2. **No new Korean prose lines, even when "just adding a translation for the team"** — except inside files explicitly listed in `tools/check_language_policy.py::LOCALE_DATA_FILES`. If translation matters for a specific document, create a sibling file (e.g. `docs/README.ko.md` is the existing reference pattern) and link to it. Tier 1 documents themselves stay English.

### Exemptions

- `README.md` — the Korean-language link label pointing to `docs/README.ko.md` is an i18n affordance pointing to a deliberately translated sibling document. `README.md` is intentionally not in the Tier 1 glob.
- `docs/README.ko.md` itself and any future `docs/*.{lang}.md` translation files (parallel translations, not in-line bilingualism).
- `docs/ai/shared/governor-review-log/**` — Korean text inside a line prefixed with `> Original user/owner statement (ko, verbatim):`, `> Original reviewer verdict (ko, verbatim):`, or `> Historical Korean excerpt (ko, verbatim):` is preserved provenance. English normalised meaning must follow on the next line. Multi-line preserved Korean must repeat the prefix on every line.
- Locale data files listed in `tools/check_language_policy.py::LOCALE_DATA_FILES` (currently `.agents/shared/governor/locale.py`) — these files are the canonical runtime source for locale translations. Korean translation strings are permitted *only* inside the language mapping values (enforced by `tests/unit/agents_shared/test_locale.py::test_locale_py_korean_only_in_locale_ko_dict_values`); comments, docstrings, identifiers, and the English table must remain ASCII. Adding a new locale data file requires updating `LOCALE_DATA_FILES`, this bullet, and adding a regression test.

### AI-when-editing rule

When you (an AI agent — Claude or Codex) edit any Tier 1 path:

- All new prose, comments, docstrings, log strings, error messages, and user-facing terminal output **must be English**, regardless of the language of the surrounding user prompt. Korean prose specifically is hard-blocked by the pre-commit hook.
- If the user instructs you in Korean (or any other language) to add a non-English note to a Tier 1 file, refuse and translate. Cite this section.
- The bilingual-token exception applies only to literal token vocabulary and references to it, in the per-file allowlist scope (`TOKEN_LITERALS_BY_FILE`). The locale-data-file exception (`LOCALE_DATA_FILES`) applies only to the language-mapping values inside `.agents/shared/governor/locale.py`; comments, docstrings, and English-table values must remain ASCII.
- Hidden Korean rationale (in HTML comments, backtick-quoted attributes, or any other line-visible form) is out of scope of the exception. The checker does not currently decode base64 / HTML entities — but smuggling Korean through those layers still violates policy intent and will be removed if found.

This rule is enforced by:

1. AI behaviour — `docs/ai/shared/skills/sync-guidelines.md` Phase 0; cross-referenced by `/review-pr`, `/review-architecture`, `/security-review`.
2. Pre-commit hook — `.pre-commit-config.yaml` `tier1-language-policy` invokes `tools/check_language_policy.py`.
3. CI — `.github/workflows/ci.yml` `architecture` job runs the hook via `uv run pre-commit run --all-files`.
4. Test — `tests/unit/agents_shared/test_language_policy.py` reuses the same checker for fixture-based regression coverage and asserts that this Tier 1 path list stays in sync with the checker's `TIER1_GLOBS` constant.

## Default Coding Flow

> Source of truth: [ADR 045](docs/history/045-hybrid-harness-target-architecture.md) + [`docs/ai/shared/target-operating-model.md`](docs/ai/shared/target-operating-model.md). Edit those first, then sync this section via `/sync-guidelines`.

Coding work proceeds through seven steps by default. Mandatory-by-default steps must be either performed or explicitly skipped via an escape token (see below). Other steps are conditional.

```
problem framing → approach options → plan → implement
                → verify → self-review → completion gate
```

Mandatory-by-default for implementation-class work: `framing`, `plan`, `verify`, `self-review`.
Conditionally mandatory (architecture commitment present): `approach options`.
Currently advisory (becomes mandatory in migration Phase 4): `completion gate`.

### Precedence

The Default Coding Flow ranks **below** the following four layers, in this order:

1. Active sandbox / approval policy / explicit user scope (e.g. read-only, review-only)
2. `.codex/rules/*` prefix rules (`forbidden` / `prompt`)
3. Safety hooks (security checks, destructive-command guards)
4. `## Absolute Prohibitions` (this document)

Escape tokens never override any of these four layers; they only reduce process burden inside the Default Coding Flow itself.

### Exception Tokens

A prompt may opt out of mandatory-by-default steps by carrying a leading exception token on its first line. Tokens are recognised after NFKC normalisation, case-insensitive, only as the leading bracketed token followed by whitespace or end-of-line.

| Token (English) | Token (Korean) | Meaning |
|---|---|---|
| `[trivial]` | `[자명]` | Self-evident change (typo, comment, rename); skip framing / approach / plan |
| `[hotfix]` | `[긴급]` | Urgent fix; skip approach options; verify still required |
| `[exploration]` | `[탐색]` | Read-only investigation or spike; nothing produces a commit |

Recognition regex: `^\s*\[(trivial|hotfix|exploration|자명|긴급|탐색)\](?:\s|$)`.

> The bilingual entries above (`[자명]`, `[긴급]`, `[탐색]`) and the locale-data carve-out (§ Language Policy → Exemptions → `LOCALE_DATA_FILES`) are the two narrowly-scoped exceptions to § Language Policy. The bilingual entries are machine-parseable and pinned by the regex; the per-file allowlist in `tools/check_language_policy.py` keeps Korean token references scoped to the files that legitimately need them.

Use of an exception token carries a follow-up obligation: the next commit message must record the rationale (one line is enough).

Auto-escapes (no token required): `changed_files == 0`, *general* doc-only changes, comment-only changes.

> **Doc-only carve-out** (Pillar 3 / Codex review R8 — added to prevent governance loosening). The doc-only auto-escape applies only to **general docs** such as `README.md`, `CHANGELOG.md`, contributor guides, and `docs/` content that is not policy or harness governance. The auto-escape does **not** apply to any path classified under Tier A of [`docs/ai/shared/governor-paths.md`](docs/ai/shared/governor-paths.md). Such changes go through normal `framing` → `plan` → `verify` → `self-review` even though they look doc-only, because they redefine the rules of the system.

### Self-Review Step — Cross-Tool Review Trigger (Pillar 2)

`self-review` is mandatory by default. When the change touches any path classified under **Tier A or Tier B (or Tier C, if introduced)** of [`docs/ai/shared/governor-paths.md`](docs/ai/shared/governor-paths.md) — and is not entirely covered by an exclusion in the same file — `self-review` must include a **cross-tool review** as a mandatory sub-step:

- run `codex exec -m gpt-5.5 --sandbox read-only "<review prompt>"` (or any cross-tool reviewer of equivalent capability) on the change set;
- capture the resulting `Findings` / `Drift Candidates` / `Sync Required` / Final Verdict in [`docs/ai/shared/governor-review-log/`](docs/ai/shared/governor-review-log/);
- address surfaced R-points or explicitly defer with rationale;
- the review artefact's location is link-cited from the PR description and the GitHub PR template's "Governor-Changing PR" section.

Non-governor-changing PRs are **exempt** from cross-tool review (issue #117 Non-Goals: avoid heavy ceremony).

### Skill Mapping

Each step routes to one or more skills. The shared procedure for each skill (under [`docs/ai/shared/skills/`](docs/ai/shared/skills/)) carries a "Default Flow Position" section documenting which step(s) the skill participates in, and tool-specific wrappers (`.claude/skills/`, `.agents/skills/`) mirror the same position. See [`target-operating-model.md`](docs/ai/shared/target-operating-model.md) §1 for the canonical mapping.

### Claude / Codex Alignment

This document is canonical. Tool-specific enforcement adapters are defined per migration phase in [`migration-strategy.md`](docs/ai/shared/migration-strategy.md). In particular, Codex enforcement is built around prompt-time routing and changed-file completion checks, not Bash-only `PostToolUse` matchers — skill-body instructions alone are insufficient because Codex does not read a skill until it is invoked.

## Reasoning-Level Consistency Guards

> Source: 4-round cross-review captured in [`governor-review-log/`](docs/ai/shared/governor-review-log/) (entry for the introducing PR). This section is the canonical Tier 1 surface; extend the log entry first when adding new guards.

This section applies to **every reasoning step — conversation, cross-review, document generation — across all tools**. It complements the PR-level governor (§ Default Coding Flow + `.agents/shared/governor/`), which operates on changed files. The guards here address miss patterns at the conversation level — patterns the PR-level governor does not cover.

The four guards (F, G, H, I) are constitutional guidance enforced by tool / human discipline. Phase 2 may add mechanical checks where feasible (G is the most amenable; F / H / I require natural-language analysis and remain text-only).

### Application order

```
H (intent classification) → F (evidence verification)
  → [if challenged conclusion] I (self-licensing check)
  → [for review output] G (closure classification)
```

Order is the natural flow, not a strict priority. The four guards are largely independent.

### F. Volatile Workspace Facts — Verify Before Consequential Assertion

**Policy.** Re-verify with tools immediately before making *consequential assertions*:

- corrective claims ("the user is mistaken")
- user-premise challenges ("that premise is wrong")
- exact line / path / PR-number / test-count claims
- mutable workspace facts (branch, git status, changed files, file existence)

System-prompt snapshots, prior memory entries, and prior-round summaries are evidence pointers, *not* current facts. Verify separately before quoting or asserting.

**Why.** During the 2026-04-28 evaluation, Claude treated a system-prompt snapshot ("Current branch: feat/121-…") as fact and challenged the user's premise; the actual current branch was `main`. The codex round-2 review (R6.1) caught this.

**How to apply.**

- Before issuing a corrective or challenging assertion, re-run the appropriate tool (`git status`, `gh pr view`, `Read`, `find`).
- Always re-verify before saying "the user is mistaken".
- Does not fire on general or exploratory questions — only on consequential cases.

### G. Cross-Review Results — Closure Classification

**Policy.** Every R-point produced by cross-review, cross-check, or external verification must be closed in one of three categories:

1. **Fixed** — handled by commit / edit / documentation.
2. **Explicitly deferred with rationale** — not handled, with the reason recorded.
3. **Rejected as non-issue** — reviewed and judged not to be a defect.

"Preserve" / "maintain" / "leave as-is" are **not** closure categories. A legitimate decision to retain something must still be classified as Deferred-with-rationale or Rejected.

**Why.** During the 2026-04-28 round-2 review, Claude framed an unaddressed gap as "preserved as cross-review asset"; the user corrected this in round 3 — cross-review exists to close gaps, not to preserve them.

**How to apply.** When recording a `governor-review-log` entry or reporting cross-review results, attach a closure status to every R-point. Saying "we will leave this as is" in prose is fine; the *category label* must be one of the three.

### H. Effect vs Process Question Discrimination

**Policy.** Classify each user question into one of two kinds:

- **Effect questions** — "is it working?", "did the error rate go down?", "what's the result?" (asking about state / quality / outcome).
- **Process questions** — "what should we do?", "what's next?", "what's the method?" (asking about action / plan / approach).

Effect questions must not be answered with process content (new actions, more ceremony). Mixed questions ("is it working, and what should we do next?") must be answered effect-first with evidence, then process options separately.

**Multi-round preservation.** For multi-round conversations, restate the original user question and stated success metric before proposing process changes. The original question must not be lost as round count grows.

**Why.** During the 2026-04-28 round 3, the user asked an effect question ("is the error rate going down?"); Claude answered with process content. Round 4's retrospective evidence (186 logged R / F points) demonstrated the effect question could in fact be answered with data.

**How to apply.**

- Classify before composing the response.
- Effect questions: answer with evidence or data. If no data exists, say so explicitly. Do not substitute process content.
- Process questions: answer with action candidates.
- Mixed questions: effect first, process second, separately labelled.

### I. Self-Licensing Detection — Sanity Check Before Defending a Challenged Conclusion

**Trigger.** This guard fires only when the user pushes back on a stated conclusion: a *correction*, *challenge*, or *evidence request* directed at that conclusion. General follow-up or clarifying questions do not fire it.

**Policy.** Before defending the conclusion, explicitly check:

1. Did the conclusion start from a stale or incorrect premise?
2. Is the reasoning circular — am I evaluating my own output by criteria I authored, or stacking new recommendations to defend earlier ones?
3. Could the user's intuition be a real domain signal that I am missing?

State the result of this check as the first sentence of the response, before any defence.

**Why.** During the 2026-04-28 evaluation, rounds 1 and 2 drifted toward adding ceremony; Claude defended this drift. Only when the user pushed back at round 3 ("is that really the conclusion?") did codex retract the entire round-2 list ("none of the six recommendations from round 2 should be retained as-is").

**How to apply.**

- On detected pushback, run the three-step check first, surface the result, then proceed.
- Re-verifying premises is the default; defence is conditional.
- General questions or requests for additional information do not fire this guard.

## Layer Architecture (3-Tier Hybrid)

- Default: Router → Service (extends `BaseService`) → Repository (extends `BaseRepository`)
- DynamoDB domain: Router → Service (extends `BaseDynamoService`) → Repository (extends `BaseDynamoRepository`)
- Complex logic: Router → UseCase (manually written) → Service → Repository
- UseCase criteria: multiple Service composition, cross-transaction boundaries, or other orchestration complexity
- When in doubt: start without UseCase, add it when complexity grows

## Responsibility Matrix

Each concern has exactly one home. Do not duplicate or split these across layers.

| Concern | Location | Rule |
|---------|----------|------|
| Pure business logic | `{domain}/domain/services/` | No SDK imports, no infra |
| Domain contracts (AI) | `{domain}/domain/protocols/` or `_core/domain/protocols/` | `typing.Protocol` + `@runtime_checkable` |
| Provider SDK calls | `_core/infrastructure/{llm,embedding,classifier,rag}/` | PydanticAI, boto3 SDK isolated here |
| Provider SDK exception translation | `_core/infrastructure/llm/error_mapper.py` | ACL — infra only, never domain |
| Provider helpers | `_core/infrastructure/ai/providers.py` | `parse_model_name`, `build_*_provider` |
| DI container, lazy factories | `{domain}/infrastructure/di/{domain}_container.py` | `_build_*` factories belong here |
| Bootstrap orchestration | `_apps/{server,worker}/bootstrap.py` | Private `_configure_*`, `_install_*`, `_setup_*` functions |
| Admin service contract | `_core/domain/protocols/admin_service_protocol.py` | `AdminCrudServiceProtocol` |
| Test DI overrides | `_apps/server/testing.py` | Public `override_database` / `reset_database_override` |

## Error Translation

Provider SDK exceptions (PydanticAI, boto3, openai, anthropic) must be translated to domain LLM exceptions in the **infrastructure layer**, never inside domain services.

- **Domain services**: let exceptions propagate — no `try/except` around provider calls
- **Infrastructure adapters** (e.g. `PydanticAIEmbeddingAdapter`): catch SDK exceptions and call `map_llm_error(exc)` (NoReturn — always raises a domain exception)
- **FastAPI `generic_exception_handler`**: catches all unhandled exceptions, calls `try_map_llm_error(exc)` (returns `Optional`) before falling through to 500
- **ACL module**: `src/_core/infrastructure/llm/error_mapper.py` — the only place that knows provider SDK class names

```
Provider SDK exception
  → propagates through domain service untouched
  → caught by FastAPI generic_exception_handler
  → try_map_llm_error(exc) → LLMException (mapped HTTP status)
  OR → 500 Internal Server Error (unrecognised exception)
```

## Optional AI Infra Pattern

All AI features (LLM classification, RAG answering, embedding) follow the same Protocol + Infra Adapter + Selector pattern. Background: [ADR 040](docs/history/040-rag-as-reusable-pattern.md) + [ADR 042](docs/history/042-optional-infrastructure-di-pattern.md).

**Pattern:**
1. `{domain}/domain/protocols/{feature}_protocol.py` — `typing.Protocol` contract
2. `_core/infrastructure/{feature}/pydantic_ai_{feature}.py` — real adapter (or domain-specific if DTO coupling is tight)
3. `_core/infrastructure/{feature}/stub_{feature}.py` — deterministic stub for quickstart/no-LLM
4. Domain container uses `providers.Selector(real=..., stub=...)` to branch

**Reference implementations:**
- RAG: `AnswerAgentProtocol` → `PydanticAIAnswerAgent` / `StubAnswerAgent` (in `_core/infrastructure/rag/`)
- Classifier: `ClassifierProtocol` → `PydanticAIClassifier` / `StubClassifier` (in `classification/infrastructure/classifier/`)

**Selector selector function convention:** `def _classifier_selector() -> str: return "real" if settings.llm_model_name else "stub"`

## Admin Service Contract

Admin pages consume domain services through `AdminCrudServiceProtocol` (`_core/domain/protocols/admin_service_protocol.py`). Any `BaseService` subclass satisfies this protocol automatically.

- `_service_provider: Callable[[], AdminCrudServiceProtocol]` — main CRUD service, wired by bootstrap
- `extra_services_config: dict[str, str]` — declare additional services by alias → container attr name
- `_get_extra_service(alias: str)` — resolve and call an extra service (e.g. `"query"` → `docs_query_service`)

**Example** (docs domain needing a query service alongside the main CRUD service):
```python
docs_admin_page = BaseAdminPage(
    domain_name="docs",
    extra_services_config={"query": "docs_query_service"},
)
# In page handler:
service = docs_admin_page._get_extra_service("query")
```

## Optional Infrastructure

Every non-DB infra in `CoreContainer` is optional — toggle via env vars, no code change. When a group is disabled, the provider returns a stub (where graceful degradation matters) or `None` (for data stores). Background: [ADR 042](docs/history/042-optional-infrastructure-di-pattern.md).

| Infra | Enable flag | Disabled behavior |
|---|---|---|
| Storage (S3 / MinIO) | `STORAGE_TYPE=s3` or `minio` | `storage_client()` / `storage()` return `None` |
| DynamoDB | `DYNAMODB_ACCESS_KEY` set | `dynamodb_client()` returns `None` |
| S3 Vectors | `S3VECTORS_ACCESS_KEY` set | `s3vector_client()` returns `None` |
| Embedding | `EMBEDDING_PROVIDER` + `EMBEDDING_MODEL` both set | `embedding_client()` returns `StubEmbedder` (keyword bag-of-words) |
| LLM | `LLM_PROVIDER` + `LLM_MODEL` both set | `llm_model()` returns PydanticAI `TestModel` via `build_stub_llm_model` when `pydantic-ai` is installed, `None` otherwise |
| Broker | `BROKER_TYPE=sqs` / `rabbitmq` / `inmemory` | Defaults to `inmemory` — no external broker required |

**Consumer rule:** data-store clients (`None`-returning) require an explicit guard at the call site when your domain needs them; stub-returning infras just work (but signal "stub" via startup warning logs). Use `providers.Selector` in your domain container to branch between real and stub paths if needed — `src/docs/infrastructure/di/docs_container.py` is the reference pattern.

**Package-level extras:** optional runtime infras are also gated at the `pyproject.toml` level. Install only what you need — `uv sync --extra admin` for the NiceGUI dashboard, `--extra aws` for object storage / DynamoDB / S3 Vectors (boto3 + aioboto3 + type stubs), `--extra sqs` / `--extra rabbitmq` for those broker backends, `--extra pydantic-ai` for LLM / Embedding, etc. When an extra is absent, the matching bootstrap path silently skips and the server continues to boot — the 4 AWS client modules (`ObjectStorageClient`, `ObjectStorage`, `DynamoDBClient`, `S3VectorClient`) import cleanly via `TYPE_CHECKING` + lazy `__init__` imports, and `CoreContainer` resolves the matching Selector to `None` when the env var is unset. `make setup` installs `--extra admin --extra aws` by default for full dev coverage; `make quickstart` only needs `--extra admin` (SQLite + InMemory broker). Every other extra opts in explicitly.

## Structured Logging

Logging is always-on (unlike Optional Infrastructure) and shared across server + worker. Pipeline: `structlog` ProcessorFormatter + `asgi-correlation-id`. Background: #9.

- **Logger acquisition** — all new code uses `structlog.stdlib.get_logger(__name__)`; legacy `logging.getLogger(__name__)` calls still flow through the same pipeline via the ProcessorFormatter bridge but new modules should not add more.
- **Renderer switching** — `LOG_JSON_FORMAT` env var (None → auto: dev/local/quickstart → console, stg/prod → JSON; True/False force override). Controlled by `settings.effective_log_json`.
- **Sensitive-field logging is prohibited** — `password`, `token`, `access_key`, `secret_key`, `api_key`, and any field that Response `model_dump(exclude={...})` strips must NOT appear in `logger.info(event, password=...)`, `logger.bind(...)`, or `structlog.contextvars.bind_contextvars(...)`. The JSON renderer ships structlog kwargs verbatim to aggregators.
- **SQLAlchemy echo** — `DATABASE_ECHO=true` is translated to `logging.getLogger("sqlalchemy.engine").setLevel(INFO)` (not a separate handler) to avoid double-emit between stdlib and structlog pipelines. Do not enable in stg/prod unless secret filtering is in place — bound query parameters reach the log stream.
- **Bootstrap entrypoints** — server: `configure_logging()` → `RequestLogMiddleware` + `CorrelationIdMiddleware` (Starlette adds late-registered middleware as the outermost layer, so CorrelationId is registered last intentionally). Worker: `configure_logging()` → `StructlogContextMiddleware` binds task id / correlation id into contextvars.
- **Env vars** — `LOG_LEVEL` (DEBUG/INFO/WARNING/ERROR), `LOG_JSON_FORMAT` (None/True/False).

## Terminology

- **Request/Response**: API communication schema (`interface/server/schemas/`)
- **Payload**: Worker message contract schema (`interface/worker/payloads/`) — background: [ADR 016](docs/history/archive/016-worker-payload-schema.md)
- **DTO**: Internal data carrier between layers — Repository → Router (`domain/dtos/`)
- **Model**: DB table mapping, never exposed outside Repository (`infrastructure/database/models/`)
- **DynamoModel**: DynamoDB table mapping, never exposed outside Repository (`infrastructure/dynamodb/models/`)

## Conversion Patterns

### Write Direction (Request → DB)

- Router → Service: `entity=item` (pass Request directly)
- Service → Repository: pass entity as-is, or transform via `entity.model_copy(update={...})` when domain logic requires it
- Repository → DB: `Model(**entity.model_dump(exclude_none=True))`

### Read Direction (DB → Response)

- DB → Repository: `DTO.model_validate(model, from_attributes=True)`
- Repository → Service → Router: pass DTO as-is
- Router → Client: `Response(**dto.model_dump(exclude={"password"}))`

### Worker Direction (Message → Service)

- Message → Task: `Payload.model_validate(kwargs)`
- Task → Service: pass payload as-is when fields match
- Task → Service: `DTO(**payload.model_dump(), extra=...)` when fields differ

## Write DTO Creation Criteria

- When fields match Request: pass Request directly, no separate Create/Update DTO needed
- When fields differ (auth context injection, derived fields, etc.): create a separate DTO in `domain/dtos/`
  - Example: `CreateUserDTO(**item.model_dump(), created_by=current_user.id)`

## Security Principles

- Do not expose internal details (traceback, DB schema, raw query) in production error responses
- Prevent OWASP Top 10 violations when writing code

## Common Commands

### Run

```bash
make quickstart   # zero-config evaluation (SQLite + InMemory broker)
make demo         # curl walkthrough against running quickstart
make dev          # real local dev (PostgreSQL via docker-compose)
make worker
make diagrams     # regenerate SVGs under docs/assets/architecture/
```

### Test

```bash
make test
make test-cov
make check
```

### Lint / Format

```bash
make lint
make format
make pre-commit
```

### Migration

```bash
make migrate
make migration
uv run alembic downgrade -1
uv run alembic current
```

## Drift Management

- `AGENTS.md` is the canonical source for shared rules; tool-specific harness docs must point here instead of re-copying rules
- Keep root `AGENTS.md` short and stable; when local context needs more detail, prefer `AGENTS.override.md` or named skills instead of expanding the root doc
- Codex memories are personal/session optimization only; do not treat them as a shared rule source
- Shared rule sources: `AGENTS.md`, `docs/ai/shared/`, `docs/ai/shared/skills/`, `.claude/`, `.codex/`, and `.agents/`
- Update related documentation in the same change when shared rules or harness behavior changes
  - `README.md`
  - `docs/README.ko.md`
  - `CONTRIBUTING.md`
  - `CLAUDE.md`
  - `docs/ai/shared/` and `docs/ai/shared/skills/`
  - `.claude/rules/` and `.claude/skills/` references when relevant
  - `.codex/hooks.json`, `.codex/rules/`, and `.agents/skills/` when relevant
- When modifying a skill procedure, verify both `.claude/skills/` and `.agents/skills/` wrappers reference the same shared procedure
  - For Hybrid C skills: `docs/ai/shared/skills/{name}.md` is the canonical source for the procedure
  - Claude and Codex wrappers must stay in sync with the shared procedure's Phase/Step structure
- If architecture or shared patterns change, inspect drift before closing the work
  - Claude workflow entry point: `/sync-guidelines`
  - Codex workflow: use `$sync-guidelines` or follow the documented verification steps in `README.md` / `CONTRIBUTING.md`
  - Both tools should run sync after architecture changes — not just the active tool
- Language drift: any new prose in non-token contexts under paths listed in § Language Policy → Tier 1 must be English. Bilingual escape tokens and locale data files (`LOCALE_DATA_FILES`) are the two narrowly-scoped exceptions. Run `python3 tools/check_language_policy.py` before closing the work to confirm zero violations.

### Skill Split Convention (Hybrid C)

When extracting shared skill procedures to `docs/ai/shared/skills/`:

**Wrapper keeps** (`.claude/skills/`, `.agents/skills/`):
- Tool-specific frontmatter (name, description, argument-hint, metadata, etc.)
- Phase/Step overview (1-2 line summary per phase — agent sees the full flow before reading external file)
- Tool-specific post-steps (e.g., Claude's `.claude/rules/*` update)
- User interaction flow when it differs between tools

**Shared procedure contains** (`docs/ai/shared/skills/{name}.md`):
- Detailed steps per phase (inspection targets, conditions, branching logic)
- Output format examples
- Checklists, file lists, grep patterns
- Cross-references to other `docs/ai/shared/` documents
