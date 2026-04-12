---
name: fix-bug
description: Investigate, reproduce, fix, and verify a bug while staying inside existing repository patterns and architecture rules.
metadata:
  short-description: Structured bug-fix workflow
---

# Fix Bug

1. Reproduce the bug first. If no failing test exists, add one when feasible.
2. Read `AGENTS.md` and `docs/ai/shared/project-dna.md`.
3. Trace the path from interface to persistence and inspect conversion boundaries plus DI wiring.
4. Fix the issue at the lowest sensible layer.
5. Do not introduce new patterns during a bug fix unless the bug itself proves an existing pattern is wrong.
6. Verify with focused tests, then broader checks as needed.
7. If the user wants a commit, propose a conventional commit message after verification.
