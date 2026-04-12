---
name: review-pr
argument-hint: "PR number, URL, or omit to detect current branch"
description: |
  Review a pull request against project architecture rules.
  Use when the user asks to "review PR", "check PR", "PR review",
  or wants architecture-aware review of a pull request before merge.
---

# Pull Request Architecture Review

Target: $ARGUMENTS (PR number, GitHub URL, or empty for current branch)

## Procedure Overview
1. Resolve PR & collect rules — load architecture/security checklists (Phase 0)
2. Apply rules to PR diff — check per layer, assign severity (Phase 1)
3. Report — BLOCKING/SUGGESTION/PASS findings (Phase 2)
4. Post to GitHub — optional, after user confirmation (Phase 3)

Read `docs/ai/shared/skills/review-pr.md` for detailed steps and output format.

## Claude-Specific: Rule Sources
Also load `.claude/rules/architecture-conventions.md` for additional DO/DON'T context.
