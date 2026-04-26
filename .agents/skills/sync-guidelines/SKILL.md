---
name: sync-guidelines
description: Inspect drift between code, shared workflow references, and Claude or Codex harness assets after architecture or workflow changes.
metadata:
  short-description: Sync shared guidelines
---

# Sync Guidelines

## Default Flow Position
- Step: **`completion gate`** (or follow-up to `self-review` when drift detected)
- Routes after: end of work
- Recursion guard: do not invoke `/sync-guidelines` recursively, do not invoke `/plan-feature` from inside

## Procedure
1. Read `AGENTS.md` and `docs/ai/shared/skills/sync-guidelines.md` for the full procedure.
   Also refer to `docs/ai/shared/drift-checklist.md` for detailed inspection items.
2. Determine the sync mode, gather incoming `Drift Candidates`, and load the governing sources (Phase 0).
3. Reconcile drift candidates with code, shared references, harness docs, and wrappers (Phase 1).
4. Refresh `project-dna` and dependent shared references as needed (Phase 2).
5. Verify Hybrid C parity for both Claude and Codex wrappers, then close with the sync contract (Phase 3).
