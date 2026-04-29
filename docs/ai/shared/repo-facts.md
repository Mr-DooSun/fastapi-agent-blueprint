# Shared Repo Facts

This file contains stable repository facts for both Claude and Codex workflows.

## Canonical Sources

- Shared rules: `AGENTS.md`
- Shared workflow references: `docs/ai/shared/`
- Claude harness: `CLAUDE.md`, `.claude/`
- Codex harness: `.codex/config.toml`, `.codex/hooks.json`, `.agents/skills/`

## Reference Code

- Use `src/user/` as the reference RDB domain when checking current patterns.
- Shared infrastructure lives under `src/_core/`.
- App entrypoints and bootstrap wiring live under `src/_apps/`.

## Shared Workflow Asset Map

- `docs/ai/shared/project-dna.md`: architecture truth and reference patterns
- `docs/ai/shared/scaffolding-layers.md`: new-domain file layout
- `docs/ai/shared/planning-checklists.md`: plan-feature questions, security matrix, task mapping
- `docs/ai/shared/architecture-review-checklist.md`: architecture audit rules
- `docs/ai/shared/security-checklist.md`: OWASP-oriented review checklist
- `docs/ai/shared/test-patterns.md`: domain test generation patterns
- `docs/ai/shared/drift-checklist.md`: rule and docs drift inspection items
- `docs/ai/shared/onboarding-role-tracks.md`: onboarding depth tracks
- `docs/ai/shared/harness-asset-matrix.md`: living inventory of every harness asset and its bucket (Keep / Replace / Overlay / Drop)
- `docs/ai/shared/target-operating-model.md`: 7-step Default Coding Flow + exception-token vocabulary + Claude/Codex alignment + sample-workflow traces
- `docs/ai/shared/migration-strategy.md`: phased migration plan for the hybrid harness target architecture (Phase 0~5)
- `docs/ai/shared/governor-review-log/`: permanent archive of cross-tool review trails for governor-changing PRs (ADR 045 Pillar 4); see `governor-review-log/README.md` for entry shape and prompt template
- `docs/ai/shared/governor-paths.md`: canonical source of governor-changing path globs (Tier A / B / C + exclusions). All consumer docs link this file; do not redeclare the list (Round-4 R4.3)
- `.agents/shared/governor/` (Phase 5 / #124): shared governor *policy* Python package consumed by Claude/Codex hook adapters as thin shims. Eight modules — `paths.py` (REPO_ROOT discovery), `time_window.py` (single `_within_24h`), `tokens.py` (Phase 2 parser + EXPLORATION_TOKENS), `markers.py` (write_marker + read_latest_token + MarkerLifecycle enum + consume_phase2_markers per IC-11/IC-12), `safety.py` (HC-1 single-entry `safe_parse_exception_token` returning `Blocked | ParsedToken`), `verify.py` (Phase 3 REMINDER_TEXT + should_remind_claude), `completion_gate.py` (Phase 4 GateResult + evaluate_gate + render_reminder + parse_trigger_globs + match_log_entry), and `__init__.py` (public API + `__all__`). Boundary: this package owns *policy*; tool-specific runtime utilities (`.codex/hooks/_shared.py`, Codex `session_id()` / verify-log writer / `cleanup_stale_verify_logs`) remain per-tool. Hooks must not redeclare reminder strings or governor-paths globs inline (`tests/unit/agents_shared/test_governor_boundary.py` enforces this).
- `tools/check_g_closure.py` (#145): pre-commit / CI checker enforcing the canonical `R-points Closure Table` shape and closure labels for governor review-log PR entries.
- `.github/pull_request_template.md`: GitHub PR template with the Governor-Changing PR checklist that artefact-locks cross-tool review and self-application proof (ADR 045 Pillar 5)
- `.claude/state/` + `.codex/state/` (gitignored): per-session governance state surfaces. Phase 2 (#121) writes exception-token marker JSON files here when a leading `[trivial]` / `[hotfix]` / `[exploration]` / `[자명]` / `[긴급]` / `[탐색]` token is recognised. Phase 4 (#123) resolves the IC-11 lifecycle: **Option A — read-and-delete on Stop**. Both `stop-sync-reminder.sh` (Claude) and `stop-sync-reminder.py` (Codex) invoke `completion_gate.consume_phase2_markers()` which deletes all `exception-token-*.json` files in the respective state dir after reading. `read_latest_token_marker` also skips markers older than 24h (defensive against Stop-failure leftovers).
- `.codex/state/verify-log-{session_id}.json` (gitignored): Phase 3 (#122) per-session verify-class command log. JSONL append-only — `.codex/hooks/post-tool-format.py` records `pytest` / `make test` / `make demo[-rag]` / `alembic upgrade` invocations. `.codex/hooks/stop-sync-reminder.py` reads only the *current session's* file (R0.2 — defeats cross-session silence) to decide whether to emit the verify-first reminder segment. Each entry stores `ts_epoch_ns` (R0.3) for subsecond freshness comparison against `Path.stat().st_mtime_ns`. Phase 4 (#123) adds opportunistic 24h cleanup of OTHER sessions' stale log files via `completion_gate.cleanup_stale_verify_logs()` on Stop; the current session's log is never deleted.

## Context Management

- Keep root `AGENTS.md` short and stable.
- Use nested `AGENTS.override.md` for directory-local rules when a subtree needs extra guidance.
- Put repeatable procedures in `.agents/skills/*/SKILL.md`.
- Use `codex -p research` or `codex --search` only when live web search is necessary.
- Treat Codex memories as personal or session-local optimization only, never as team governance.

## Verification Commands

```bash
codex mcp list
codex mcp get context7
codex debug prompt-input -c 'project_doc_max_bytes=400' "healthcheck" | rg "Shared Collaboration Rules|AGENTS\\.md"
codex execpolicy check --rules .codex/rules/fastapi-agent-blueprint.rules git push origin main
```

## Why context7 stays MCP (not plugin) — 2026-04-26 review

We considered migrating context7 from MCP (`.mcp.json` + `.codex/config.toml`)
to a Claude Code / Codex CLI plugin, motivated by `uv sync`-style one-shot
team setup. Decision: **keep MCP**. Two findings drove this:

- **Plugin SKILL auto-trigger reliability ≈ 50% in practice.** Token-budget
  truncation, YAML formatter conflicts, and Claude's task-completion bias
  cause silent skips. MCP + the explicit `CLAUDE.md` "Proactively use
  context7" rule yields deterministic invocation.
- **upstash/context7 has no official Codex CLI plugin.** Official targets
  are `--cursor`, `--claude`, `--opencode`. Splitting Claude(plugin) /
  Codex(MCP) creates a dual-track setup; using a third-party Codex plugin
  introduces maintenance risk.

Re-evaluate when any of the following becomes true:

1. upstash/context7 ships an official Codex CLI plugin.
2. Claude Code supports plugin auto-install ([anthropics/claude-code#28310](https://github.com/anthropics/claude-code/issues/28310)).
3. Skill auto-trigger reliability publicly improves to ≥ 80%, or the
   `SLASH_COMMAND_TOOL_CHAR_BUDGET` default is raised meaningfully.
4. The team grows enough that plugin-based onboarding automation becomes
   a clear win over the current `.mcp.json` + `.codex/config.toml` flow.
