# PR #143 — Reasoning-Level Consistency Guards (F / G / H / I)

> Issue: none (sourced from 2026-04-28 cross-review evaluation, not from a pre-existing issue)
> Pull Request: [#143](https://github.com/Mr-DooSun/fastapi-agent-blueprint/pull/143)
> ADR: ADR 045 (constraints inherited; this PR introduces a parallel Layer 2 governor)

## Summary

Adds a new Tier 1 section `Reasoning-Level Consistency Guards`
to AGENTS.md covering four reasoning-level miss patterns that the
existing PR-level governor (ADR 045 + `.agents/shared/governor/`)
does not address by design. The four guards are F (volatile
workspace facts re-verification), G (closure classification for
cross-review R-points), H (effect vs process question
discrimination), I (self-licensing detection before defending a
challenged conclusion). The body is canonical only in AGENTS.md;
`CLAUDE.md` and `.codex/hooks/session-start.py` carry one-line
cross-references so both tool harnesses surface the new guards on
session start without duplicating the body (drift risk explicitly
rejected during round-5 review, R8.2).

The guards are sourced from documented failure modes captured
during a five-round cross-review on 2026-04-28: (1) Claude treated
a system-prompt branch snapshot as fact and corrected the user
incorrectly; (2) Claude framed an unaddressed gap as "preserved as
cross-review asset"; (3) Claude answered an effect question
("is the error rate going down?") with process content
("add or remove these ceremonies"); (4) ceremony drift across
rounds 1–2 was halted only by user pushback at round 3.

This PR is **governor-changing** because it edits Tier A
(`AGENTS.md`, `CLAUDE.md`) and Tier B (`.codex/hooks/`) per
[`governor-paths.md`](../governor-paths.md). Therefore this
self-application entry is mandatory.

Phase 1 (this PR) lands the text guards plus visibility cross-refs
only. Phase 2 (mechanical linter for G — closure status presence in
review-log entries) and Phase 3 (retrospective audit after
3–5 governor-changing PRs accumulate) are deferred to follow-up
PRs by explicit decision (round 5 R5.3 / R5.4).

## Review rounds

Five rounds of cross-tool review with Codex CLI
(`codex exec -m gpt-5.5 --sandbox read-only`) before
implementation. The review trail itself is the primary evidence
base for the four failure modes the guards encode.

### Round 1 — hybrid harness progress evaluation

- **Target**: open question from the user — "did the harness
  development meet the 'superpowers-grade' goal?"
- **Reviewer**: `codex exec` after a Claude self-evaluation.
- **Final Verdict**: partial agreement. Claude's framing
  (philosophy adoption, not external package) was supported, but
  six substantive misses were surfaced (operational verification
  not closed, KPI not declared, Phase 5 underweighted, AGENT_LOCALE
  underweighted, OTEL ≠ governor observability, "100 % achieved"
  self-licensing risk, stale-branch single-shot misread).
- **Outcome**: Claude's narrative split into "implementation scope
  achieved" vs "operational effect not yet measured".

### Round 2 — action-list verification

- **Target**: a six-action plan Claude proposed in response to
  round 1.
- **Reviewer**: same Codex thread, asked whether the action list
  was correctly scoped, prioritised, and implementable.
- **Final Verdict**: 4 fixes required — A / B ordering inverted
  (KPI definition must precede measurement), KPI count too high
  (4 → 2 primary), location of soak counter wrong
  (`.agents/shared/governor/` is policy, not telemetry; counter
  should live tool-side), `eval-2026-04-28-...md` violates the
  review-log naming convention.
- **Outcome**: action list re-shaped; "B-lite runbook" replaced
  the immediate ADR.

### Round 3 — over-engineering check

- **Target**: the user's pushback — "is that really the
  conclusion? we redesigned the harness to reduce error rate, do
  we really need to fix it again?"
- **Reviewer**: same Codex thread, instructed to evaluate whether
  the round-2 action list was actually necessary or itself
  ceremony.
- **Final Verdict**: **0 user-facing actions needed**. Round 2's
  six recommendations were retracted; only `#140` soak placeholder
  remained as a deferred-optional, conditional on sample size.
  Personal-memory rules (F / G suggestions in earlier rounds) were
  marked not load-bearing.
- **Outcome**: user intuition validated; round-2 over-correction
  identified.

### Round 4 — retrospective effect evidence

- **Target**: the question the previous three rounds had drifted
  away from — "is the error rate actually going down?"
- **Reviewer**: same Codex thread, scoped to retrospective
  evidence only (no ceremony additions).
- **Final Verdict**: PR-level governor is working, with **186
  pre-merge R / F points** logged across the existing review-log
  entries (design-contract defects 80, consistency drift 63,
  factual errors 27, cross-tool drift 16, Claude self-review
  misses 4–7). Operational soak (`#140`) cannot give a clean
  before-after comparison because the pre-`#125` PRs do not have
  a comparable trail. Layer 2 (reasoning-level) is **not** covered;
  the four-round trail itself is the evidence.
- **Outcome**: error-rate question is split into Layer 1
  (PR-level — working) and Layer 2 (reasoning-level — uncovered).
  This PR addresses Layer 2.

### Round 5 — plan review for this PR

- **Target**: the plan file `memory-agile-blanket.md` proposing
  AGENTS.md + visibility cross-refs.
- **Reviewer**: same Codex thread, asked to evaluate auto-load
  chain assumptions, guard wording, self-application status, and
  ceremony cost.
- **Final Verdict**: **"OK after fixing 4 items"** — auto-load
  chain assumption corrected (`AGENTS.md` is *not* auto-loaded;
  `CLAUDE.md` and `.codex/hooks/session-start.py` are the correct
  visibility surfaces), Codex cross-ref location corrected
  (`.codex/rules/*.rules` is a shell-prefix DSL, unsuitable for
  natural-language pointers), Tier 1 English-only enforced for the
  new section, and F / G / H / I wording tightened to avoid
  over-broad triggers and false positives.
- **Outcome**: this PR's body, location choices, and four guard
  texts all reflect the round-5 fixes.

## Inherited Constraints

Future governor-changing PRs that touch reasoning-level guards
(extending F / G / H / I, adding new guards, or moving the
canonical body) must respect:

- **IC-RG-1**: Body stays in AGENTS.md only. Visibility surfaces
  (`CLAUDE.md`, `.codex/hooks/session-start.py`) carry pointers
  only; never duplicate the body. Round-5 R8.2 (drift risk).
- **IC-RG-2**: New guards must be sourced from a documented
  failure mode in the review-log, not from speculation.
- **IC-RG-3**: Guard triggers must be narrow enough not to fire
  on general or exploratory questions. Round-5 R2.1 / R2.4
  (over-broad scope).
- **IC-RG-4**: G's closure categories are exactly three
  (Fixed / Deferred-with-rationale / Rejected). Adding a fourth
  category requires its own governor-changing PR with explicit
  rationale.
- **IC-RG-5**: Phase 2 mechanical checks (G's closure-status
  presence linter is the most amenable) belong in a separate PR.
  Phase 1 PRs must not carry mechanical enforcement and text rule
  changes together — they have different review surfaces.

## Self-Application Proof

This PR was constructed under the four guards it lands. Each guard
has a verifiable artefact in this PR's history.

- **F (Volatile facts verification)** — applied. AGENTS.md line
  numbers (Self-Review Step at line 144, Layer Architecture at
  line 163) were re-verified by `grep -n` before quoting in the
  plan and PR body. The current branch (`main` at the time of
  evaluation, then `feat/reasoning-level-guards` for the
  implementation) was confirmed by `git status` rather than
  trusting the round-1 system-prompt snapshot.
- **G (Closure classification)** — applied. Every R-point from
  round 5 was assigned one of the three closure categories in the
  plan file's "Round 5 R-points Closure Table". Categories used
  in this PR: Fixed (12), Deferred-with-rationale (2),
  Rejected (3).
- **H (Effect vs process discrimination)** — applied. The user's
  final approval question ("then how should we do it?") was
  classified as a process question, and answered with a plan
  (action candidates) rather than effect/data substitution. The
  earlier round-3 user question ("is the error rate actually going
  down?") was classified as effect and answered with the round-4
  retrospective evidence (186 R / F points).
- **I (Self-licensing detection)** — applied. The user's round-3
  pushback ("is that really the conclusion?") triggered the
  three-step check; the result (round-2 over-correction
  identified, round-1/2 stacked recommendations retracted) was
  surfaced before any defence. The user's later pushback
  ("does memory only apply to me, not to all users of this
  harness?") triggered the same check and led directly to this
  PR's repo-level artefact decision.

### `/review-architecture` equivalent (manual capture)

- **Scope**: `AGENTS.md`, `CLAUDE.md`, `.codex/hooks/session-start.py`.
- **Findings**: new section integrates cleanly with existing
  Default Coding Flow + Self-Review Step structure; no new
  Domain → Infrastructure import surface; no Tier 1 Language
  Policy violations (`tools/check_language_policy.py` reports 0
  violations across 162 scanned files).
- **Drift Candidates**: `governor-review-log/README.md` Entry
  shape currently does not require closure-status presence; this
  is a known gap and the canonical entry shape may be tightened
  in the Phase 2 PR (G's mechanical linter), not in Phase 1.
- **Sync Required**: `false` — the canonical Entry shape and
  Reasoning-Level Guards section are coherent at the Phase 1
  level.

### `/sync-guidelines` equivalent (manual capture)

- **Mode**: standalone closure for this Tier A change.
- **Input Drift Candidates**: 0 from `/review-architecture`.
- **AUTO-FIX**: 0 — no auto-fixable drift was found.
- **REVIEW**: 0 — no manual reconciliation needed beyond the new
  section itself.
- **Remaining**: 0.
- **Next Actions**: file Phase 2 work (G mechanical linter) as a
  separate issue when sample governor-review-log entries
  accumulate enough to write the linter against; this PR does
  not block on it.

## R-points Closure Table

| Source | R-point | Closure | Note |
|---|---|---|---|
| Round 1 | operational verification not closed | **Deferred-with-rationale** | `#140` soak placeholder; Phase 2 of this work, not Phase 1 |
| Round 1 | "100 % achieved" self-licensing risk | **Fixed** | this PR splits implementation-scope vs operational-effect explicitly |
| Round 1 | Phase 5 underweighted | **Rejected** | `pr-130` log already records v1 closure with acceptance proof |
| Round 1 | AGENT_LOCALE underweighted | **Rejected** | `#133` belongs to a separate axis; not an ADR 045 closure defect |
| Round 1 | OTEL ≠ governor observability | **Rejected after correction** | one-line clarification; not load-bearing |
| Round 1 | KPI not declared | **Deferred-with-rationale** | not load-bearing at sample size of 1 dogfooder |
| Round 2 | A / B ordering | **Fixed** | reflected in plan |
| Round 2 | KPI count too high (4 → 2) | **Fixed** | reflected in plan; runbook-class scope |
| Round 2 | counter location wrong | **Fixed** | reflected in plan |
| Round 2 | eval-2026-04-28 violates naming | **Fixed** | this entry is `pr-143-...`, conventional |
| Round 3 | round-2 six recommendations | **Fixed (retracted)** | replaced by 0 user-facing actions; only `#140` placeholder remains |
| Round 4 | Layer 2 (reasoning-level) uncovered | **Fixed** | this PR is the response |
| Round 5 | R1.2 — auto-load chain assumption | **Fixed** | plan's "Auto-load Chain" section corrected |
| Round 5 | R1.3 — Codex `.rules` cross-ref unsuitable | **Fixed** | cross-ref moved to `.codex/hooks/session-start.py` |
| Round 5 | R1.4 — `.claude/rules/architecture-conventions` semantic mismatch | **Fixed** | cross-ref moved to `CLAUDE.md` Collaboration Rules |
| Round 5 | R1.5 — Language Policy pattern overclaim | **Fixed** | "reduced variant" rather than "same pattern" |
| Round 5 | R2.1 — F scope too broad | **Fixed** | scope tightened to consequential assertions |
| Round 5 | R2.2 — G banned-words too rigid | **Fixed** | "preserve" allowed in prose; only banned as a closure category |
| Round 5 | R2.3 — H mixed-question failure | **Fixed** | mixed-question rule added (effect first, process second, separately labelled) |
| Round 5 | R2.4 — I trigger too narrow / too wide | **Fixed** | trigger limited to correction / challenge / evidence-request |
| Round 5 | R2.5 — Tier 1 English-only | **Fixed** | section body in English; Korean only in `Why` references to dialogue, never in policy text |
| Round 5 | R3.3 — application order | **Fixed** | "Application order" subsection added |
| Round 5 | R5.3 — G mechanical linter Phase 2 | **Deferred-with-rationale** | Phase 2 PR; out of this PR's scope |
| Round 5 | R5.4 — Phase 3 retrospective | **Deferred-with-rationale** | needs accumulated samples; out of scope |
| Round 5 | R7.1 — stale memory absorbed into F | **Fixed** | F's "scope" paragraph adds prior-round summaries and memory entries |
| Round 5 | R7.2 — user-intent loss absorbed into H | **Fixed** | H's "Multi-round preservation" paragraph added |
| Round 5 | R7.3 — separate rule J | **Rejected** | absorption into F / H is sufficient at four-rule scope |
| Round 5 | R8.1 — `.codex/rules` location | **Fixed** | moved to `.codex/hooks/session-start.py` |
| Round 5 | R8.2 — single PR vs split | **Fixed** | this PR is Phase 1 only; Phase 2 / 3 are separate |
| Round 5 | R8.3 — eval-only entry vs PR entry | **Fixed** | this is a PR-numbered entry; the four-round trail is folded into Review Rounds above |
| Plan-level | duplicate body in `.claude/rules` and `.codex/rules` | **Rejected** | drift risk outweighs benefit |
| Plan-level | new ADR 047 | **Rejected** | live collaboration rule, not an immutable architecture decision |
