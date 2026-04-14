---
name: sync-guidelines
description: Inspect drift between code, shared workflow references, and Claude or Codex harness assets after architecture or workflow changes.
metadata:
  short-description: Sync shared guidelines
---

# Sync Guidelines

## Procedure Overview
1. Reference code analysis — read `src/user/` for current patterns
2. Code ↔ Documentation consistency check — `AGENTS.md`, shared refs, harness docs, skills, `.claude/rules/` (Phase 1-3)
3. `project-dna.md` regeneration — extract from code and update when drift exists (Phase 4)
4. References drift inspection — report both `AUTO-FIX` and `REVIEW` targets (Phase 5)

Read `AGENTS.md` and `docs/ai/shared/skills/sync-guidelines.md` for the full procedure.
Also refer to `docs/ai/shared/drift-checklist.md` for detailed inspection items.

## Completion Contract
`$sync-guidelines` is not complete until the result explicitly reports all of:
- `project-dna` — regenerated or confirmed unchanged
- `AUTO-FIX` — automatic drift targets and whether they were applied
- `REVIEW` — human-review targets and why they need review, or `none`
- `Remaining` — unresolved drift items, or `none`

If any `REVIEW` item exists, do not close with “nothing to change” or equivalent wording.
