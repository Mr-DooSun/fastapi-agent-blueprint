# Harness Asset Inventory Matrix

> Last synced: 2026-04-26 (initial inventory, ADR 045 + Phase 1)
> Source of truth: this is a **living inventory**. Update when assets are added, renamed, or removed. `/sync-guidelines` validates that this file matches the actual filesystem.
> Sibling docs: [ADR 045](../../history/045-hybrid-harness-target-architecture.md) · [target-operating-model.md](target-operating-model.md) · [migration-strategy.md](migration-strategy.md)

## Purpose

This matrix answers issue #117 Required Output #1: classify every harness asset into one of four buckets and record the evidence that justifies the classification. It is the input that constrains the Target Operating Model and Migration Strategy.

## Bucket Definitions

The four buckets defined in #117 are interpreted as follows. The original wording in the issue ("Replace — can be replaced by superpowers") is reinterpreted because superpowers is **not** an external package this repo adopts; it is a philosophy reference. See [ADR 045 §Background](../../history/045-hybrid-harness-target-architecture.md) and [archive/044](../../history/archive/044-superpowers-gstack-process-governor-evaluation.md).

| Bucket | Meaning | Example |
|---|---|---|
| **Keep** | Asset stays as-is. Project-specific value that no philosophy port can substitute. | `AGENTS.md`, `project-dna.md`, RDB-architecture skills |
| **Replace** | Asset is rewritten in place to absorb superpowers-style discipline. The file location is unchanged but its content is replaced. | (none in this initial inventory; reserved for future passes) |
| **Overlay** | Asset is preserved but the canonical execution path runs through the new Default Coding Flow. The asset becomes a *reference* that the flow consults, not a primary entry point. | `planning-checklists.md`, `plan-feature` skill, `onboard` skill |
| **Drop** | Asset is removed because it is duplicated, dead, or superseded. | (none in this initial inventory; reserved for future passes) |

## Classification Columns

