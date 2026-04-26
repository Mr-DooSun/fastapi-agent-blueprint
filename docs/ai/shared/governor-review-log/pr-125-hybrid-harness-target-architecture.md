# PR #125 — Hybrid Harness Target Architecture + Phase 1

- GitHub PR: <https://github.com/Mr-DooSun/fastapi-agent-blueprint/pull/125>
- Closes: #117
- Branch: `feat/117-hybrid-superpowers` → `main`
- Date range: 2026-04-26
- Cross-tool reviewer: `codex exec -m gpt-5.5 --sandbox read-only` (ChatGPT-authenticated)

## Summary

Implements the four design outputs and Phase 1 of the hybrid local process governor inspired by superpowers' philosophy:

- **ADR 045** — top-level decisions D1~D4 + 8 design-question resolutions.
- **harness-asset-matrix.md** — living inventory of 53 assets (~85% Keep / ~15% Overlay / 0% Replace / 0% Drop).
- **target-operating-model.md** — 7-step Default Coding Flow + escape-token vocabulary + Claude/Codex alignment + sample workflow traces.
- **migration-strategy.md** — Phase 0~5 spec with shared-policy + per-tool-adapter split.
- **AGENTS.md § Default Coding Flow** — constitutional flow with sandbox > prefix-rule > safety-hook > Absolute-Prohibition > flow precedence.
- **14 × 3 skill wrappers** — each gains a `Default Flow Position` section.
- **Cross-links** — CLAUDE.md, .claude/rules/{architecture-conventions,project-status,commands}.md, .codex/rules/fastapi-agent-blueprint.rules, drift-checklist §1C.

Final variant pushed to PR: 5 commits. The fifth (Round-4 reinforcement) adds the canonical `governor-paths.md`, README prompt template, log freshness corrections, and Pillar 8 demotion. Total changed-files count is read from `git diff --stat main..HEAD` at merge time; the PR's GitHub display includes pre-existing maintenance commits on the same branch (sync-guidelines snapshot, context7 review log, gitignore entry).

## Review Rounds

### Round 1 — Plan Review (Phase 0.5)

- **Target**: `/Users/doo/.claude/plans/117-playful-dongarra.md` plan file.
- **Prompt focus**: cross-tool consistency of the proposed plan; Codex-only blind spots; doc structure & length; mandatory phase coverage; precedence wording.
- **Final Verdict**: 7 R-points actionable; plan adoption recommended after R-points reflected.
- **R-points surfaced** (all reflected into plan and implementation):
  - **R1**. Default Flow precedence must be explicit (sandbox / approval / `.codex/rules` / safety hooks / Absolute Prohibitions, in that order).
  - **R2**. Phase 2~5 must split shared policy from per-tool hook adapters because Codex hook surface differs from Claude.
  - **R3**. Exception-token recognition must be leading-line only with NFKC normalisation; vocabulary must include Korean tokens.
  - **R4**. ADR 045 should stay 150~220 lines; matrix / operating-model / migration-strategy carry the long-form material.
  - **R5**. The 3-layer skill-wrapper invariant means every wrapper must also carry the "Default Flow Position" content, not only the shared procedure.
  - **R6**. `.codex/rules/...` `git push` justification should mention Default Flow verification and self-review.
  - **R7**. Codex enforcement must be designed around prompt-time routing + changed-file completion checks, not Bash-only `PostToolUse` matchers, because `apply_patch` and similar non-Bash edits do not surface there.

### Round 2 — Implementation 1st Pass

- **Target**: 53-file working tree after the initial implementation push.
- **Prompt focus**: did the implementation honour R1~R7? new cross-tool gaps not seen at plan time?
- **Final Verdict**: 7 cross-tool gaps identified; fixes required before readiness review.
- **Findings (all fixed)**:
  - Broken relative links in 14 shared-skill docs (`../../../AGENTS.md` should be `../../../../AGENTS.md`) and three living docs (`../history/` should be `../../history/`).
  - Matrix bucket-definition table still cited a stale `Drop` example that the body had already overturned.
  - Matrix did not classify itself or the new process-governor docs as assets.
  - ADR 045 §Decision-Question summary used a precedence ordering different from the body and AGENTS.md.
  - `target-operating-model.md` Trace 2 conflicted with the §3 token-skip definition (it skipped `self-review` under `[trivial]`, but the table forbids that).
  - `migration-strategy.md` Phase 1 acceptance demanded a drift-checklist row that did not exist.
  - Phase 3 acceptance temporally depended on a Phase 5 deliverable.

### Round 3 — Implementation 2nd Pass / Merge-Readiness

