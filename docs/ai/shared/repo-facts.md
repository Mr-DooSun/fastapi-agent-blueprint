# Shared Repo Facts

This file contains stable repository facts for both Claude and Codex workflows.

## Canonical Sources

- Shared rules: `AGENTS.md`
- Shared workflow references: `docs/ai/shared/`
- Claude harness: `CLAUDE.md`, `.claude/`
- Codex harness: `.codex/config.toml`, `.codex/hooks.json`, `.agents/skills/`, `.agents/plugins/`

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
