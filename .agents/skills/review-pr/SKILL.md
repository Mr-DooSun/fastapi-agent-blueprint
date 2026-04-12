---
name: review-pr
description: Review a pull request or local diff against the repository's shared architecture, security, and workflow rules.
metadata:
  short-description: Review PR or local diff
---

# Review PR

1. Read `AGENTS.md`, `docs/ai/shared/project-dna.md`, `docs/ai/shared/architecture-review-checklist.md`, and `docs/ai/shared/security-checklist.md`.
2. Resolve the review target:
   - PR number or URL when provided
   - current branch diff otherwise
3. Limit the review to changed files, but inspect surrounding context when needed to confirm behavior.
4. Prioritize findings:
   - blocking bugs or regressions
   - architecture violations
   - security risks
   - missing tests
5. Output findings first with file and line references.
6. Only summarize after the findings list, or state explicitly when no findings were found.
