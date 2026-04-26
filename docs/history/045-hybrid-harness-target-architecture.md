# 045. Hybrid Harness Target Architecture — Process Governor + Asset Triage

- Status: Accepted
- Date: 2026-04-26
- Related issue: #117
- Related PRs: #115 / #116 (first philosophy port — `/plan-feature` Approach Options Phase)
- Precursor memo: [archive/044](archive/044-superpowers-gstack-process-governor-evaluation.md) (superpowers / gstack / process-governor evaluation)
- Constraints: ADR [040](040-rag-as-reusable-pattern.md), [042](042-optional-infrastructure-di-pattern.md), [043](043-responsibility-driven-refactor.md) — architecture / DI / responsibility 계층은 **불변**

## Summary

This ADR records the top-level decisions that resolve issue #117 (`Design a hybrid superpowers adoption model with harness asset triage`). It commits the project to a **local process governor inspired by superpowers' philosophy**, not to adopting an external superpowers package. The three design outputs required by #117 (Asset Inventory Matrix, Target Operating Model, Migration Strategy) are split into separate living docs under `docs/ai/shared/` and indexed from this ADR.

Four decisions:

1. **D1 — 7-step Default Coding Flow** added to `AGENTS.md` as a new shared-constitution section, with explicit precedence rules below sandbox / approval / `.codex/rules` / safety hooks / Absolute Prohibitions.
2. **D2 — Hybrid graduated enforcement**: guidance + skill-body mandatory phases now (Phase 1) + minimal hooks later (Phase 2~5). Critical gates remain hard; trivial work escapes via explicit tokens.
3. **D3 — Machine-readable exception token vocabulary** (English + Korean) recognised only as a leading token on prompt line 1, never overriding safety.
4. **D4 — Output split** across one ADR (decisions) and three living docs (matrix / operating-model / migration-strategy).

## Background

[archive/044](archive/044-superpowers-gstack-process-governor-evaluation.md) diagnosed the real problem as **weak routing**, not missing skills: the repo already ships a shared constitution (`AGENTS.md`), a 3-layer Hybrid C skill split (14 skills × 3 layers), 11 hooks (Claude + Codex), and a shared reference layer (`docs/ai/shared/`). What is missing is a default execution flow that *routes* most coding tasks through framing → planning → verification → self-review by default.

