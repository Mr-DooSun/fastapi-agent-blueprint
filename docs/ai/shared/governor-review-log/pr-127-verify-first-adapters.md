# PR #127 — Hybrid Harness Phase 3: verify-first adapters (Claude PostToolUse + Codex Stop)

- GitHub PR: <https://github.com/Mr-DooSun/fastapi-agent-blueprint/pull/127>
- Closes: #122
- Branch: `feat/122-verify-first-adapters` → `main`
- Date range: 2026-04-27
- Cross-tool reviewer: `codex exec -m gpt-5.5 --sandbox read-only` (Round 0); Round 1 / Round 2 in progress.

## Summary

Implements Phase 3 of [ADR 045](../../history/045-hybrid-harness-target-architecture.md): adds informational verify-first reminders to both harnesses so the `verify` step of the Default Coding Flow is not silently skipped.

- **Claude side** — new `PostToolUse Edit|Write` sibling hook pair (`.claude/hooks/verify-first.sh` + `.claude/hooks/verify_first.py`). On every `.py` edit, reads the latest Phase 2 marker from `.claude/state/exception-token-*.json`; emits bilingual stderr reminder unless the token is `[exploration]`/`[탐색]`. Never blocks (HC-3.3). Fail-open on all error paths (HC-3.6).
- **Codex side** — Stop hook segment merge pattern (IC-2). New library module `.codex/hooks/verify_first.py` imported by the existing `stop-sync-reminder.py` (no new hooks.json entry). `.codex/hooks/post-tool-format.py` extended with a verify-log writer that records `pytest` / `make test` / `make demo[-rag]` / `alembic upgrade` invocations as JSONL to `.codex/state/verify-log-{session_id}.json`. `stop-sync-reminder.py` refactored to a segments list (IC-2 single output) and appends a verify-first segment when changed `.py` files exist and the current-session verify-log is absent or stale.
- Phase 2 `[exploration]`/`[탐색]` markers silence both adapters. Read-only on Phase 2 markers (IC-11; lifecycle is Phase 4 #123's responsibility). Informational only — never blocks commit or Stop (HC-3.3).
- Tests: `tests/unit/agents_shared/test_verify_first.py` (25 cases). String-equality of `REMINDER_TEXT` across tools (IC-2 cornerstone). Silence on `[exploration]`/`[탐색]` markers (both Claude and Codex). Non-silence on `[trivial]`/`[hotfix]`. Non-Python edits silent. Codex verify-log freshness (recent → silent; stale → remind). Cross-session silence prevention (R0.2). Fail-open smokes. Marker read idempotency (IC-11). 7-case parametrised verify-log writer pattern suite.
- Docs: `harness-asset-matrix.md` Tier 3 +3 rows (Total 58→61, Bucket Distribution updated); `repo-facts.md` registers `.codex/state/verify-log-{session_id}.json` surface.

R0 reinforcement applied before any implementation file was touched: import fail-open (R0.1), current-session-only verify-log to defeat cross-session silence (R0.2), subsecond `ts_epoch_ns` freshness comparison (R0.3), top-level fail-open in `post-tool-format.py` (R0.4), Codex marker silence parity tests + test name correction (R0.5).

## Review Rounds

### Round 0 — Plan Review (plan stage)

- **Target**: `/Users/coursemos/.claude/plans/122-playful-snail.md` (Phase 3 plan, §1~§15 + §16 R0 Reinforcement Log).
- **Reviewer**: `codex exec -m gpt-5.5 --sandbox read-only` (Codex CLI, read-only sandbox).
- **Final Verdict**: `still needs reinforcement` → all 5 R-points (R0.1~R0.5) reflected into plan §16 "R0 Reinforcement Log" before implementation files were created.
- **R-points** (full text in plan §16; abbreviated here):
  - **R0.1** (merge-blocking): `import verify_first` at module level in `stop-sync-reminder.py` — if import fails, entire Stop hook crashes, violating HC-3.6. → **Applied**: import moved inside `with contextlib.suppress(Exception):` block; existing sync-reminder behaviour preserved on ImportError.
  - **R0.2** (merge-blocking): `latest_verify_log_ts()` originally globbed all `verify-log-*.json` files → a prior Codex session's `pytest` run could silence the current session (cross-session contamination). → **Applied**: reads only `verify-log-{session_id()}.json` (current session); `session_id()` uses `CODEX_SESSION_ID or f"{ppid}-{pid}-{start_ns_hex}"` to defeat PPID collision across rapid Codex re-invocations. Renamed to `current_session_latest_verify_ns()`.
  - **R0.3** (merge-blocking): ISO 8601 string comparison truncated to 1-second precision → false-negative when `pytest` and `.py` edit land in the same wall-clock second. → **Applied**: JSONL stores `ts_epoch_ns: int` (`time.time_ns()`); mtime comparison uses `Path.stat().st_mtime_ns`; `should_remind()` compares `verify_ns < py_mtime_ns` (epoch-ns integers).
  - **R0.4** (merge-blocking): `post-tool-format.py` had no top-level fail-open — `json.load(sys.stdin)` could crash on invalid stdin now that the hook has Phase 3 verify-log writer responsibility. → **Applied**: entire body wrapped in `def main()` with `try/except (json.JSONDecodeError, ValueError)` around stdin parse; both format and record branches use `with contextlib.suppress(Exception):`.
  - **R0.5** (advisory): test name `test_codex_silent_when_verify_log_older_than_py_mtime` backwards (assert is `True` = reminds); Codex marker silence parity tests missing; `git status --porcelain` wording vs `_shared.changed_files()` wording. → **Applied**: test renamed `test_codex_reminds_when_verify_log_older_than_py_mtime`; `test_codex_silent_on_exploration_marker` + `test_codex_silent_on_korean_탐색_marker` added; wording uses function name.

### Round 1 — Implementation Review

- **Target**: 4-commit working tree (commits d143491, 9d88064, 000893f, 2283dad). Pytest 25/25 PASSED at submission time.
- **Reviewer**: *(pending — to be run post-PR-create; log entry extended as backfill commit)*
- **Status**: In progress.

### Round 2 — Cross-Check (gate-on-gate)

- **Target**: post-R1-fix working tree.
- **Reviewer**: *(pending — to be run after Round 1 resolves its R-points)*
- **Status**: In progress.

## Inherited Constraints

Carried from prior governor-changing PRs (no new IC introduced by Phase 3 — by design):

| IC | Source | Rule | Phase 3 application |
|---|---|---|---|
| IC-1 | PR #125 | Shared rules live in `AGENTS.md` + `docs/ai/shared/` | Phase 3 hook spec derived from `AGENTS.md` Default Flow |
| IC-2 | PR #125 | Single Stop event output (Codex) | `stop-sync-reminder.py` segments list → single `{"systemMessage": ...}` |
| IC-3 | PR #125 | Token regex canonical form in `AGENTS.md` | Phase 3 reads Phase 2 markers; no new token vocab |
| IC-4 | PR #125 | Exception tokens do not override Absolute Prohibitions | Phase 3 is informational only; no override path |
| IC-5 | PR #125 | Codex `apply_patch` is invisible to `^Bash$` matcher | Codex reminder uses Stop changed-files (`_shared.changed_files()`); verify-log writer on PostToolUse Bash only records, never emits |
| IC-6 | PR #125 | Hook spec lives in `AGENTS.md`; skills in `.agents/skills/` | Phase 3 hooks registered in `CLAUDE.md` + `AGENTS.md` sections |
| IC-7 | PR #125 | `governor-paths.md` is the canonical governor-changing path list | No new paths added in Phase 3 |
| IC-8 | PR #125 | Cross-tool review is multi-round Codex `gpt-5.5 --sandbox read-only` | Round 0 completed; Rounds 1/2 in progress |
| IC-9 | PR #125 | Governor-review-log entry required before merge (HC-3.5) | This file — log-only-backfill commit 5 |
| IC-10 | PR #125 | PR template Governor-Changing section required | PR #127 body fills the section |
| IC-11 | PR #126 | Phase 2 marker lifecycle is un-decided; Phase 3 is read-only | `read_latest_token_marker()` reads only; no delete/mutate anywhere in Phase 3 |
| HC-1 | PR #126 | Codex safety-block-first; parser runs only after safety pass | Phase 3 hooks all fail-open (HC-3.6); safety hook path unchanged |

## Self-Application Proof

*(Populated as backfill once Round 1 / Round 2 complete and self-review skills run)*

### `/review-architecture all`

```
Scope: ...
Sources Loaded: ...
Findings: ...
Drift Candidates: ...
Next Actions: ...
Completion State: ...
Sync Required: ...
```

### `/sync-guidelines`

```
Mode: ...
Input Drift Candidates: ...
project-dna: ...
AUTO-FIX: ...
REVIEW: ...
Remaining: ...
Next Actions: ...
```

### `/review-pr 127`

```
Scope: ...
Sources Loaded: ...
Findings: ...
Drift Candidates: ...
Next Actions: ...
Completion State: ...
Sync Required: ...
```

## New Inherited Constraints

None introduced by Phase 3 (by design — Phase 3 is informational only, no new lifecycle decisions).

Open questions carried into Phase 4 (#123):
- IC-11 marker lifecycle (read-and-delete vs. age-based filter vs. session-id correlation) — same open question as PR #126.
- `.codex/state/verify-log-{session_id}.json` lifecycle — shares IC-11 open question; Phase 4 decides both at once.

## 1-week soak measurement

*(Backfill commit after 2026-05-04 — false-positive rate measurement: reminder fires / total reminder events where silence would have been correct)*