Each asset is recorded with the following nine fields (issue #117 mandates seven; two more are added for Tier grouping and follow-up tracking).

| Column | Issue #117 mapping | Description |
|---|---|---|
| Asset | asset name | Filesystem path, repo-relative |
| Layer | (added) | Tier 0~4 grouping for readability |
| Current Role | current role | What this asset does in the running harness |
| Why It Exists | why it exists | The constraint or precedent that produced it (often an ADR or issue) |
| Replacement Feasibility | replacement feasibility | Could superpowers-style philosophy substitute it? `None` / `Partial` / `Full` |
| Bucket | (decision) | `Keep` / `Replace` / `Overlay` / `Drop` |
| Final Location | final ownership location | Where the asset lives after Phase 5 |
| Migration Risk | migration risk | `Low` / `Medium` / `High` with one-line rationale |
| Stability/Error-rate Impact | impact on error rate / stability | Net effect on the operational metrics targeted by issue #117 |
| Notes | (added) | Cross-reference to related ADR, issue, or follow-up phase |

---

## Tier 0 — Constitutional Assets

The shared constitution and the tool-level entry points. These files transitively define every downstream asset; they are unconditionally `Keep`.

| Asset | Bucket | Risk | Impact |
|---|---|---|---|
| `AGENTS.md` | Keep | Low (additive section only) | High |
| `CLAUDE.md` | Keep | Low | Medium |
| `.codex/config.toml` | Keep | Low | Medium |
| `.codex/hooks.json` | Keep | Low | Medium |
| `.claude/settings.json` | Keep | Low | Medium |
| `.claude/settings.local.json` | Keep | Low | Low |
| `.mcp.json` | Keep | Low | Low |
| `docs/history/045-hybrid-harness-target-architecture.md` | Keep | Low | High |
| `.github/pull_request_template.md` | Keep | Low | High |

### `AGENTS.md`

- **Current role**: Canonical shared collaboration rules. Every other harness file references this one.
- **Why it exists**: Cross-tool drift was previously handled by duplicating rules across `CLAUDE.md` and Codex-specific files. Centralised in this document during the Codex CLI adoption (#66).
- **Replacement feasibility**: None. Project-specific architecture and prohibitions cannot be substituted by an external philosophy.
- **Final location**: unchanged.
- **Migration risk**: Low. Phase 1 only adds `§ Default Coding Flow` and Tool-Specific Harnesses cross-links; nothing existing is rewritten.
- **Stability impact**: High. Default Flow precedence rules anchor every later phase.
- **Notes**: Phase 1 edit is the first time this file gains a process-layer section; previously it covered only architecture and conventions.

### `CLAUDE.md`

- **Current role**: Claude-specific harness guide; redirects to `AGENTS.md` for shared rules.
- **Why it exists**: Pre-existed AGENTS.md split (#66). Now an explicit Claude-only entry point.
- **Replacement feasibility**: None. Tool-specific guidance cannot be shared.
- **Final location**: unchanged.
- **Migration risk**: Low.
- **Stability impact**: Medium. Phase 1 update adds Default Flow cross-link; Phase 2 may add prompt-submit hook reference.
- **Notes**: Quality Gate Flow section becomes a redirect to Default Coding Flow once Phase 4 lands.

### `.codex/config.toml`

- **Current role**: Codex CLI sandbox / approval / web_search settings + MCP servers + research profile.
- **Why it exists**: #66 Codex adoption. Defaults: `sandbox_mode="workspace-write"`, `approval_policy="on-request"`, `web_search="disabled"`, `[profiles.research].web_search="live"`.
- **Replacement feasibility**: None.
- **Final location**: unchanged.
- **Migration risk**: Low. Phase 1 does not edit this file. Phase 5 may add hook configuration.
- **Stability impact**: High. Default Flow precedence rule (D1.1) explicitly subordinates the flow below this file's sandbox / approval configuration.
- **Notes**: Codex review (R7) emphasised that any web-search-requiring step must explicitly use `profiles.research`; the Phase 0.5 review itself was run under that profile.

### `.codex/hooks.json`

- **Current role**: Five Codex hook chains (SessionStart / UserPromptSubmit / PreToolUse Bash / PostToolUse Bash / Stop), each with a 30~120s timeout.
- **Why it exists**: Mirrors the Claude `.claude/settings.json` hooks structure adopted in #66.
- **Replacement feasibility**: None.
- **Final location**: unchanged.
- **Migration risk**: Medium starting Phase 2. UserPromptSubmit gets the exception-token parser; PostToolUse Bash matcher is insufficient for non-Bash edits (Codex R7) and may grow a second hook entry or be supplemented by Stop-side change-detection.
- **Stability impact**: High once hooks land.
- **Notes**: Codex R7 — schema validation of hook payloads must precede Phase 3 work.

### `.claude/settings.json`

- **Current role**: Four Claude hook chains (SessionStart / PreToolUse Edit|Write|Bash / PostToolUse Edit|Write / Stop) + plugin enablement (`pyright-lsp`).
- **Why it exists**: Established by #63 (Serena → pyright-lsp) and #66 cross-tool harness alignment.
- **Replacement feasibility**: None.
- **Final location**: unchanged.
- **Migration risk**: Medium starting Phase 3. New hooks attach to existing matchers; payload backward-compatibility must hold.
- **Stability impact**: High.
- **Notes**: PostToolUse matcher set is `Edit|Write` (not Bash-only as in Codex), so Phase 3 verification-first hook can attach here directly. Codex side requires a different shape — see migration-strategy.md.

### `.claude/settings.local.json`

- **Current role**: User-specific overrides; `.gitignore`d.
- **Why it exists**: #66 Codex adoption + Claude harness alignment. Local-only customisation.
- **Replacement feasibility**: None.
- **Final location**: unchanged.
- **Migration risk**: Low (file is gitignored — no PR can modify it).
- **Stability impact**: Low.
- **Notes**: Track only the existence of the file pattern; contents are user-private.

### `.mcp.json`

- **Current role**: Claude-only MCP server config (currently `context7`).
- **Why it exists**: Context7 stays as MCP per 2026-04 review (`docs/ai/shared/repo-facts.md`).
- **Replacement feasibility**: None.
- **Final location**: unchanged.
- **Migration risk**: Low.
- **Stability impact**: Low (does not interact with Default Flow).
- **Notes**: Codex MCP servers live under `.codex/config.toml [mcp_servers.*]`, not here.

### `docs/history/045-hybrid-harness-target-architecture.md`

- **Current role**: ADR 045 — top-level decisions for the hybrid harness target architecture (this initiative). Navigator to the three living docs.
- **Why it exists**: Issue #117 mandates a load-bearing decision record alongside the matrix / operating model / migration strategy.
- **Replacement feasibility**: None (an ADR is immutable history once accepted).
- **Final location**: unchanged.
- **Migration risk**: Low (immutable).
- **Stability impact**: High (every later phase cites this ADR).
- **Notes**: Self-classified — included in the matrix because the matrix is a living inventory and this ADR is itself a constitutional asset of the process layer.

### `.github/pull_request_template.md`

- **Current role**: GitHub PR template. Original purpose was simple change-summary + checklist. Round-4 (Pillar 5) added a "Governor-Changing PR" section that artefact-locks cross-tool review, self-application proof, and review-trail link.
- **Why it exists**: Round-4 review found that user-memory-only enforcement of cross-tool review is insufficient for new contributors and new sessions. PR template moves the requirement into a repo artefact.
- **Replacement feasibility**: None.
- **Final location**: unchanged.
- **Migration risk**: Low (additive section; non-governor-changing PRs delete the section).
- **Stability impact**: High (every PR sees the template; governor-changing PRs cannot easily skip the checklist).
- **Notes**: Pillar 5 of ADR 045's Self-Application Recovery.

---

## Tier 1 — Shared Reference Layer (`docs/ai/shared/`)

Twelve canonical reference documents that both Claude and Codex consume. Most are factual or architecture references (`Keep`). Three are process-discipline checklists that become *consulted* by the Default Coding Flow rather than primary entry points (`Overlay`).

| Asset | Bucket | Risk | Impact |
|---|---|---|---|
| `project-dna.md` | Keep | Low | High |
| `architecture-diagrams.md` | Keep | Low | Medium |
| `scaffolding-layers.md` | Keep | Low | High |
| `security-checklist.md` | Keep | Low | High |
| `test-patterns.md` | Keep | Low | High |
| `architecture-review-checklist.md` | Keep | Low | Medium |
| `ai-infrastructure-overview.md` | Keep | Low | Medium |
| `repo-facts.md` | Keep | Low | Medium |
| `test-files.md` | Keep | Low | Medium |
| `planning-checklists.md` | Overlay | Low | Medium |
| `drift-checklist.md` | Overlay | Low | Medium |
| `onboarding-role-tracks.md` | Overlay | Low | Low |
| `harness-asset-matrix.md` | Keep | Low | High |
| `target-operating-model.md` | Keep | Low | High |
| `migration-strategy.md` | Keep | Low | High |
| `governor-review-log/` (directory) | Keep | Low | High |
| `governor-paths.md` | Keep | Low | High |

### `project-dna.md`

- **Current role**: 906-line canonical pattern catalogue auto-extracted from the codebase. Sections §0~§14 cover directory structure, base classes, generics, CRUD, DI, conversions, security, features, routers, exception, admin, vector, embedding, LLM.
- **Why it exists**: Adopted as part of the Hybrid C harness so that both Claude and Codex read identical architecture references.
- **Replacement feasibility**: None — superpowers carries no project-specific architecture.
- **Final location**: unchanged.
- **Migration risk**: Low (read-only reference).
- **Stability impact**: High. Implementation skills resolve their procedure detail by reading from here.
- **Notes**: Section count and ADR cross-references must remain in sync with `/sync-guidelines` snapshot. New tiers (e.g. §15 Default Flow) would be additive.

### `architecture-diagrams.md`

- **Current role**: Mermaid diagrams for layer dependency, Write/Read flows, RDB / DynamoDB / S3 Vector tables. Re-rendered to SVG via `make diagrams`.
- **Why it exists**: Visual reference; surfaced by `architecture-review-checklist.md`.
- **Replacement feasibility**: None.
- **Final location**: unchanged.
- **Migration risk**: Low.
- **Stability impact**: Medium.
- **Notes**: Edits require `make diagrams` to refresh exports under `docs/assets/architecture/`.

### `scaffolding-layers.md`

- **Current role**: 295-line scaffolding manual: per-layer file list, paths, import rules. Source of truth for `/new-domain`.
- **Why it exists**: Hybrid C shared procedure for layer scaffolding. Carries the Optional AI Infra Variant section (post-ADR 042).
- **Replacement feasibility**: None.
- **Final location**: unchanged.
- **Migration risk**: Low. Phase 1 may add a "Default Flow Position" reference for `/new-domain`.
- **Stability impact**: High.
- **Notes**: Cited from `architecture-conventions.md` and the `/new-domain` skill.

### `security-checklist.md`

- **Current role**: 369-line OWASP-aligned security review reference. Surface for `/security-review`.
- **Why it exists**: Project-specific security stance (auth, OWASP Top 10, key-rotation rules).
- **Replacement feasibility**: None.
- **Final location**: unchanged.
- **Migration risk**: Low.
- **Stability impact**: High.
- **Notes**: `/security-review` skill reads this; no Default Flow change needed for Phase 1.

### `test-patterns.md`

- **Current role**: 144-line test pyramid + factory/fixture patterns. Cited by `/test-domain` and the test-baseline file inventory.
- **Why it exists**: Shared test conventions across domains.
- **Replacement feasibility**: None.
- **Final location**: unchanged.
- **Migration risk**: Low.
- **Stability impact**: High. Anchors the `verify` step of the Default Flow.
- **Notes**: Phase 3 verification-first hook will rely on this file's authoritative naming conventions for "what counts as a test for this change".

### `architecture-review-checklist.md`

- **Current role**: 107-line architecture-audit checklist. Surface for `/review-architecture`.
- **Why it exists**: Standardise the questions a domain or full-repo review must answer.
- **Replacement feasibility**: None.
- **Final location**: unchanged.
- **Migration risk**: Low.
- **Stability impact**: Medium.
- **Notes**: Examples-profile carve-out (`examples/todo`) was added 2026-04-26 — see `repo-facts.md`.

### `ai-infrastructure-overview.md`

- **Current role**: 117-line overview of LLM / Embedding / RAG / Vector / Classifier patterns.
- **Why it exists**: New-contributor orientation to the AI infra layer.
- **Replacement feasibility**: None.
- **Final location**: unchanged.
- **Migration risk**: Low.
- **Stability impact**: Medium.
- **Notes**: Pattern-pointer document; rarely edited.

### `repo-facts.md`

- **Current role**: Canonical sources index + tooling decisions log.
- **Why it exists**: Single document the drift checklist consumes.
- **Replacement feasibility**: None.
- **Final location**: unchanged.
- **Migration risk**: Low (additive only — Phase 1 adds the four new doc references).
- **Stability impact**: Medium.
- **Notes**: This file is updated whenever Tier 0/1 gain new entries.

### `test-files.md`

- **Current role**: 27-line baseline-test file checklist (factories / unit / integration / admin).
- **Why it exists**: Enforces minimum-viable test coverage for new domains.
- **Replacement feasibility**: None.
- **Final location**: unchanged.
- **Migration risk**: Low.
- **Stability impact**: Medium.
- **Notes**: Examples profile is exempted — short carve-out is documented here, not in the matrix.

### `planning-checklists.md`

- **Current role**: 211-line planning checklist for feature work (Requirements, Data Model, Business Rules, Security, Tasks). Currently consulted by `/plan-feature` only.
- **Why it exists**: Prevent planning omissions in implementation work.
- **Replacement feasibility**: Partial. Default Flow's `framing` and `plan` steps now route to a *subset* of these questions automatically; the full checklist remains as the deep-dive reference.
- **Bucket: Overlay** because the canonical entry point shifts from "user invokes `/plan-feature`" to "Default Flow routes the user through framing → plan, which references this checklist". The file content stays.
- **Final location**: unchanged.
- **Migration risk**: Low.
- **Stability impact**: Medium.
- **Notes**: After Phase 1, the `/plan-feature` skill body explicitly cites this checklist as Phase 0/2 supporting reference rather than the primary procedure.

### `drift-checklist.md`

- **Current role**: 189-line drift-detection items consumed by `/sync-guidelines`.
- **Why it exists**: Code ↔ shared docs ↔ tool harness alignment.
- **Replacement feasibility**: Partial. Drift-detection becomes a `completion gate` activity in the Default Flow instead of a free-standing skill the user invokes.
- **Bucket: Overlay** for the same reason as planning-checklists.
- **Final location**: unchanged.
- **Migration risk**: Low.
- **Stability impact**: Medium.
- **Notes**: Phase 1 must add a checklist row for "Tier 0/1/2 entries in `harness-asset-matrix.md` match filesystem".

### `onboarding-role-tracks.md`

- **Current role**: 100-line role-specific onboarding (New / Intermediate / Advanced).
- **Why it exists**: Surface for `/onboard`.
- **Replacement feasibility**: Partial. Onboarding is the most clearly commodity scaffolding among reference docs; only the project-specific intro must remain locally.
- **Bucket: Overlay** — the role tracks themselves are kept; the Default Flow does not invoke onboarding except at session-start.
- **Final location**: unchanged.
- **Migration risk**: Low.
- **Stability impact**: Low.
- **Notes**: Could be re-evaluated for `Drop` if a future ADR consolidates onboarding into a single page.

### `harness-asset-matrix.md`

- **Current role**: This document. Living inventory of every harness asset and its bucket.
- **Why it exists**: Issue #117 Required Output #1.
- **Replacement feasibility**: None.
- **Final location**: unchanged.
- **Migration risk**: Low (additive only — entries are added when assets are added).
- **Stability impact**: High (asset triage authority for every Phase).
- **Notes**: Self-classified. `/sync-guidelines` validates that the matrix matches the actual filesystem (see drift-checklist.md row).

### `target-operating-model.md`

- **Current role**: Long-form Target Operating Model — 7-step Default Flow, mandatory subset, exception model, Claude/Codex alignment, sample-workflow traces.
- **Why it exists**: Issue #117 Required Output #2.
- **Replacement feasibility**: None.
- **Final location**: unchanged.
- **Migration risk**: Low.
- **Stability impact**: High (every Phase 2~5 adapter spec resolves to this document).
- **Notes**: Self-classified.

### `migration-strategy.md`

- **Current role**: Phased migration plan — Phase 0~5 spec, rollback, dual-system window, asset movement order.
- **Why it exists**: Issue #117 Required Output #3.
- **Replacement feasibility**: None.
- **Final location**: unchanged.
- **Migration risk**: Low.
- **Stability impact**: High (Phase 2~5 acceptance criteria copy from §1).
- **Notes**: Self-classified.

### `governor-review-log/` (directory)

- **Current role**: Permanent archive of cross-tool review trails for every governor-changing PR (ADR 045 Pillar 4). Each PR adds `pr-{NNN}-{slug}.md` with Summary / Review Rounds / Inherited Constraints / Self-Application Proof.
- **Why it exists**: Round-4 self-coherence review found that PR #125's review trail was only in PR body — not auto-transmitted to Phase 2~5 work. The directory makes review trails first-class repo artefacts.
- **Replacement feasibility**: None.
- **Final location**: unchanged.
- **Migration risk**: Low (additive only — entries grow over time).
- **Stability impact**: High (drift-checklist §1D verifies sync; Phase 4 hook reminds on missing entry).
- **Notes**: Self-classified. Long-term retention; archive subdirectories (e.g. `2026/`) may be introduced by a future ADR if size becomes a problem.

### `governor-paths.md`

- **Current role**: Canonical source for the governor-changing path list (Tier A / B / C plus exclusions). All consumer docs (AGENTS.md, target-operating-model.md, migration-strategy.md, drift-checklist.md, `.github/pull_request_template.md`) link this file rather than redeclare the list.
- **Why it exists**: Round-4 cross-tool review (R4.3) caught microscopic drift between the five copies of the path list. A single source removes the drift surface and prepares Phase 5's shared module to read the file directly.
- **Replacement feasibility**: None.
- **Final location**: unchanged.
- **Migration risk**: Low.
- **Stability impact**: High — every path-classification decision in Phase 2~5 hooks resolves to this file.
- **Notes**: Itself governor-changing. Editing it requires a fresh `governor-review-log/` entry per the file's own §Updating section.

---

## Tier 2 — Skills (3-Layer Hybrid C)

Fourteen skills, each existing in three layers (`docs/ai/shared/skills/{name}.md` shared procedure + `.claude/skills/{name}/SKILL.md` wrapper + `.agents/skills/{name}/SKILL.md` wrapper). The bucket is assigned per skill (all three layers share the bucket); the matrix records the skill once.

Bucket guideline:
- Skills that scaffold or audit *project-specific architecture* (3-tier hybrid, optional infra DI, ADR 040/042/043 patterns) → **Keep**.
- Skills whose procedure is *generic process discipline* (planning, review, onboarding) → **Overlay**: the Default Flow routes work through them; their bodies remain.

| Skill | Bucket | Risk | Impact |
|---|---|---|---|
| `new-domain` | Keep | Low | High |
| `add-api` | Keep | Low | High |
| `add-worker-task` | Keep | Low | Medium |
| `add-admin-page` | Keep | Low | Medium |
| `add-cross-domain` | Keep | Low | Medium |
| `migrate-domain` | Keep | Low | Medium |
| `test-domain` | Keep | Low | High |
| `review-architecture` | Keep | Low | High |
| `security-review` | Keep | Low | High |
| `sync-guidelines` | Keep | Low | High |
| `plan-feature` | Overlay | Low | High |
| `review-pr` | Overlay | Low | High |
| `fix-bug` | Overlay | Low | Medium |
| `onboard` | Overlay | Low | Low |

### `new-domain` (Keep)

- **Current role**: Full domain scaffolding (15 content + 25 `__init__.py` + 4 tests = 44 files).
- **Why it exists**: Project's 3-tier hybrid architecture is too large to scaffold by hand.
- **Replacement feasibility**: None.
- **Final location**: unchanged.
- **Phase 1 edit**: All 3 layers gain a "Default Flow Position" section locating the skill at `implement` step (post-`framing`/`approach`/`plan`); shared procedure adds Pre/Post-implementation routing notes.
- **Notes**: Carries the Optional AI Infra Variant pattern (ADR 042); examples-profile carve-out applies.

### `add-api` (Keep)

- **Current role**: Add an endpoint to an existing domain following bottom-up layering.
- **Why it exists**: Enforces DTO rules, base-service generics, router conventions per ADR 011/043.
- **Replacement feasibility**: None.
- **Final location**: unchanged.
- **Phase 1 edit**: Default Flow Position = `implement`. Shared procedure adds an explicit "verify with `/test-domain`" pointer.
- **Notes**: Most-used skill after `/plan-feature`.

### `add-worker-task` (Keep)

- **Current role**: Taskiq worker task scaffolding with explicit payload contract and thin task adapter.
- **Why it exists**: Broker abstraction (#8) requires a uniform pattern; payload-vs-business separation enforced.
- **Replacement feasibility**: None.
- **Final location**: unchanged.
- **Phase 1 edit**: Default Flow Position = `implement`.
- **Notes**: Codex-side `BROKER_TYPE` env-var rules apply; not affected by hook phases.

### `add-admin-page` (Keep)

- **Current role**: NiceGUI admin page scaffold with config / page split + sensitive-field masking.
- **Why it exists**: ADR 014 admin dashboard pattern; admin extra split (#104).
- **Replacement feasibility**: None.
- **Final location**: unchanged.
- **Phase 1 edit**: Default Flow Position = `implement`.
- **Notes**: Requires `admin` extra installed; skill body documents fallback message when extra is absent.

### `add-cross-domain` (Keep)

- **Current role**: Wire one domain's data to another via Protocol-based DIP.
- **Why it exists**: Prevents direct cross-domain implementation imports (Absolute Prohibition).
- **Replacement feasibility**: None.
- **Final location**: unchanged.
- **Phase 1 edit**: Default Flow Position = `implement` (after `approach options` for whether to introduce the dependency at all).
- **Notes**: Most likely to require `approach options` step because cross-domain dependencies are architecture commitments.

### `migrate-domain` (Keep)

- **Current role**: Alembic revision generation, application, downgrade, status.
- **Why it exists**: Migration safety guards (autogenerated revisions are review-required).
- **Replacement feasibility**: None.
- **Final location**: unchanged.
- **Phase 1 edit**: Default Flow Position = `implement` and feeds into the `verify` step (must run `alembic upgrade head` against a clean DB).
- **Notes**: `disable-model-invocation: true` in skill frontmatter; manual user invocation only.

### `test-domain` (Keep)

- **Current role**: Generate or run tests for a domain. Surface for the `verify` step.
- **Why it exists**: Project-specific test patterns (factories, integration baseline, e2e).
- **Replacement feasibility**: None.
- **Final location**: unchanged.
- **Phase 1 edit**: Default Flow Position = `verify`. Shared procedure becomes the canonical `verify`-step skill.
- **Notes**: Phase 3 verification-first hook will auto-suggest invocation when changed_files include source code.

### `review-architecture` (Keep)

- **Current role**: Audit a domain or the full repo for architecture compliance against the shared checklist.
- **Why it exists**: Catches Absolute Prohibition violations and ADR drift.
- **Replacement feasibility**: None.
- **Final location**: unchanged.
- **Phase 1 edit**: Default Flow Position = `self-review` (architecture commitments) and may be triggered before `completion gate`.
- **Notes**: Examples profile carve-out applies (relaxed §5 / §2).

### `security-review` (Keep)

- **Current role**: OWASP-aligned audit for a domain or file.
- **Why it exists**: Project-specific security stance.
- **Replacement feasibility**: None.
- **Final location**: unchanged.
- **Phase 1 edit**: Default Flow Position = `self-review` (security-sensitive surfaces).
- **Notes**: Trigger list lives in the shared procedure; not all changes invoke this.

### `sync-guidelines` (Keep)

- **Current role**: Drift management — code ↔ shared docs ↔ skill wrappers.
- **Why it exists**: Single closure step that reconciles all rule sources.
- **Replacement feasibility**: None.
- **Final location**: unchanged.
- **Phase 1 edit**: Default Flow Position = `completion gate` follow-up. Adds drift detection for `harness-asset-matrix.md` ↔ filesystem.
- **Notes**: `disable-model-invocation: true`; user-explicit only. Critical for Phase 1 acceptance — must catch any 3-layer skill drift introduced this PR.

### `plan-feature` (Overlay)

- **Current role**: Feature planning with five phases (Requirements, Approach, Architecture, Security, Tasks). Phase 1 (Approach Options) was added in #115/#116 — the first philosophy port.
- **Why it exists**: Prevent omission-driven feature planning.
- **Replacement feasibility**: Partial. The skill itself remains; the Default Flow now invokes its phases as discrete steps (`framing`, `approach options`, `plan`).
- **Bucket: Overlay**. Skill body unchanged in essence; the entry-point shifts from "user invokes /plan-feature" to "Default Flow routes through it".
- **Final location**: unchanged.
- **Phase 1 edit**: Default Flow Position section + recursion guard ("do not invoke /plan-feature recursively from within /plan-feature").
- **Notes**: First skill where the philosophy port is most visible.

### `review-pr` (Overlay)

- **Current role**: PR architecture quality-gate review with drift-candidate detection.
- **Why it exists**: Standardise PR-time architecture audits.
- **Replacement feasibility**: Partial. Activity becomes part of the `completion gate` step.
- **Bucket: Overlay**.
- **Final location**: unchanged.
- **Phase 1 edit**: Default Flow Position = `completion gate`. Recursion guard.
- **Notes**: Phase 4 Stop hook will auto-suggest invocation once a commit-time gate is wired.

### `fix-bug` (Overlay)

- **Current role**: Reproduce → Trace → Fix → Verify 4-phase bug workflow.
- **Why it exists**: Prevent symptom-only fixes.
- **Replacement feasibility**: Partial. The four phases map naturally onto Default Flow's `framing`+`plan`+`implement`+`verify`.
- **Bucket: Overlay**. The skill body remains valuable for the Trace/Verify detail; entry-point shifts.
- **Final location**: unchanged.
- **Phase 1 edit**: Default Flow Position section explaining the 1:1 phase mapping.
- **Notes**: `[hotfix]` exception token is the natural escape for genuinely urgent bug-fix work.

### `onboard` (Overlay)

- **Current role**: Interactive onboarding (Welcome / Domains / Workflow / Assets / Next Steps).
- **Why it exists**: New-contributor structured introduction.
- **Replacement feasibility**: Full for the procedure; project intro must stay local.
- **Bucket: Overlay** — kept on disk, but Default Flow does not invoke it during normal coding.
- **Final location**: unchanged.
- **Phase 1 edit**: Add Default Flow Position section that clarifies "session-start only; not a coding-flow skill".
- **Notes**: Largest skill body (317 lines shared procedure); could be a future Drop candidate after a few revisions of usage data.

---

## Tier 3 — Hooks

Sixteen hook scripts (6 Claude shell + 3 Claude Python implementations + 7 Codex Python). Phase 2 (#121) added `.claude/hooks/user-prompt-submit.sh` + `.claude/hooks/user_prompt_submit.py` as the first Claude UserPromptSubmit hook surface; Phase 3 (#122) added `.claude/hooks/verify-first.{sh,py}` as a **sibling** hook in the existing `PostToolUse Edit|Write` matcher block, plus `.codex/hooks/verify_first.py` as a library module imported by the Stop hook (segment merge, IC-2). The Codex side `.codex/hooks/post-tool-format.py` was extended (behaviour-preserving) to record verify-class commands to `.codex/state/verify-log-{session}.json`. Phase 3 introduces the second *process-governor* hook surface (verify-first reminder).

| Asset | Bucket | Risk | Impact |
|---|---|---|---|
| `.claude/hooks/check-required-plugins.sh` | Keep | Low | Low |
| `.claude/hooks/pre-tool-security.sh` | Keep | Low | Medium |
| `.claude/hooks/post-tool-format.sh` | Keep | Low | Medium |
| `.claude/hooks/stop-sync-reminder.sh` | Keep | Low | Medium |
| `.claude/hooks/user-prompt-submit.sh` | Keep | Low | Medium |
| `.claude/hooks/verify-first.sh` | Overlay | Low | Low |
| `.claude/hooks/pre_tool_security.py` | Keep | Low | Medium |
| `.claude/hooks/user_prompt_submit.py` | Keep | Low | Medium |
| `.claude/hooks/verify_first.py` | Overlay | Low | Low |
| `.codex/hooks/_shared.py` | Keep | Low | Low |
| `.codex/hooks/session-start.py` | Keep | Low | Low |
| `.codex/hooks/user-prompt-submit.py` | Keep | Low | Medium |
| `.codex/hooks/pre-tool-security.py` | Keep | Low | Medium |
| `.codex/hooks/post-tool-format.py` | Keep | Low | Medium |
| `.codex/hooks/stop-sync-reminder.py` | Keep | Low | Medium |
| `.codex/hooks/verify_first.py` | Overlay | Low | Low |

### `.claude/hooks/check-required-plugins.sh`

- **Current role**: SessionStart guard that ensures `pyright-lsp` is enabled.
- **Why it exists**: #63 plugin migration; missing plugins silently break LSP-aware skills.
- **Bucket**: Keep.
- **Notes**: No Default Flow interaction.

### `.claude/hooks/pre-tool-security.sh`

- **Current role**: PreToolUse on Edit / Write / Bash; static checks against destructive commands and architecture violations.
- **Why it exists**: Safety gate in the precedence layer (D1.3).
- **Bucket**: Keep.
- **Notes**: Default Flow ranks **below** this hook; escape tokens cannot bypass it.

### `.claude/hooks/post-tool-format.sh`

- **Current role**: PostToolUse on Edit / Write; runs `ruff format` + `ruff check --fix` on `.py` files.
- **Why it exists**: Format consistency without manual invocation.
- **Bucket**: Keep.
- **Notes**: Phase 3 (#122) verification-first hook (`.claude/hooks/verify-first.sh`) lives in the *same* `PostToolUse Edit|Write` matcher block as a sibling, not a separate matcher. SoC: this hook mutates files (ruff), the verify-first hook is informational stderr only.

### `.claude/hooks/stop-sync-reminder.sh`

- **Current role**: Stop hook reminding the user to run `/sync-guidelines` if shared rule sources changed.
- **Why it exists**: Drift management closure.
- **Bucket**: Keep.
- **Notes**: Phase 4 completion-gate hook will *combine* its output with this reminder rather than overwrite it (Codex R2).

### `.claude/hooks/pre_tool_security.py`

- **Current role**: Python implementation of pre-tool security checks. The `.sh` wrapper at `.claude/hooks/pre-tool-security.sh` reads stdin and pipes to this `.py` module via `python3`.
- **Why it exists**: Cleaner separation between hook contract (the `.sh` matched against `.claude/settings.json` matchers) and security-check logic (the `.py` module). Mirrors `.codex/hooks/_shared.py` + `.codex/hooks/pre-tool-security.py` separation on the Codex side.
- **Bucket**: Keep.
- **Migration risk**: Low.
- **Notes**: Earlier draft of this matrix (initial Phase 1 pass) misclassified this as Drop. Self-verification during cross-link work caught the misclassification: `.claude/hooks/pre-tool-security.sh` line 6 explicitly invokes `python3 "$(dirname "$0")/pre_tool_security.py"`. The two files are an active pair, not duplication.

### `.codex/hooks/_shared.py`

- **Current role**: Shared utility for Codex hook scripts (logging / config / colorised output).
- **Bucket**: Keep.
- **Notes**: Phase 5 shared governor module may absorb part of this; the file itself remains during Phases 1~4.

### `.codex/hooks/session-start.py`

- **Current role**: SessionStart message announcing Codex repo harness.
- **Bucket**: Keep.
- **Notes**: Phase 2 extension may inject a Default Flow reminder banner here.

### `.codex/hooks/user-prompt-submit.py`

- **Current role**: Prompt safety check (rule-bypass / destructive git / destructive shell) **plus** Phase 2 (#121) exception-token parser. Order: safety check first; on `decision: block`, return without parsing or writing a marker (HC-1 from PR #121). Only after safety has passed does the parser run; its output is informational and never blocks submission.
- **Bucket**: Keep — Phase 2 (#121) extension is behaviour-preserving.
- **Notes**: Codex R3 — exception-token recognition never overrides safety / sandbox / Absolute Prohibitions (IC-1). Safety still wins (D1.3). Marker file location: `.codex/state/exception-token-{ts}-{seq}.json` (gitignored).

### `.claude/hooks/user-prompt-submit.sh`

- **Current role**: Phase 2 (#121) UserPromptSubmit wrapper. Mirrors `pre-tool-security.sh` shape — pipes stdin to the Python helper. Informational only, exits 0.
- **Why it exists**: Claude did not have a UserPromptSubmit hook before Phase 2; this PR adds the surface so the exception-token vocabulary defined in PR #125 becomes machine-readable on the Claude side.
- **Bucket**: Keep.
- **Notes**: Mirrored against Codex `.codex/hooks/user-prompt-submit.py` for Phase 5 consolidation under `.agents/shared/governor/`.

### `.claude/hooks/user_prompt_submit.py`

- **Current role**: Phase 2 (#121) parser helper. NFKC normalisation + canonical regex `^\s*\[(trivial|hotfix|exploration|자명|긴급|탐색)\](?:\s|$)` (case-insensitive). Emits `{matched, token, rationale_required}` JSON to stderr; on match, writes a marker file under `.claude/state/`.
- **Why it exists**: Sh wrapper + py helper split (matches the `pre-tool-security.sh` + `pre_tool_security.py` pattern). Avoids shell-escaping NFKC + regex inline.
- **Bucket**: Keep.
- **Notes**: Output is identical to `.codex/hooks/user-prompt-submit.py` parser. Parity asserted by `tests/unit/agents_shared/test_token_parser.py` (silent-divergence safety net for D1=B).

### `.claude/hooks/verify-first.sh`

- **Current role**: Phase 3 (#122) PostToolUse `Edit|Write` sibling wrapper. Pipes stdin to `verify_first.py`; always exits 0 (HC-3.3 informational only).
- **Why it exists**: New SoC surface — formatting (`post-tool-format.sh`) is mutating; verify-first is advisory. Mixing them in one script complicates failure modes.
- **Bucket**: Overlay.
- **Notes**: Mirrors the `pre-tool-security.sh` + `pre_tool_security.py` shape. Phase 5 (#124) consolidates with `.codex/hooks/verify_first.py` into `.agents/shared/governor/`.

### `.claude/hooks/verify_first.py`

- **Current role**: Phase 3 (#122) verify-first decision helper. Reads PostToolUse Edit|Write payload from stdin; if the changed `file_path` ends with `.py` AND the latest Phase 2 marker is not `[exploration]/[탐색]`, prints a frozen `REMINDER_TEXT` to stderr.
- **Why it exists**: Reminds the user that the Default Coding Flow `verify` step is missing for the changed Python file. Read-only on Phase 2 markers (IC-11 from PR #126; Phase 4 #123 owns lifecycle).
- **Bucket**: Overlay.
- **Notes**: `REMINDER_TEXT` constant is string-equal to `.codex/hooks/verify_first.py`. Parity asserted by `tests/unit/agents_shared/test_verify_first.py::test_reminder_text_string_equality`. Fail-open on every error path (HC-3.6).

### `.codex/hooks/pre-tool-security.py`

- **Current role**: PreToolUse Bash matcher; checks destructive commands, SQL injection patterns, secret leakage.
- **Bucket**: Keep.
- **Notes**: Codex R7 — Default Flow does not weaken any prefix_rule decision (`forbidden`/`prompt`).

### `.codex/hooks/post-tool-format.py`

- **Current role**: PostToolUse Bash matcher. Two responsibilities: (1) runs ruff after a Bash invocation that touched Python files; (2) Phase 3 (#122) — records verify-class commands (`pytest`, `make test`, `make demo[-rag]`, `alembic upgrade`) to `.codex/state/verify-log-{session}.json` so the Stop hook can detect whether verify happened in this session.
- **Bucket**: Keep — but Codex R7 is critical: this hook **does not see** edits that bypass Bash (e.g. `apply_patch`). Phase 3 verification-first reminder relies on Stop-side change detection for Codex (`.codex/hooks/stop-sync-reminder.py` extension), not on extending this hook to emit reminders.
- **Notes**: Largest Codex-side blind spot identified during Phase 0.5 review. Phase 3 R0.4 wraps the file in a top-level fail-open so invalid stdin / ruff-missing / verify-log writer failures all return exit 0.

### `.codex/hooks/stop-sync-reminder.py`

- **Current role**: Stop hook with two segments merged into a single `{"systemMessage": "..."}` JSON output (IC-2): (1) sync-reminder for foundation/structure path drift; (2) Phase 3 (#122) verify-first segment via `verify_first.should_remind()` import (current-session log read only — R0.2; subsecond freshness — R0.3).
- **Bucket**: Keep.
- **Notes**: Phase 4 completion-gate output is merged as a third segment in the same hook output; Codex R2. Phase 3 R0.1: the verify-first import is performed inside the same `try` block that calls `should_remind` so an ImportError leaves the existing sync-reminder behaviour intact (HC-3.6 fail-open).

### `.codex/hooks/verify_first.py`

- **Current role**: Phase 3 (#122) verify-first decision helper. Library module — NOT registered as its own hook (IC-2 single Stop event output). Imported by `stop-sync-reminder.py` (decision) and `post-tool-format.py` (verify-log writer).
- **Why it exists**: Codex side cannot trigger reminders on `PostToolUse Bash` because `apply_patch` is invisible there (IC-5). Detection happens at Stop time using `_shared.changed_files()` + per-session verify-log freshness check.
- **Bucket**: Overlay.
- **Notes**: `REMINDER_TEXT` is string-equal to `.claude/hooks/verify_first.py`. `session_id()` = `CODEX_SESSION_ID` env var or `f"{ppid}-{pid}-{start_ns:016x}"` fallback (R0.2 — defeats PPID collision). Verify-log entries store `ts_epoch_ns` for subsecond freshness comparison against `Path.stat().st_mtime_ns` (R0.3). `read_latest_token_marker` duplicated from Claude side — consolidated by Phase 5 (#124).

---

## Tier 4 — Rule Files

Six rule files (5 Claude + 1 Codex). All `Keep` except `commands.md` which becomes `Overlay` because Default Flow rerouting changes its primary use.

| Asset | Bucket | Risk | Impact |
|---|---|---|---|
| `.claude/rules/absolute-prohibitions.md` | Keep | Low | High |
| `.claude/rules/project-overview.md` | Keep | Low | Medium |
| `.claude/rules/project-status.md` | Keep | Low | Medium |
| `.claude/rules/architecture-conventions.md` | Keep | Low | High |
| `.claude/rules/commands.md` | Overlay | Low | Low |
| `.codex/rules/fastapi-agent-blueprint.rules` | Keep | Low | Medium |

### `.claude/rules/absolute-prohibitions.md`

- **Current role**: Auto-loaded projection of `AGENTS.md § Absolute Prohibitions` for Claude.
- **Bucket**: Keep.
- **Notes**: Default Flow precedence (D1.4) makes Absolute Prohibitions canonical above Default Flow. No edit needed.

### `.claude/rules/project-overview.md`

- **Current role**: Project purpose, app entry-points, dependency direction, infra options, Settings validation, key VOs.
- **Bucket**: Keep.
- **Notes**: Periodic `/sync-guidelines` snapshot.

### `.claude/rules/project-status.md`

- **Current role**: Latest release notes, active domains, recent ADRs, status of "not yet implemented" features.
- **Bucket**: Keep.
- **Notes**: Phase 1 update will record ADR 045 and Default Flow adoption in the Recent Major Changes table.

### `.claude/rules/architecture-conventions.md`

- **Current role**: Structural data-flow + base-class generics + selectors + storage / embedding / LLM choices + structured logging + object roles.
- **Bucket**: Keep.
- **Notes**: Phase 1 edit adds a small "Default Flow" cross-link in the Quality Gate Flow vicinity (no structural change).

### `.claude/rules/commands.md` (Overlay)

- **Current role**: Quick-reference shell commands.
- **Why it exists**: Reduce trial-and-error cost during routine tasks.
- **Replacement feasibility**: Partial. Default Flow steps will reference these commands; the file becomes a *consulted* reference rather than an entry point.
- **Bucket**: Overlay.
- **Phase 1 edit**: Add "Default Flow" pointer near the top.
- **Notes**: Most assets in this bucket are reference rather than process; this is the only Tier 4 example.

### `.codex/rules/fastapi-agent-blueprint.rules`

- **Current role**: Codex prefix rules: forbidden (`git reset --hard`, `git checkout --`, `rm -rf`) + prompt-required (`git push`, `alembic downgrade`).
- **Bucket**: Keep.
- **Phase 1 edit (Codex R6)**: `git push` justification updated to mention "Default Coding Flow verification and self-review steps".
- **Notes**: Default Flow ranks below this file (D1.2). Escape tokens never lift a prefix rule.

---

## Bucket Distribution Summary

| Bucket | Count | Share | Notes |
|---|---|---|---|
| Keep | 50 | ~82% | Project-specific architecture / safety / reference value (incl. 4 design + 3 self-coherence-recovery process-governor artefacts + 2 Phase 2 #121 hooks) |
| Overlay | 11 | ~18% | Process discipline now routed by Default Flow (Phase 3 #122 adds 3 verify-first hooks) |
| Replace | 0 | 0% | None in initial inventory; reserved for future passes |
| Drop | 0 | 0% | Initial pass found no genuinely removable assets |
| **Total** | **61** | 100% | |

Counting note: `Tier 0=9` (8 + ADR 045 + `.github/pull_request_template.md`), `Tier 1=17` (12 reference + 3 design living docs + `governor-review-log/` directory + `governor-paths.md`), `Tier 2=14` (skill rows; each row covers all 3 wrapper layers), `Tier 3=16` (Phase 3 #122 added `.claude/hooks/verify-first.{sh,py}` + `.codex/hooks/verify_first.py`; previously 13 after Phase 2), `Tier 4=6` — sum 62. The 61 figure above excludes `.claude/settings.local.json` from the active-share count because it is `.gitignore`d (its row is recorded for completeness only). The bucket-share percentages use 61 as the denominator.

This distribution matches the "Mostly Local with Philosophy Overlay" model declared in [ADR 045 §D4](../../history/045-hybrid-harness-target-architecture.md). The `Replace` and `Drop` columns are both empty in the initial pass: no asset's content is being rewritten, and self-verification during cross-link work showed that the only `Drop` candidate identified during the first triage was actually an active component (a sh-wrapper `.py` pair).

If a future `Replace` candidate emerges, the threshold is: Keep+Overlay would otherwise force the asset into structural inconsistency with the Default Flow. None of the current 58 assets meet that.

## Verification

The following self-checks must pass before this matrix is treated as authoritative.

- [ ] Every asset on the filesystem appears in this matrix exactly once. Verify via:
  ```bash
  # Tier 0
  ls AGENTS.md CLAUDE.md .codex/config.toml .codex/hooks.json \
     .claude/settings.json .claude/settings.local.json .mcp.json
  # Tier 1
  ls docs/ai/shared/*.md
  # Tier 2 (3 layers per skill)
  ls docs/ai/shared/skills/*.md .claude/skills/*/SKILL.md .agents/skills/*/SKILL.md
  # Tier 3 (exclude gitignored caches such as __pycache__/*.pyc)
  find .claude/hooks .codex/hooks -type f \
    ! -path '*/__pycache__/*' ! -name '*.pyc'
  # Tier 4
  ls .claude/rules/*.md .codex/rules/*
  ```
- [ ] Every skill has a consistent bucket across its three wrapper layers (Phase 1 update preserves this invariant).
- [ ] No asset is classified `Replace` while other Phase 1 work treats it as `Keep`.
- [ ] Any `Drop` candidate has been verified to have zero callers (`rg <name> .claude/ .codex/`). Self-verification during cross-link work overturned the only initial Drop candidate; the principle remains: a Drop classification requires positive evidence of zero callers.
- [ ] Bucket-share ratio matches §Bucket Distribution Summary (~86% Keep / ~14% Overlay / 0% Replace / 0% Drop) within ±10%.

## Update Log

- 2026-04-26 — Initial inventory under ADR 045 / Phase 1.
- 2026-04-26 — Phase 2 (#121): added `.claude/hooks/user-prompt-submit.sh` + `.claude/hooks/user_prompt_submit.py` to Tier 3; updated `.codex/hooks/user-prompt-submit.py` role to include exception-token parsing (behaviour-preserving). Total 56 → 58.
- 2026-04-27 — Phase 3 (#122): added `.claude/hooks/verify-first.{sh,py}` (sibling in existing `PostToolUse Edit|Write` matcher) + `.codex/hooks/verify_first.py` library to Tier 3; extended `.codex/hooks/post-tool-format.py` with verify-class command logger and top-level fail-open (R0.4); extended `.codex/hooks/stop-sync-reminder.py` to merge a verify-first segment (import inside try-block per R0.1). Total 58 → 61. Bucket-share shifted Keep 86% → 82% / Overlay 14% → 18% as the 3 new hooks all classify as Overlay (process-governor verify-first reminder).
