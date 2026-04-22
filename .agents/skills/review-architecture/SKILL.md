---
name: review-architecture
description: Audit a domain or the full repository for architecture compliance using the shared architecture checklist and repository rules.
metadata:
  short-description: Architecture compliance audit
---

# Review Architecture

1. Read `AGENTS.md` and `docs/ai/shared/skills/review-architecture.md` for the full procedure.
2. Read `docs/ai/shared/architecture-review-checklist.md` and `docs/ai/shared/project-dna.md` as the shared architecture rule sources.
3. Resolve the audit target and load the shared rule sources (Phase 0).
4. Audit the target against the 9 architecture checklist categories (Phase 1).
5. Determine `Drift Candidates` and whether `Sync Required` is `true` or `false` (Phase 2).
6. Report using the shared review contract: `Scope`, `Sources Loaded`, `Findings`, `Drift Candidates`, `Next Actions`, `Completion State`, `Sync Required` (Phase 3).