- **Target**: 54-file working tree after Round-2 fixes.
- **Prompt focus**: are Round-2 fixes semantic (not surface)? merge blockers? Phase 2 hand-off readiness?
- **Final Verdict**: `minor fixes recommended`, **no merge blockers**.
- **Findings (all fixed)**:
  - Stale "dead" / "Drop 2%" phrasing in five locations (matrix Hook-tier intro, migration-strategy §1 + §6, target-operating-model §4 + §7).
  - Bucket-share denominators were not internally consistent across the four docs; unified to 85% / 15% / 0% / 0% with a counting note.
  - `.agents/skills/{new-domain,test-domain,fix-bug}` had less information than their Claude / shared counterparts.
  - Trace 1 implement column listed `/add-cross-domain` first, masking the actual `/new-domain` → `/add-cross-domain` → `/add-api` order.
  - Tier-3 verification command in matrix did not exclude `__pycache__/*.pyc`.
  - Phase 2 acceptance lacked a parser-fixture spec.
  - `.claude/rules/commands.md` had no Default Flow pointer despite the matrix claiming a Phase 1 edit.

### Round 4 — Self-Coherence Review

- **Target**: 8-Pillar self-application recovery commit (4th commit on the branch) plus the original 3-round trail.
- **Prompt focus**: did PR #125 itself follow the governor it defines? Pillar 1~8 self-coherence; trigger-glob alignment across documents; new cascade risk; hand-off readiness for Phase 2~5.
- **Final Verdict**: `still needs reinforcement` — fixes applied in 5th commit (Round-4 reinforcement), not a merge blocker.
- **R-points surfaced** (all addressed in 5th commit):
  - **R4.1** Self-Application Proof freshness: changed-file count and explicit Round 1/2 Final Verdicts. → Round verdicts and freshness note added.
  - **R4.2** Pillar 8 (memory feedback) is repo-invisible because the file lives only in claude-code memory. Risk: new contributor / CI cannot consume it. → Pillar 8 demoted to "optional supplemental" in ADR 045 (the substantive enforcement now lives in Pillars 4 + 5, both repo-visible).
  - **R4.3** Trigger-glob list duplicated across five documents with microscopic differences. → New canonical `docs/ai/shared/governor-paths.md` (Tier A / B / C + exclusions); all consumers updated to link the file instead of redeclaring.
  - **R4.4** Phase 4 gate did not match log entry to current PR number → stale entries could satisfy the gate. → Phase 4 acceptance and drift-checklist §1D updated to require `pr-{currentN}-` filename match.
  - **R4.5** `governor-review-log/**` is itself under `docs/ai/shared/**` (Tier A) → log-only edits would recursively require their own self-log. → `governor-paths.md` Exclusions section adds the log-only backfill exception.
  - **R4.6** Cross-tool review prompt template existed only as "Entry shape" outline → new `governor-review-log/README.md` Cross-Tool Review Prompt Template section adds an explicit template adaptable per phase.
  - **R4.7** PR template Governor-Changing section length flagged as noise risk for general contributors. Minor; deferred (delete-section instruction is sufficient for now). Re-evaluate after first non-governor PR using the template.

### Round 5 — Final Self-Coherence and Merge Readiness

- **Target**: Round-4 reinforcement commit (5th commit on the branch) plus prior commits.
- **Prompt focus**: did the Round-4 fixes actually close the gap? canonical-paths drift residue? self-application proof freshness; merge readiness on the *"superpowers-grade robust harness"* user-stated bar.
- **Final Verdict**: `minor fixes recommended` — four small drift residues identified; addressed in the 6th commit (Round-5 fix). No structural blocker.
- **R-points surfaced** (all addressed in 6th commit):
  - **R5.1** PR template `.github/pull_request_template.md` retained an inline path list at the "Triggered files" hint that contradicted the Round-4 canonicalisation. → reduced to a single instruction pointing to `governor-paths.md`.
  - **R5.2** `governor-review-log/README.md` Scope section repeated the path list verbatim. → replaced with a link to `governor-paths.md`; "non-governor-changing PRs" guidance kept.
  - **R5.3** `target-operating-model.md` had residual "glob list above" wording that referenced an inline list which had since been removed. → wording rewritten to point at `governor-paths.md`.
  - **R5.4** Self-Application Proof opened with a stale "54 files" count even though Summary correctly said the count is read from `git diff --stat` at merge time. → Self-Application Proof scope line updated to the same convention.

**Self-Coherence Note**: Round 5 reviewed the very PR that introduced the cross-tool review process, so finding additional small drift is expected and itself proves the governor works. The fact that the residue was four small docs lines, not structural design issues, indicates that the substantive design has stabilised.

## Inherited Constraints (for Phase 2~5 and any future governor-changing PR)

These items are referenced from follow-up issue bodies. They are not optional reading.

