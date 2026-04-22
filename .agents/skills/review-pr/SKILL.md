---
name: review-pr
description: Review a pull request or local diff against the repository's shared architecture, security, and workflow rules.
metadata:
  short-description: Review PR or local diff
---

# Review PR

1. Read `AGENTS.md` and `docs/ai/shared/skills/review-pr.md` for the full procedure.
2. Read `docs/ai/shared/architecture-review-checklist.md`, `docs/ai/shared/security-checklist.md`, and `docs/ai/shared/project-dna.md` as shared rule sources.
3. Resolve the review target and load the shared rule sources (Phase 0).
4. Review changed files against the shared architecture and security rules (Phase 1).
5. Determine `Drift Candidates` and whether `Sync Required` is `true` or `false` (Phase 2).
6. Report using the shared review contract: `Scope`, `Sources Loaded`, `Findings`, `Drift Candidates`, `Next Actions`, `Completion State`, `Sync Required` (Phase 3).
7. Optionally post the final review after user confirmation (Phase 4).
