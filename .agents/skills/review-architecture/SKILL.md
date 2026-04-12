---
name: review-architecture
description: Audit a domain or the full repository for architecture compliance using the shared architecture checklist and repository rules.
metadata:
  short-description: Architecture compliance audit
---

# Review Architecture

1. Read `AGENTS.md`, `docs/ai/shared/project-dna.md`, and `docs/ai/shared/architecture-review-checklist.md`.
2. Decide whether to scan one domain or all domains.
3. Apply the checklist category by category:
   - layer dependency rules
   - conversion pattern compliance
   - DTO and response integrity
   - DI correctness
   - test coverage
   - worker payload compliance
   - admin page compliance
   - bootstrap wiring
4. Report findings with severity and actionable fixes.
5. When no findings exist, say so explicitly and note any residual verification gaps.