- **IC-1** Default Flow ranks **below** sandbox / approval / `.codex/rules/*` / safety hooks / Absolute Prohibitions. Escape tokens never lift any of these (R1).
- **IC-2** Each migration phase must split *shared policy* from *Claude adapter* and *Codex adapter*. The two adapters are not symmetric: Codex `PostToolUse` matcher is `^Bash$` only and **does not** see `apply_patch` / non-Bash edits (R2 + R7).
- **IC-3** Exception-token parser must operate on the leading bracketed token of the first prompt line, after NFKC normalisation, regex `^\s*\[(trivial|hotfix|exploration|자명|긴급|탐색)\](?:\s|$)` (R3). It must never short-circuit safety hooks, `.codex/rules` prefix rules, or Absolute Prohibitions (R7 + IC-1).
- **IC-4** A skill addition or change requires updating **all three wrapper layers** (`docs/ai/shared/skills/{name}.md`, `.claude/skills/{name}/SKILL.md`, `.agents/skills/{name}/SKILL.md`) with consistent information density, including the `Default Flow Position` block (R5).
- **IC-5** Verification reminders on the Codex side must rely on **changed-files state at Stop time**, not on `PostToolUse Bash` (R7).
- **IC-6** Phase acceptance criteria must not reference deliverables produced by later phases (R3-derived after Round-2; canonised in migration-strategy.md §1).
- **IC-7** Bucket-share denominator across the four design docs must reconcile to the matrix; `.gitignore`d entries (e.g. `.claude/settings.local.json`) are excluded from the share denominator but recorded for completeness.
- **IC-8** A governor-changing PR must produce or extend an entry under `docs/ai/shared/governor-review-log/`. `/sync-guidelines` checks this via drift-checklist §1D.
- **IC-9** The `auto-escape: doc-only` rule does **not** apply to policy / harness docs. See `target-operating-model.md` §3 "Auto-escapes" for the carve-out reasoning. The actual path list is in [`governor-paths.md`](../governor-paths.md) Tier A.
- **IC-10** (Round-4) Trigger-glob list lives in a single canonical document — [`governor-paths.md`](../governor-paths.md). All consumer docs (AGENTS.md, target-operating-model, migration-strategy, drift-checklist, PR template) **link** the file, never redeclare the list. Phase 5 shared module reads the same file (or its parsed form). Log-only backfill PRs are explicitly excluded (no recursion). Phase 4 gate matches log entry filename to `pr-{currentN}-` to prevent stale-entry false-negative.

## Self-Application Proof

PR #125 itself touched shared rule sources, so it qualified as governor-changing. The governor's own self-review and completion-gate steps are recorded here for the first time so that the PR is not the historical exception.

### `/review-architecture` (manual scan, structural only — no `src/` changes in this PR)

```
Scope
- Target: changed surface of PR #125 (doc/skill/wrapper/rule only; final file count read from `git diff --stat main..HEAD` at merge time)
- Audited domains: none (no src/ change)
- Important exclusions: src/ tree (untouched)

Sources Loaded
- AGENTS.md
- docs/ai/shared/project-dna.md
- docs/ai/shared/architecture-review-checklist.md

Findings
- [OK] Layer Dependency Rules — no src/ changes.
- [OK] Conversion Patterns Compliance — no DTO/Model/Schema changes.
- [OK] DTO / Response Integrity — no schema changes.
- [OK] DI Container Correctness — no container or bootstrap changes.
- [OK] Test Coverage — no production code added; no test obligations triggered.
- [OK] Worker Payload Compliance — no worker change.
- [OK] Admin Page Compliance — no admin change.
- [OK] Bootstrap Wiring — no wiring change.
- [OK] DynamoDB Domain Compliance — no DynamoDB change.

Drift Candidates
- target: docs/ai/shared/repo-facts.md
  reason: New shared docs (governor-review-log/, .github/pull_request_template.md) introduced after Pillar 4/5 landed.
  auto-fix: yes (this PR's commit handles it).
  sync-required: true
- target: docs/ai/shared/drift-checklist.md §1D
  reason: New governor-review-log invariant.
  auto-fix: yes.
  sync-required: true

Next Actions
- Apply Pillar 4~8 fixes in this PR (this commit).
- Run /sync-guidelines after artifacts land.

Completion State
- complete; clean on architecture surface, drift candidates handled by this commit.

Sync Required
- true (handled by `/sync-guidelines` invocation below)
```

### `/sync-guidelines` (manual scan against drift-checklist 1A~1D)

```
Mode: review follow-up
Input Drift Candidates: 2 consumed (governor-review-log existence; drift-checklist §1D)

project-dna: unchanged (no code-pattern shift; project-dna §0~§14 still accurate)

AUTO-FIX:
- repo-facts.md updated to register governor-review-log/ and .github/pull_request_template.md.
- drift-checklist.md §1D added.
- All four design docs reconciled to 85% / 15% / 0% / 0% bucket distribution (Round-3 fixes).
- 14 × 3 skill wrappers carry consistent Default Flow Position content (Round-2 R5).
- Shared procedure ↔ Claude wrapper ↔ Agents wrapper Hybrid C parity confirmed for all 14 skills.

REVIEW:
- none (Pillar set is decision-stable per ADR 045; no policy-judgment items left open in this commit).

Remaining: none

Next Actions:
- Re-run `/review-pr` once GitHub PR sees the additional commit (Codex round 4).
- Treat the governor as having satisfied its own quality gate for this PR.
```

## Recommendations Carried Forward

For Phase 2~5 implementations, link this entry's `Inherited Constraints` block from each PR description. Add a new entry under `governor-review-log/` per PR, with at least one round of Codex review captured.
