---
name: fix-bug
description: Investigate, reproduce, fix, and verify a bug while staying inside existing repository patterns and architecture rules.
metadata:
  short-description: Structured bug-fix workflow
---

# Fix Bug

1. Read `AGENTS.md` and `docs/ai/shared/skills/fix-bug.md` for the full procedure.
2. Reproduce the bug first. If no failing test exists, add one when feasible.
3. Trace the path from interface to persistence, inspecting conversion boundaries and DI wiring.
4. Fix the issue at the lowest sensible layer without introducing new patterns.
5. Verify with focused tests, then broader checks as needed.
6. If the user wants a commit, propose a conventional commit message after verification.
