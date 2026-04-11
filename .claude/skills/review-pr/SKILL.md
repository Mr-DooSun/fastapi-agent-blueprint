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

## Core Principle: No custom rules — reference existing rule sources only

This skill does NOT define its own review criteria.
It applies existing rules from the project's rule sources to the PR diff scope.

Rule sources to load:
- `${CLAUDE_SKILL_DIR}/../review-architecture/references/checklist.md` — 20+ architecture checklist items
- `${CLAUDE_SKILL_DIR}/../security-review/references/security-checklist.md` — OWASP security items
- `${CLAUDE_SKILL_DIR}/../_shared/project-dna.md` — conversion patterns, DI rules, base classes
- `.claude/rules/architecture-conventions.md` — DO/DON'T rules
- `CLAUDE.md` — Absolute Prohibitions

## Difference from `/review-architecture`
```
/review-architecture  →  Audit an entire domain offline (full scan)
/review-pr            →  Same rules, applied only to PR diff (change-scoped)
```

## Phase 0: Resolve PR & Collect Rules

1. Resolve the target PR:
   - If a number or URL is given: `gh pr view $ARGUMENTS --json number,title,body,baseRefName,headRefName`
   - If empty: `gh pr view --json number,title,body,baseRefName,headRefName` (current branch)
   - If no PR exists for the current branch → abort with instructions to create one first

2. Fetch PR context:
   ```bash
   gh pr diff {number}
   gh pr view {number} --json files --jq '.files[].path'
   ```

3. Identify affected domains: extract domain names from paths matching `src/{name}/`

4. Load all rule sources listed above. These are the ONLY review criteria.

## Phase 1: Apply Rules to PR Diff

- Walk through each checklist item from the loaded rule sources
- For each changed file, check only the applicable rules based on its layer:
  - `domain/` files → Layer Dependency, Conversion Patterns, DTO Integrity
  - `infrastructure/` files → DI Container, Repository patterns
  - `interface/` files → Response field exposure, Router patterns
  - `application/` files → UseCase patterns
  - `migrations/` files → upgrade/downgrade existence
- When surrounding context is needed, use Grep/Read to read related code
  (e.g., cross-reference DTO fields with Response exclude set)
- Assign severity from the checklist source's own categorization

## Phase 2: Report

```
=== PR #{number}: {title} ===
Affected domains: {domain_list}
Changed files: {count}

--- Findings ---
[FAIL][BLOCKING] {checklist item name} — {file:line}
  → {what's wrong + how to fix}

[NOTE][SUGGESTION] {checklist item name} — {file:line}
  → {recommendation}

=== Summary ===
BLOCKING: {count} | SUGGESTION: {count} | PASS: {count}
```

If no violations found:
```
=== PR #{number}: {title} ===
All architecture checks passed. No violations in changed files.
```

## Phase 3: Post to GitHub (optional)

Ask the user: "Post this review to the PR?"

If yes:
- BLOCKING items present → `gh pr review {number} --request-changes --body "{review}"`
- SUGGESTION only → `gh pr review {number} --comment --body "{review}"`
- All PASS → `gh pr review {number} --approve --body "Architecture review: all checks passed"`
