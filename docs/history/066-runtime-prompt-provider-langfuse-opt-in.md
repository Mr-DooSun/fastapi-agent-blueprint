# 066. Runtime Prompt Provider — Inline Default, Langfuse Opt-in, Code-Owned Boundary

- Status: Accepted
- Date: 2026-11-16 (decision and recording date)
- Record type: contemporaneous
- Decision evidence: approved Execution Packet on [#447](https://github.com/Mr-DooSun/fastapi-agent-blueprint/issues/447)
- Related issue: #447
- Amends / supersedes: amends [ADR 046](046-otel-core-langfuse-recipe-prompt-domain-defer.md) §4 (implements the deferred `get_active` contract) and §3 / Trade-offs (the meaning of `external_prompt_ref`). ADR 046 §1 (OTEL core), §2 (Langfuse trace recipe) and its rejection of a self-built editor remain in force.
- Related: [ADR 042](042-optional-infrastructure-di-pattern.md) (optional infra Selector), [ADR 051](051-runtime-llm-guardrails.md) (runtime guardrails)

## Summary

To let non-developers change agent personas without a deploy, we implement the
`get_active(name) -> PromptSnapshot` contract ADR 046 reserved as an optional
provider: inline (code text) by default, Langfuse by label when
`PROMPT_PROVIDER=langfuse`. Only the persona is editable; the prompt-injection
boundary guidance stays in code and is always appended last.

## Background

**Trigger.** ADR 046 §4 deferred the prompt domain until either "a non-developer
needs to edit prompts without code deployment" or "3+ distinct prompts require
version management". #447 records the first condition as met: planners and
operators need to tune prompts without a release, and the need is expected to
continue. The second condition is not met — two production prompts exist
(`docs_answer`, `classification`).

**Decision type.** Upfront design against a reserved contract, not a correction
after experience. ADR 046 already shipped the anchors: the `PromptSnapshot` VO,
the `PromptSource` vocabulary (`inline` / `langfuse` / `self`), the four nullable
prompt columns on the `ai_usage` ledger, and a `prompt_snapshot` parameter on
`track_agent_usage` that no production caller passed.

## Problem

1. Personas were `Final[LiteralString]` module constants passed to the
   PydanticAI `Agent` constructor. Changing one required a code change and a deploy.
2. The ledger could not say which prompt served a call, so a bad edit could not
   be traced to the requests it affected — the gap ADR 046 Problem §3 called out
   for multi-worker rollbacks.
3. Making prompt text runtime data must not weaken the LLM01 boundary. The
   persona and the "treat wrapped content as untrusted DATA" guidance were one
   `LiteralString` concatenation; an editable prompt that included the guidance
   would let an operator — or anyone holding the operator's credentials — delete it.

## Alternatives Considered

### A. Provider protocol, inline default + Langfuse opt-in — chosen

The shape ADR 046 §4 reserved, using the ADR 042 Selector + lazy factory. Langfuse
is MIT-licensed, self-hostable, and already the project's opt-in observability
recipe; its UI supplies the versioning, diff, label workflow and RBAC that ADR 046
Problem §3 listed as the real cost of a prompt editor.

### B. Logfire `ManagedPrompt` (via `pydantic-ai-harness`) — rejected for now

Native to PydanticAI, but commercial SaaS only, which conflicts with the
provider-neutral, self-hostable direction of ADR 046. It can be a second
implementation behind the same protocol later; nothing here forecloses it.

### C. Langflow — rejected

A visual workflow builder with its own runtime. Adopting it would replace the
PydanticAI agent stack rather than manage that stack's prompts.

### D. Self-built prompt domain + NiceGUI editor — rejected

Rejected by ADR 046 Problem §3 (diff, rollback, audit, variable validation, label
workflow, RBAC and concurrent-edit handling are the real scope), and it would
cross the "admin-panel product" non-goal. Nothing in #447 changed that argument.

## Decision

1. **Contract.** `PromptProviderProtocol.get_active(name, *, default) -> PromptSnapshot`
   in `src/_core/domain/protocols/prompt_provider_protocol.py`. The caller always
   passes the code persona as `default`, so a provider needs no registry and an
   unreachable backend degrades to code text. Implementations must not raise for a
   backend failure. The label is provider configuration (`PROMPT_LABEL`), not a
   per-call argument as #447 first sketched: no consumer needs a different label
   from the rest of its process.
2. **Selection (ADR 042).** `CoreContainer.prompt_provider` is a `providers.Selector`.
   Unset `PROMPT_PROVIDER` → `InlinePromptProvider` (returns `default`,
   `source="inline"`); `PROMPT_PROVIDER=langfuse` → `LangfusePromptProvider`. The
   disabled branch is a working provider rather than `None`, because a consumer
   always needs *a* prompt. The `langfuse` extra (`langfuse>=4.18.0,<5`) is imported
   lazily on the enabled branch only.
3. **Boot validation.** `PROMPT_PROVIDER=langfuse` requires `LANGFUSE_PUBLIC_KEY`,
   `LANGFUSE_SECRET_KEY` and `LANGFUSE_BASE_URL`. The base URL is required because
   the SDK default is Langfuse Cloud, which would silently send credentials off-site
   for a self-hosting operator. Any `LANGFUSE_*` credential without the provider is
   rejected (the notification-webhook precedent: credentials that do nothing are a
   misconfiguration). `PROMPT_LABEL` defaults to `production`;
   `PROMPT_CACHE_TTL_SECONDS` defaults to 60 and must be ≥ 0.
4. **Editable surface: persona only.** `compose_instructions(persona, tail)` in
   `prompt_boundaries.py` appends the code-owned tail (`RAG_INSTRUCTIONS_TAIL`,
   `CLASSIFIER_INSTRUCTIONS_TAIL`) after the resolved persona. `tail` is typed
   `LiteralString`, so pyright rejects runtime text in that slot. Instructions are
   passed per `agent.run(..., instructions=...)`, not at `Agent` construction:
   PydanticAI places constructor instructions before run-time ones, which would put
   an edited persona *after* the boundary guidance. Input escaping and the ADR 051
   guardrails are unchanged; the prompt-leak check now runs against the resolved
   instructions.
5. **Degrade, never fail, never wait long.** The Langfuse SDK `get_prompt` is
   synchronous and its knobs do not bound it: `max_retries` limits only the outer
   loop, while the generated HTTP client retries each attempt twice more and honours
   `Retry-After` up to 60 s per sleep (review R1 measured ~4 minutes against a 503).
   So the request never waits on the SDK call: each fetch runs on a daemon thread,
   single-flight per prompt name, and the request waits at most 3 s
   (`prompt_fetch_timeout`) before degrading while the fetch carries on and warms
   the cache. Daemon threads, not a pool, so a cold fetch sleeping on `Retry-After`
   cannot hold a shutdown and cannot starve the shared default executor. That claim
   is scoped to this cold-fetch path: the SDK's own warm-cache refresh consumer is
   joined at exit, so a refresh in flight during an outage can still delay process
   shutdown by its retry sleeps (review round 2 measured ~3 s) — SDK behaviour this
   provider does not control. A warm
   cache returns immediately and, after the TTL, serves the stale value while
   refreshing in the background; during an outage a warm process keeps serving the
   last fetched Langfuse version, not the code text. A raised exception, an SDK
   fallback (`is_fallback`), or non-text / empty content all return the inline
   snapshot and log a warning (`prompt_fetch_failed` with `exc_type` only,
   `prompt_fallback_served`, `prompt_unusable_content`). The SDK's own three
   fetch-error log records — two on the request path, one from the warm-cache
   refresh thread — are filtered out, because they interpolate the HTTP response
   body (review R2). The client is built with
   `tracing_enabled=False`: trace export stays on the OTEL path (ADR 046 §1).
6. **Ledger linkage.** The real answer agent and classifier pass the resolved
   snapshot to `track_agent_usage` on every call, inline included, filling
   `prompt_name`, `prompt_version`, `prompt_source` and `external_prompt_ref`. No
   migration: the columns exist since ADR 046 §3.
7. **`external_prompt_ref` = `"{name}@{version}"`** for Langfuse-served calls (null
   for inline). ADR 046 §3 and its Trade-offs assumed a stable Langfuse prompt UUID;
   the SDK prompt client exposes no id. Langfuse versions are immutable, so
   name + version identifies the exact text that served the call, which is the
   property the UUID was wanted for. Labels still move, so `prompt_version` alone
   remains analytics metadata, not a registry.

### Settled decisions from #447

- **Langfuse Cloud vs self-host** — left to the operator. The provider needs only a
  base URL and a project key pair; `docker-compose.langfuse.yml` remains a
  local-development recipe, not a production manifest.
- **Label convention and promotion rights** — `staging` → `production`, with
  `PROMPT_LABEL` selecting what a deployment serves. Who may move `production` is
  governed by Langfuse project RBAC, not by this repository.
- **Variables** — not supported. Personas are used verbatim; `compile()` is never
  called, so a `{{var}}` placeholder in a Langfuse prompt reaches the model
  literally. Validation of missing variables is therefore moot until a consumer
  needs templating, which would be its own decision.

### Out of scope

Per-tenant prompts (no tenancy model exists), a NiceGUI prompt editor, A/B traffic
routing (label analysis is possible through the ledger; routing is not built), the
`examples/*` chatbots (they stay inline as copy-flow standalones), and the stub
agents (they call no model and resolve no prompt).

## Rationale

The provider boundary is placed at the persona rather than at the whole
instruction string because the two halves have different owners. The persona is
product behaviour — tone, scope, format — which is exactly what operators were
asking to tune. The boundary tail is a security control whose correctness depends
on the escape-wrapping in `_format_prompt`; it changes only with that code, so it
stays in code. Splitting them lets the editable surface grow without the security
surface growing with it.

Degrading to inline rather than failing keeps ADR 042's promise that optional
infrastructure never takes the request path down. The cost is that a broken
Langfuse configuration is silent to users — which is why every degraded call
logs a warning and records `prompt_source=inline`.

### Self-check

- [x] Does this decision address the root cause, not just the symptom?
- [x] Is this the right approach for the current project scale?
- [x] Will a reader understand "why" 6 months from now without extra context?
- [x] Am I recording the decision process, or justifying a conclusion?

## Consequences

- **ADR066-G1** — The boundary tail is code-owned. A consumer that resolves a
  persona from a provider must compose instructions with `compose_instructions`
  (tail last, `LiteralString`) and pass them per run. Constructor `instructions=`
  combined with a runtime persona reverses the order and is a defect.
- **ADR066-G2** — A prompt provider never raises into the request path. Backend
  failure, fallback, and unusable content degrade to the caller's `default` with
  `source="inline"`; a provider must not record a backend version for a call that
  ran on code text.
- **ADR066-G3** — A consumer that resolves a prompt passes the snapshot to
  `track_agent_usage`, so the ledger can attribute a call to a prompt version.
- **ADR066-G4** — Langfuse is opt-in. Quickstart and every environment without
  `PROMPT_PROVIDER` behave as before, and the `langfuse` extra is imported only on
  the enabled branch.

**Trust-boundary change.** Before this ADR the persona was `LiteralString` text
that passed code review. With `PROMPT_PROVIDER=langfuse` it is operator data, so
write and promote access in the Langfuse project is equivalent to changing agent
behaviour in production. The tail and guardrails bound what an edit can remove,
not what it can add. Operators must restrict who can move the served label; the
runbook says so.

**Operational trade-offs.**
- Propagation is eventually consistent: each server and worker process holds its
  own SDK cache, so after an edit or rollback processes can serve different versions.
  The bound is not one TTL: the SDK refreshes stale-while-revalidate, triggered by a
  call, so a process switches one TTL *plus one call* after the change (measured:
  1.5 s at TTL 1 s, 5.6 s at TTL 5 s), and a process idle for longer than the TTL
  serves the old version on its first call afterwards. ADR 046 Problem §3 named
  this; the ledger's
  `external_prompt_ref` is now the way to identify affected calls.
- A cold-cache miss against a slow or down Langfuse delays a call by at most the
  3-second request deadline before degrading. `PROMPT_CACHE_TTL_SECONDS=0`
  puts that round-trip on every call.
- Langfuse answers 404 for a label no version carries and does not fall back to
  another label, so a `PROMPT_LABEL` typo degrades every call to code text,
  visible only as `prompt_fallback_served` warnings and `prompt_source=inline` rows.
- Enabling the `langfuse` extra moved the locked OpenTelemetry packages from 1.40
  to 1.45.2, shared with the `otel` extra.

**Decision basis** (per [adr-evidence.md](../ai/shared/adr-evidence.md)):

| Decision / claim | ADR, status and exact clause | Applicability / limits | Current evidence and disposition |
|---|---|---|---|
| `get_active` is the consumer contract | ADR 046 (Accepted) §4 | Prompt resolution for `_core` RAG and classification adapters | `PromptProviderProtocol`; conform (signature gains `default`) |
| Trigger to build prompt management | ADR 046 §4 trigger conditions | First condition only | #447 problem statement; new decision (this ADR) |
| No self-built editor | ADR 046 Problem §3 | Editing UI | Not built; conform |
| Optional infra Selector, working disabled branch | ADR 042 (Accepted) Decision §1–§2 | `CoreContainer.prompt_provider` | `core_container.py`, `test_core_container_selectors.py`, `test_optional_infra.py`; conform |
| Guardrails unchanged | ADR051-G1 | Answer agent and classifier | `test_adversarial_prompts.py`; conform |
| `external_prompt_ref` holds a stable UUID | ADR 046 §3, Trade-offs | Langfuse-served calls | SDK `BasePromptClient` has no id field; conflict → amended by Decision 7 |
| Hostile persona cannot displace the tail | ADR066-G1 | Both consumers | `test_pydantic_ai_answer_agent_prompt.py`, `test_pydantic_ai_classifier_prompt.py` |

**Limits of the evidence.** The Langfuse path is verified with a fake client in
`tests/unit/_core/infrastructure/prompt/test_prompt_providers.py` (success, `is_fallback`, exception, unusable content, label/TTL
pass-through, deadline and single-flight) and against the real SDK 4.18.0 over an
`httpx.MockTransport` (a 503 with `Retry-After: 60` returns in under 2 s; a 401 body
never reaches the logs). Propagation timing was measured against the real SDK and a
stand-in prompt API, not a running Langfuse server; a live round-trip is not part of
CI.

**Revisit when** a consumer needs prompt variables, a per-tenant prompt model
exists, traffic must be split between versions, or a second backend (for example
Logfire) is requested.