[#115 / #116](https://github.com/anthropics/claude-code/issues/28310) ported the first piece of that flow (Approach Options as Phase 1 of `/plan-feature`), but did not generalise it to other implementation skills, and added no enforcement beyond skill-body text.

Issue #117 asked for three explicit deliverables — an Asset Inventory Matrix, a Target Operating Model, and a Migration Strategy — together with answers to eight key design questions. This ADR records the meta-decisions; the deliverables themselves are in `docs/ai/shared/`.

A read-only Codex review (gpt-5.5, sandbox=read-only, run via `profiles.research`) on 2026-04-26 contributed seven cross-tool consistency corrections that are now baked into the design.

## Decision

### D1 — Default Coding Flow with explicit precedence

Seven steps, added as a new top-level section of `AGENTS.md`:

```
problem framing → approach options → plan → implement
                → verify → self-review → completion gate
```

Mandatory-by-default for implementation-class work: `framing`, `plan`, `verify`, `self-review`.
Conditionally mandatory (architecture commitment present): `approach options`.

**Precedence (Codex R1).** Default Coding Flow ranks **below** the following four layers, in order:

1. Active sandbox / approval policy / explicit user scope (e.g. read-only, review-only)
2. `.codex/rules/*` prefix rules (`forbidden` / `prompt`)
3. Safety hooks (security checks, destructive-command guards)
4. `AGENTS.md` § Absolute Prohibitions

Escape tokens (D3) reduce process burden only. They never override any of the four layers above.

### D2 — Hybrid graduated enforcement

Three layers of strength, introduced incrementally:

- **(a) Guidance** — `AGENTS.md` § Default Flow, `CLAUDE.md` cross-link, `docs/ai/shared/skills/{name}.md` mandatory-phase text. Phase 1 (this PR).
- **(b) Skill body** — 14 skills × 3 wrapper layers (`docs/ai/shared/skills/`, `.claude/skills/`, `.agents/skills/`) gain a "Default Flow Position" section + Phase/Step overview update. Phase 1 (this PR).
- **(c) Minimal hooks** — `UserPromptSubmit` (Phase 2), `PostToolUse` / `Edit|Write` for Claude + `Stop` / changed-files for Codex (Phase 3), `Stop` completion gate (Phase 4), shared parser/policy module (Phase 5). Each as a separate follow-up issue.

Critical gates remain hard in (c); the hybrid label refers to the explicit escape lane, not to weakened blocking. False-positive cost (which silently normalises hook bypass and thus disables the governor) is the reason hard-only enforcement is rejected. See `target-operating-model.md` §3.

### D3 — Exception token vocabulary

English: `[trivial]` / `[hotfix]` / `[exploration]`. Korean (matching contributor language preference): `[자명]` / `[긴급]` / `[탐색]`.

Recognition rules (Codex R3):

- Tokens are recognised **only as a leading token on the first line** of a prompt. Body occurrences are ignored, preventing accidental matches in natural Korean text.
- Prompts are NFKC-normalised before matching.
- Regex: `^\s*\[(trivial|hotfix|exploration|자명|긴급|탐색)\](?:\s|$)` (case-insensitive).
- Token use carries a follow-up obligation: the next commit message must record the rationale.

Auto-escapes (no token required): `changed_files == 0`, doc-only changes, comment-only changes.

### D4 — Output split

| Doc | Location | Target length | Role |
|---|---|---|---|
| ADR 045 (this) | `docs/history/` | 150~220 lines | Decisions + navigator + design-question resolutions |
| `harness-asset-matrix.md` | `docs/ai/shared/` | 600~800 lines | Living inventory: ~50 assets across 5 tiers, 9 columns |
| `target-operating-model.md` | `docs/ai/shared/` | 400~500 lines | §1~§7 of the operating model + workstream / sample-trace / Q&A appendices |
| `migration-strategy.md` | `docs/ai/shared/` | 200~300 lines | Phase 0~5 spec, rollback, dual-system window, ordering |

The matrix is a *living* inventory and must not be embedded in an ADR (which is immutable). The operating model carries the long-form workflow traces that a navigator-style ADR cannot host without bloating.

## Eight Design Questions (issue #117) — Resolution Map

1. **Project-specific value vs commodity scaffolding** → resolved by the matrix Tier classification (Tier 0/1 = project-specific; parts of Tier 2 = commodity process scaffolding).
2. **Stay local / overlay / replace / drop** → matrix bucket column. Initial Phase 1 pass produced ~85% Keep / ~15% Overlay / 0% Replace / 0% Drop. The first triage flagged one Drop candidate (`.claude/hooks/pre_tool_security.py`); self-verification during cross-link work overturned it because the file is the active body invoked by `pre-tool-security.sh`. Future passes may re-introduce Replace or Drop candidates; the matrix is living.
3. **Minimum viable process governor** → the 7-step Default Coding Flow + mandatory-by-default subset + explicit escape lane.
4. **Mandatory by default for coding work** → framing + plan + verify + self-review. `approach options` mandatory only when the change is an architecture commitment.
5. **Where enforcement lives** → (i) shared rules: `AGENTS.md` § Default Flow; (ii) shared workflow docs: `target-operating-model.md`; (iii) skill wrappers: 3-layer mandatory-phase + Default Flow Position; (iv) session-start guidance: deferred to Phase 2; (v) prompt-submit hooks: Phase 2; (vi) stop-time completion gates: Phase 4.
6. **Valid exception** → leading-line escape tokens (D3) + auto-escapes (no-change, doc-only, comment-only). Safety / sandbox / prefix rules are never escapable.
7. **Claude / Codex alignment** → `AGENTS.md` is canonical. Tool-specific adapters are split per phase: Codex enforcement is **prompt-time routing + changed-file completion checks**, not Bash-only `PostToolUse` (Codex R7). Phase 5 consolidates parsers and policies into a shared module so neither side duplicates harness logic.
8. **Rigor without friction** → hybrid graduated (D2). Hard at critical gates, escape lane for trivial work. Aligned with #117 Non-Goals (no heavy ceremony) and Constraints (narrow exceptions).

## Consequences

**Positive**

- Resolves the "weak routing" diagnosis from archive/044 with a concrete, phased mechanism rather than further documentation increase.
- Preserves ADR 040 / 042 / 043 architecture and DI decisions intact; this ADR sits strictly above them in the process layer.
- Phase 2~5 are independently revertable. Single-PR rollback per phase.
- The `/sync-guidelines` skill already detects 3-layer skill drift, so Phase 1's wrapper-synchronisation requirement is enforceable without new tooling.

**Negative**

- This PR touches ~50 files. The 14 × 3 wrapper edits are a repeated pattern (review burden ≈ 10 files), but the surface is still wide.
- Escape-token vocabulary widens hook complexity in Phase 2. Mitigated by leading-token-only recognition (D3).
- Adds a new top-level section to `AGENTS.md`. Future contributors must respect the precedence ordering (D1) when proposing further enforcement.

**Neutral**

- Phase 0.5 Codex cross-tool review is now a documented step that any future cross-tool design change should follow. Not a binding rule, but a referenced precedent.

## Alternatives Considered

- **Full superpowers adoption** — Rejected in archive/044. Replaces our shared constitution and project-specific architecture canon; collides with ADR 040 / 042 / 043 boundaries.
- **Soft enforcement only (guidance, no skill-body / no hooks)** — Reproduces the archive/044 diagnosis ("good rules ≠ good default behavior"). Reverting the disease is not a fix.
- **Hard enforcement only (every task hook-blocks)** — Violates #117 Non-Goals (heavy ceremony, false-positive blocking) and Constraints (narrow exceptions). False-positive cost normalises bypass and disables the governor.
- **Single ADR carrying matrix + model + strategy** — Living inventory cannot live in an immutable ADR. Length would exceed 1000 lines. Rejected for both shape and decay reasons.

## Related Documents

- [`docs/ai/shared/harness-asset-matrix.md`](../ai/shared/harness-asset-matrix.md) — issue #117 Required Output #1
- [`docs/ai/shared/target-operating-model.md`](../ai/shared/target-operating-model.md) — issue #117 Required Output #2
- [`docs/ai/shared/migration-strategy.md`](../ai/shared/migration-strategy.md) — issue #117 Required Output #3
- [`AGENTS.md` § Default Coding Flow](../../AGENTS.md) — Phase 1 constitutional addition
- [archive/044](archive/044-superpowers-gstack-process-governor-evaluation.md) — antecedent evaluation memo
