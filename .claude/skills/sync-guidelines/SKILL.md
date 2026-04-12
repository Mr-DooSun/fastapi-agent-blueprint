---
name: sync-guidelines
disable-model-invocation: true
description: |
  This skill should be used when the user asks to "sync guidelines",
  "document inspection", "check skill updates",
  "update project-dna", "sync patterns", "verify code-document consistency",
  or after architecture changes to verify Skills/AGENTS.md/CLAUDE.md match the actual code.
---

# Guideline Synchronization Inspection

## Procedure Overview
1. Reference code analysis — read `src/user/` for current patterns
2. Code ↔ Documentation consistency check — AGENTS.md, shared refs, harness docs, skills, `.claude/rules/` (Phase 1-3)
3. project-dna.md regeneration — extract from code and update (Phase 4)
4. References drift inspection — AUTO-FIX and REVIEW targets (Phase 5)

Read `docs/ai/shared/skills/sync-guidelines.md` for detailed steps.
Also refer to `docs/ai/shared/drift-checklist.md` for inspection items.

## Claude-Specific Post-Steps
After completing the shared procedure:
1. Update `.claude/rules/architecture-conventions.md`
   (data flow, object roles, generic signatures changes)
2. Update `.claude/rules/project-status.md`
   (Recent Major Changes table, version context, violation status)
   - `git log --oneline --since="{last_synced_date}"` to identify major changes
   - project-dna.md §8 "Not implemented" items for Not Yet Implemented
3. Update `.claude/rules/project-overview.md`
   (infrastructure options, environment config, app entrypoint changes)
4. Update `.claude/rules/commands.md`
   (new CLI commands, env vars, test commands, verification commands)

All rules files: update "Last synced" date line to current date.
