# PR #128 — Hybrid Harness Phase 4: completion-gate Stop adapter

- GitHub PR: <https://github.com/Mr-DooSun/fastapi-agent-blueprint/pull/128>
- Closes: #123
- Branch: `feat/123-completion-gate-stop-adapter` → `main`
- Date range: 2026-04-27
- Cross-tool reviewer: `codex exec -m gpt-5.5 --sandbox read-only` (Round 0 hung — see §6 of plan); Round 1 in progress.

## Summary

Implements Phase 4 of [ADR 045](../../history/045-hybrid-harness-target-architecture.md): adds the completion-gate Stop adapter so the `completion gate` step of the Default Coding Flow is enforced at session end.

- **IC-11 resolution (Option A)**: Phase 2 exception-token markers are read-and-deleted by the Stop hook on both sides. `read_latest_token_marker` (both `verify_first.py` files) gains a 24h filter to skip Stop-failure leftovers. Marker schema unchanged from Phase 2 (no `session_id` field added). See §IC-11 Resolution below.
- **Pillar 7**: `completion_gate.py` (both sides) parses `governor-paths.md` at runtime (IC-10 — no inline glob re-declaration) and emits a reminder when `changed_files` intersects Tier A/B/C globs without a matching `governor-review-log/pr-{N}-*.md` entry whose `{N}` equals the current PR number. `[exploration]`/`[탐색]` token silences Pillar 7 too.
- **Claude side** — new `.claude/hooks/completion_gate.py` (~120 LOC). Called as subprocess by existing `stop-sync-reminder.sh` (HC-4.2 single Stop entry — `.claude/settings.json` unchanged). `main()` runs Pillar 7 check then `consume_phase2_markers()`.
- **Codex side** — new `.codex/hooks/completion_gate.py` (~140 LOC). Imported by existing `stop-sync-reminder.py` segments list (IC-2). Adds `governor_changing_segment()`, `consume_phase2_markers()`, `cleanup_stale_verify_logs()` (opportunistic 24h cleanup of OTHER sessions' verify-log files).
- **Phase 3 compatibility** — `verify_first.py` 24h filter is purely additive; Phase 3 test fixtures updated from hardcoded past-ts to dynamic ts.
- **Informational only** — never blocks commit or Stop (HC-4.1 / HC-3.3).
- Tests: `tests/unit/agents_shared/test_completion_gate.py` (31 cases). IC-2 GOVERNOR_REMINDER_* string-equality. `parse_trigger_globs` real file parse. `is_governor_changing` / `is_log_only_backfill` / `match_log_entry` classification. `pr_number_from_branch` fail-open smoke. 4 sample runs per `migration-strategy.md §Phase 4`. IC-11 lifecycle (consume deletes, idempotent, post-consume None). 24h stale marker ignored. `cleanup_stale_verify_logs` session isolation. Pillar 7 silence on exploration tokens / no-PR fallbacks.
- Docs: `harness-asset-matrix.md` Tier 3 +2 rows (Total 61→63, Overlay 11→13); `repo-facts.md` IC-11 resolution entry; `project-status.md` Phase 4 row.

## IC-11 Resolution (closed by Phase 4 / PR #128)

Phase 4 commits to **Option A — read-and-delete on Stop** with opportunistic 24h cleanup:

- Stop hook (both Claude and Codex sides) reads the latest marker (via `verify_first.read_latest_token_marker` or `completion_gate._read_latest_token`), applies `[exploration]`/`[탐색]` silence to its own segments, then calls `completion_gate.consume_phase2_markers()` which deletes ALL `exception-token-*.json` files in the state dir.
- `read_latest_token_marker` skips markers older than 24h (defensive against Stop-failure leftovers).
- Marker schema unchanged from Phase 2 (no `session_id` field added; PR #126 schema remains valid).
- Rationale: Stop is the sole consumer-deleter; PostToolUse readers (Phase 3 Claude `verify_first.py`) and Stop pre-segment readers (Phase 3 Codex `verify_first.should_remind`) all run before Stop's delete, so within one prompt all reads see the same file.
- Open question absorbed by Phase 5 (#124): should `.codex/state/verify-log-*.json` cleanup also be Stop-driven, or thread-aware via `CODEX_THREAD_ID` lifecycle? Phase 4 only does opportunistic 24h cleanup of *other* sessions' logs.

## Review Rounds

### Round 0 — Plan Review (plan stage)

- **Target**: `/Users/coursemos/.claude/plans/phase-4-123-snug-babbage.md` (§1~§10).
- **Reviewer**: `codex exec -m gpt-5.5 --sandbox read-only` (Codex CLI, read-only sandbox).
- **Status**: **Hung** — process ran 70+ minutes with ~0 CPU after exhausting model context. All 10 review angles are enumerated in plan §10 (Open Questions); they are carried into Round 1.
- **Fallback**: Claude self-stand-in (same as PR #126 lesson).

### Round 1 — Implementation Review

*(To be completed after pytest green + all 4 sample runs verified.)*

- **Target**: Commits `73054bc`, `cd26321`, `28edb9a`, `03fd6ed` (4 impl commits). pytest 59/59 PASSED.
- **Reviewer**: TBD (Claude cross-session or Codex re-attempt).
- **Angles to cover** (carried from Round 0 plan §10 + new impl angles):
  - R0 angles: IC-11 Option A multi-Stop edge cases; Pillar 7 false-positive/negative; 24h filter Phase 3 fixture; IC-2 single-event; governor-paths.md parse robustness; Phase 3/4 segment overlap; self-application recursion; `[trivial]` cascade vs Pillar 7; Phase 5 readiness (`.sh`+`.py` pair vs current); acceptance test coverage gaps.
  - New impl angles: `_read_latest_token` duplication in completion_gate.py vs verify_first.py; `_within_24h` duplicated 4×; Pillar 7 silence for `[trivial]`/`[hotfix]` (plan left open — currently NOT silenced).

### Round 2 — Cross-Check (gate-on-gate)

*(To be completed after Round 1 R-points applied.)*

### Self-Application Proof

*(To be filled in after Round 2 with `/review-architecture all` + `/sync-guidelines` + `/review-pr 128` outputs.)*

## Inherited Constraints

Carried from prior governor-changing PRs (no new IC introduced by Phase 4 — IC-11 is resolved, not new):

| IC | Source | Rule | Phase 4 application |
|---|---|---|---|
| IC-1 | PR #125 | Shared rules live in `AGENTS.md` + `docs/ai/shared/` | Phase 4 hook spec derived from `AGENTS.md` Default Flow + `governor-paths.md` |
| IC-2 | PR #125 | Single Stop event output (Codex) | `stop-sync-reminder.py` segments list; `GOVERNOR_REMINDER_*` string-equal Claude/Codex |
| IC-3 | PR #125 | Token regex canonical form in `AGENTS.md` | Phase 4 reads Phase 2 markers; no new token vocab |
| IC-4 | PR #125 | Exception tokens do not override Absolute Prohibitions | Phase 4 is informational only; `[exploration]` silences Pillar 7 but not blocking |
| IC-5 | PR #125 | Codex `apply_patch` is invisible to `^Bash$` matcher | Codex Pillar 7 uses Stop `changed_files()`; `completion_gate.py` is never a PostToolUse hook |
| IC-6 | PR #125 | Hook spec lives in `AGENTS.md`; skills in `.agents/skills/` | Phase 4 hooks registered in `CLAUDE.md` + `AGENTS.md` sections |
| IC-7 | PR #125 | `governor-paths.md` is the canonical governor-changing path list | Phase 4 reads this file at runtime (no inline re-declaration per IC-10) |
| IC-8 | PR #125 | Cross-tool review is multi-round Codex `gpt-5.5 --sandbox read-only` | Round 0 hung; Round 1 in progress (see §Review Rounds) |
| IC-9 | PR #125 | Governor-review-log entry required before merge (HC-3.5) | This file |
| IC-10 | PR #125 | PR template Governor-Changing section required | PR #128 body fills the section |
| IC-11 | PR #126 | Phase 2 marker lifecycle is un-decided; Phase 3 is read-only | **RESOLVED by Phase 4**: Option A (read-and-delete on Stop) + 24h defensive filter |

## New Inherited Constraints

None introduced by Phase 4. IC-11 is closed (resolved, not deferred).

Open questions carried into Phase 5 (#124):
- `.codex/state/verify-log-*.json` lifecycle — Phase 4 does opportunistic 24h cleanup of OTHER sessions' logs; Phase 5 may introduce thread-aware cleanup via `CODEX_THREAD_ID`.
- `_within_24h` helper is duplicated 4× (both `verify_first.py` files + both `completion_gate.py` files) — Phase 5 consolidates into `.agents/shared/governor/`.

## 1-week soak measurement

*(Backfill commit after 2026-05-04 — false-positive rate measurement for Pillar 7 and verify-first reminders.)*
