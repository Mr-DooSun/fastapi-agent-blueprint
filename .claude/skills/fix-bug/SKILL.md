---
name: fix-bug
argument-hint: "bug description or issue number"
description: |
  This skill should be used when the user asks to
  "fix bug", "resolve issue", "fix error", "troubleshoot",
  "debug", or reports a specific bug or error that needs investigation and fixing.
---

# Bug Fix Workflow

Bug description: $ARGUMENTS

## Procedure Overview
1. Reproduce — identify affected domain/layer, write failing test (Phase 1)
2. Trace — follow call path, inspect conversion boundaries and DI wiring (Phase 2)
3. Fix — fix at lowest layer, follow existing patterns (Phase 3)
4. Verify — confirm test passes, run domain tests and pre-commit (Phase 4)
5. Commit — propose conventional commit message (Phase 5)

Read `docs/ai/shared/skills/fix-bug.md` for detailed steps.
Also refer to `docs/ai/shared/project-dna.md` §6 for conversion patterns and §9 for router patterns.
