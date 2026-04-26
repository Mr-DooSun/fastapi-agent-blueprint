# Governor Review Log

> Living archive of cross-tool review trails for **governor-changing PRs**.
> Source of truth: ADR 045 §Self-Application Recovery + AGENTS.md § Default Coding Flow §Cross-Tool Review.

## Purpose

Issue #117 introduced a hybrid local process governor (ADR 045). The review trail that produced ADR 045 — three rounds of Codex `gpt-5.5 --sandbox read-only` review — is *itself* a load-bearing piece of context that subsequent governor-changing PRs (Phase 2~5 of [migration-strategy.md](../migration-strategy.md), and any future shared-rule edit) must inherit to avoid re-discovering the same blind spots.

This directory exists so that the trail is not buried in PR descriptions.

## Scope (which PRs need a log entry)

A PR is **governor-changing** — and therefore must add an entry here — if it touches any of:

- `AGENTS.md`
- `docs/ai/shared/**` (any file)
- `docs/history/**` (ADR or archive)
- `.claude/**` (rules, skills, hooks, settings)
- `.codex/**` (config, hooks, rules)
- `.agents/**` (skills, shared modules)
- `.github/pull_request_template.md` or other repo-level governance artifacts

For non-governor-changing PRs (regular feature, bug fix, refactor inside `src/`), no entry is required.

## File naming

```
pr-{NNN}-{short-slug}.md
```

Example: `pr-125-hybrid-harness-target-architecture.md`.

The number is the GitHub PR number. The slug is a kebab-cased short title (≤ 60 chars).

## Entry shape

Each entry must contain at minimum:

1. **Summary** — one-paragraph PR description, link to GitHub PR.
2. **Review rounds** — ordered list of Codex review rounds (or equivalent cross-tool review). Each round captures: target, prompt focus, surfaced points (R1, R2, ...), Final Verdict.
3. **Inherited constraints** — the R-points and lessons that future governor-changing PRs must respect. This is the part that is link-cited from follow-up issues.
4. **Self-application proof** — explicit invocation of `/review-architecture` and `/sync-guidelines` on the PR's own changed surface, with their canonical outputs (Findings / Drift Candidates / Sync Required / Remaining). Required so that the governor proves it followed itself.

## Retention

Entries are kept for the lifetime of the repository. The matrix and the migration-strategy document rely on this directory as a permanent reference.

If a future ADR consolidates or rotates entries (e.g. annual archive subdirectories), that decision is itself a governor-changing PR that must add its own entry here.

## Drift discipline

`docs/ai/shared/drift-checklist.md` §1D verifies that every governor-changing PR merged into `main` has a corresponding log entry. `/sync-guidelines` consumes that row.

## Index

| PR | Title | Issue | Entry |
|---|---|---|---|
| #125 | hybrid harness target architecture + Phase 1 | #117 | [pr-125-hybrid-harness-target-architecture.md](pr-125-hybrid-harness-target-architecture.md) |
