---
name: review-pr
description: Review a pull request or local diff against the repository's shared architecture, security, and workflow rules.
metadata:
  short-description: Review PR or local diff
---

# Review PR

1. Read `AGENTS.md` and `docs/ai/shared/skills/review-pr.md` for the full procedure.
2. Read `docs/ai/shared/architecture-review-checklist.md` and `docs/ai/shared/security-checklist.md`.
3. Resolve the review target (PR number, URL, or current branch diff).
4. Limit the review to changed files, inspecting surrounding context when needed.
5. Prioritize: blocking bugs > architecture violations > security risks > missing tests.
6. Output findings with file/line references, then summarize.
