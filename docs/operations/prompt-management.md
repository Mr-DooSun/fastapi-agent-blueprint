# Prompt Management Runbook — Editing Agent Personas in Langfuse

This document covers how to let operators change the persona of the built-in
agents without a deploy
([#447](https://github.com/Mr-DooSun/fastapi-agent-blueprint/issues/447),
[ADR 066](../history/066-runtime-prompt-provider-langfuse-opt-in.md)).

Like every non-DB infrastructure in this blueprint it is **optional** — with
`PROMPT_PROVIDER` unset the personas are the text shipped in code and the
zero-config quickstart is unchanged
([ADR 042](../history/042-optional-infrastructure-di-pattern.md)).

> **Langfuse write access is production access.** With this feature on, whoever
> can edit a prompt *and* move the label the app serves can change what the
> agents do in production, without a code review. Restrict who can promote to
> `production` before enabling it — see [Security notes](#security-notes).

## What is editable

Two prompts are resolved at runtime. Only the persona — the first part of the
agent's instructions — comes from Langfuse.

| Prompt name | Agent | Code default (fallback) |
|---|---|---|
| `docs_answer` | RAG answer agent (`PydanticAIAnswerAgent`) | `_PERSONA` in `src/_core/infrastructure/rag/pydantic_ai_answer_agent.py` |
| `classification` | Classifier (`PydanticAIClassifier`) | `_PERSONA` in `src/classification/infrastructure/classifier/pydantic_ai_classifier.py` |

**Not editable**, by design:

- **The boundary tail** (`RAG_INSTRUCTIONS_TAIL`, `CLASSIFIER_INSTRUCTIONS_TAIL`
  in `src/_core/infrastructure/llm/prompt_boundaries.py`) — the guidance telling
  the model to treat wrapped user and document content as untrusted data. The
  app appends it in code **after** whatever persona was resolved, on every call.
  An edited persona can add guidance; it cannot remove or override the tail.
- Input escaping, the prompt-injection input guard and the output guards
  ([ADR 051](../history/051-runtime-llm-guardrails.md)) — unchanged.
- The user prompt format, output schema, and model selection.
- The `examples/*` chatbots — they keep inline prompts.

**Variables are not supported.** The persona is used verbatim; the app never
calls Langfuse's `compile()`. A `{{variable}}` placeholder in the prompt reaches
the model literally, so do not use them.

**Prompt resolution only happens when an LLM is configured.** Without
`LLM_PROVIDER` + `LLM_MODEL`, the docs and classification containers select
stub agents, which call no model and resolve no prompt.

## Enabling

```bash
uv sync --extra langfuse   # plus the extras you already use, e.g. --extra pydantic-ai
```

`uv sync` removes extras you do not name, so list every extra the deployment needs.

| Variable | Required | Meaning |
|---|---|---|
| `PROMPT_PROVIDER` | yes | `langfuse`. Unset → personas from code. Any other value is rejected at boot. |
| `LANGFUSE_PUBLIC_KEY` | yes | Langfuse project public key |
| `LANGFUSE_SECRET_KEY` | yes | Langfuse project secret key — a credential |
| `LANGFUSE_BASE_URL` | yes | e.g. `https://cloud.langfuse.com` or your self-hosted URL. Required so credentials never default to Langfuse Cloud by accident |
| `PROMPT_LABEL` | no | Label to serve. Default `production` |
| `PROMPT_CACHE_TTL_SECONDS` | no | Per-process cache TTL. Default `60`, must be ≥ 0. `0` disables caching and puts a Langfuse round-trip on every agent call |

Boot validation rejects `PROMPT_PROVIDER=langfuse` with any of the three
`LANGFUSE_*` values missing, and rejects `LANGFUSE_*` values set **without**
`PROMPT_PROVIDER` (they would otherwise be silently ignored).

```bash
PROMPT_PROVIDER=langfuse \
LANGFUSE_PUBLIC_KEY=pk-lf-... \
LANGFUSE_SECRET_KEY=sk-lf-... \
LANGFUSE_BASE_URL=http://localhost:3000 \
LLM_PROVIDER=openai LLM_MODEL=gpt-4o-mini LLM_API_KEY=sk-... \
make dev
```

Langfuse Cloud or self-hosted is the operator's choice — the provider only needs
a base URL and a key pair. For local testing, `make observability-langfuse`
starts a self-hosted stack on `http://localhost:3000` and its project keys are in
`_env/langfuse.env` (see [observability-langfuse.md](observability-langfuse.md)).
That Compose file is a local-development recipe, not a production manifest.

The Langfuse client is created with tracing disabled. Prompt management and
trace export are independent: traces still go through the OTEL path
(`OTEL_ENABLED`), with or without this feature.

## Editing a prompt

1. In the Langfuse project, open **Prompts** and create a prompt of type
   **text** with the exact name `docs_answer` or `classification`. A chat-type
   prompt is not usable here and falls back to code text.
2. Start from the code default (the `_PERSONA` constant listed above) and edit.
   Write only the persona — do not paste the boundary tail; the app adds it.
3. Save. Each save creates a new, immutable version.
4. Give the new version the `staging` label and verify it from an environment
   started with `PROMPT_LABEL=staging`.
5. Promote by moving the `production` label to that version.

Each environment serves exactly one label, chosen by `PROMPT_LABEL`.

### Rolling back

Move the `production` label back to the previous version. Do not delete or edit
versions to roll back — versions are immutable and the ledger refers to them.

### Propagation delay

Every server and worker process keeps its own cache. After an edit, promotion or
rollback, a process does **not** switch on a timer. The refresh is triggered by
a call: the first call that finds its cached entry older than
`PROMPT_CACHE_TTL_SECONDS` (default 60 s) is still served the cached version and
starts a background refresh, and calls after that refresh completes get the new
version.

So the delay is "one TTL, then one more call" under steady traffic. Measured
against the real SDK (4.18.0) with a call every 0.25 s, the switch landed at
1.5 s with a 1 s TTL and at 5.6 s with a 5 s TTL. A process that has been idle
for longer than the TTL serves the **old** version on its first call after the
idle period, however long ago the label moved.

During that window different processes can serve different versions; the ledger
records which one each call used. To confirm a rollback has reached every
process, filter `ai_usage` by `prompt_version` rather than waiting a fixed time.

## Failure modes

A prompt fetch never fails a request, and a request never waits more than
3 seconds for one. Every failure below except the warm-cache row serves the code
persona and records `prompt_source=inline`.

| Situation | What happens | Log event (warning) |
|---|---|---|
| Langfuse slow or unreachable on a cold cache (first call in a process) | The call waits at most 3 s, then uses code text. The fetch carries on in a background thread — the SDK's HTTP client retries and honours `Retry-After` for up to minutes — and fills the cache when it lands. Concurrent calls for the same prompt join that one fetch instead of starting more | `prompt_fetch_timeout`, or `prompt_fallback_served` if the SDK gives up first |
| Langfuse unreachable on a warm cache | The **last fetched Langfuse version** keeps being served — not the code text — and the ledger still records it as `langfuse`. The SDK's background refresh fails and retries on the next expired call; its error record is filtered (below), so nothing is logged | none |
| `PROMPT_LABEL` not carried by any version (typo, label removed) | Langfuse answers 404 and does **not** fall back to another label, so a cold process serves code text on every call | `prompt_fallback_served` |
| Prompt not found under that name | Same as above | `prompt_fallback_served` |
| Prompt is chat-type, or the text is empty | Code text | `prompt_unusable_content` |
| Any other error raised by the client | Code text | `prompt_fetch_failed` (logs `exc_type` only) |

Each event carries `prompt_name` and `label`. The SDK's own three fetch-error
records (`Error while fetching prompt`, `Returning fallback prompt`, and the
background `PromptCacheRefreshConsumer encountered an error`) are dropped
by a filter on the `langfuse` logger, because they interpolate the HTTP response
body — which can carry whatever a proxy or Langfuse put there. The events above
replace them.

A sustained stream of `prompt_fallback_served` usually means a wrong
`PROMPT_LABEL`, prompt name, or `LANGFUSE_BASE_URL` — the feature then looks
"on" but every call runs the code persona.

## Verifying which prompt served a call

Every call by the real answer agent and classifier writes the resolved prompt
into the `ai_usage` ledger:

| Column | Langfuse-served call | Code-text call |
|---|---|---|
| `prompt_name` | `docs_answer` / `classification` | same |
| `prompt_version` | Langfuse version number | empty |
| `prompt_source` | `langfuse` | `inline` |
| `external_prompt_ref` | `"{name}@{version}"`, e.g. `docs_answer@7` | empty |

The admin **AI Usage** page shows the Prompt, Prompt Version and Prompt Source
columns. After a promotion, new rows show the new version once each process has
refreshed (one TTL plus one call — see [Propagation delay](#propagation-delay));
rows with `prompt_source=inline` while the feature is enabled are degraded calls.
`external_prompt_ref` identifies the exact text, because Langfuse versions are
immutable — use it to find the requests a bad version affected. The label is not
recorded per row, since labels move.

## Security notes

- **The persona is now operator data, not reviewed code.** Before this feature
  it was a `LiteralString` constant that went through code review. With it, the
  Langfuse project's edit and label permissions decide what the agents are told.
  Use Langfuse project roles so that only the people who may release a behaviour
  change can move the `production` label.
- **The tail and guardrails limit what an edit can remove, not what it can add.**
  A persona can still instruct the model to answer differently, be verbose, or
  ignore the documents; review persona changes as you would a release.
- **Keys are credentials.** Keep `LANGFUSE_SECRET_KEY` in gitignored env files.
  The app logs only the exception type on a fetch error.
