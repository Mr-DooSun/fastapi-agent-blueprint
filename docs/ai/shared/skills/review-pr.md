# Pull Request Quality Gate Review

## Default Flow Position

This skill participates in the [Default Coding Flow](../../../../AGENTS.md#default-coding-flow) at the **`completion gate`** step.

It is invoked at the end of work — after `implement`, `verify`, and `self-review` have settled — to apply a final architecture- and security-aware review against the change set as a whole.

After completion-gate review, route to:
- `/sync-guidelines` if the review reported `Drift Candidates` or `Sync Required: true`

Recursion guard: do **not** invoke `/review-pr` recursively from within itself, and do not invoke `/plan-feature` from inside this skill (the change has already been implemented).

## Core Principle

This skill does not define custom review rules.
It applies the project's shared rule sources to the PR diff and decides whether
the quality gate can close or must continue into `/sync-guidelines`.

Only shared rule sources may create findings:
- `AGENTS.md`
- `docs/ai/shared/project-dna.md`
- `docs/ai/shared/architecture-review-checklist.md`
- `docs/ai/shared/security-checklist.md`

Tool-specific convention files, if available, may help with wording or
navigation, but they must not introduce findings that are not already backed by
the shared rule sources above.

## Review Contract

Every result must include the sections below.

- `Scope` - PR number/title, base/head refs, affected domains, changed file count
- `Sources Loaded` - exact shared rule sources used for the review
- `Findings` - only open issues; each item includes `severity`, `rule source`,
  `file:line`, `impact`, and `recommended fix`
- `Drift Candidates` - shared docs, checklists, wrappers, or `project-dna`
  targets that may need sync; each item includes `target`, `reason`,
  `auto-fix`, and `sync-required`
- `Next Actions` - code fixes, follow-up review, sync request, optional GitHub
  posting
- `Completion State` - concise closure status for the review
- `Sync Required` - explicit `true` or `false`

### Severity Taxonomy

Use a separate review state and severity. Do not mix them.

- Review state: `OPEN`, `OK`, `SKIP`
- Severity: `BLOCKING`, `HIGH`, `MEDIUM`, `LOW`, `NOTE`

## Difference from `/review-architecture`

```text
/review-pr            -> review only changed files, then decide whether sync is required
/review-architecture  -> audit a domain or the full repo structure outside PR scope
```

## Phase 0: Resolve Target and Collect Evidence

1. Resolve the review target.
   - If a PR number or URL is given: inspect that PR
   - If omitted: inspect the current branch diff or current branch PR
   - If no review target exists, stop with instructions to create or identify one
2. Collect the diff, changed filenames, affected domains, and surrounding code
   when a changed file alone is not enough to judge the rule.
3. Load the shared rule sources listed above before forming findings.
4. AGENTS.md § Language Policy (cross-ref): if the diff inserts non-English
   prose into Tier 1 paths, surface as a `Findings` violation and a
   `Sync Required: true` candidate. Bilingual escape tokens are exempt.

## Phase 1: Review Changed Files Against Shared Rules

Walk through changed files and apply only the relevant checklist categories.

- `domain/` -> layer dependency, conversion patterns, DTO integrity
- `application/` -> orchestration, dependency boundaries
- `infrastructure/` -> DI, repository, provider, storage, worker, logging rules
- `interface/` -> router, response exposure, admin, auth, validation rules
- `migrations/` -> upgrade/downgrade completeness and compatibility concerns
- shared docs / skill wrappers -> drift risk, source-of-truth alignment, quality
  gate follow-up

Use surrounding context whenever a rule depends on code outside the diff.

## Phase 2: Determine Drift Candidates and Sync Requirement

After findings are collected, determine whether the PR also created or exposed
reference drift.

Mark `Sync Required: true` when at least one of the following is true:
- the diff touches `AGENTS.md`, `docs/ai/shared/`, `project-dna`, checklist
  files, skill procedures, or tool wrappers
- the diff touches shared/base architecture files whose patterns are documented
- the review discovers a mismatch between code and shared references
- the review discovers stale feature detection assumptions that should update
  `project-dna` or a checklist

When a drift exists, create a `Drift Candidates` entry even if the code change
itself is otherwise acceptable.

## Phase 3: Report Using the Review Contract

Use the contract sections exactly and keep the result action-oriented.

Example:

```text
Scope
- PR #128: Add DynamoDB-backed docs query path
- Affected domains: docs, _core
- Changed files: 7

Sources Loaded
- AGENTS.md
- docs/ai/shared/project-dna.md
- docs/ai/shared/architecture-review-checklist.md
- docs/ai/shared/security-checklist.md

Findings
- [OPEN][HIGH] Architecture checklist - src/docs/infrastructure/di/docs_container.py:18
  Impact: container wiring uses the wrong dependency source for DynamoDB mode.
  Recommended fix: switch to `core_container.dynamodb_client` and keep RDB wiring out.
- [OK][MEDIUM] Architecture checklist §5 - Test coverage: all 3 baseline test files present for docs domain
- [SKIP] Security checklist §4.2 - File Upload input validation: project-dna §8 and live code both confirm feature inactive

Drift Candidates
- target: docs/ai/shared/architecture-review-checklist.md
  reason: PR introduces DynamoDB-specific guidance that the shared checklist does not mention consistently.
  auto-fix: no
  sync-required: true

Next Actions
- Fix the container wiring issue.
- Run `/sync-guidelines` after the DynamoDB guidance is updated.
- Post the review to GitHub only after the findings are addressed.

Completion State
- complete with findings

Sync Required
- true
```

If no issues are found, still emit all sections and explicitly state
`Findings: none`, `Drift Candidates: none`, and `Sync Required: false`.

## Phase 4: Post to GitHub (Optional)

Ask before posting.

- `BLOCKING` findings present -> request changes
- only `HIGH` / `MEDIUM` / `LOW` / `NOTE` findings -> comment
- no findings and `Sync Required: false` -> approve or leave a clean comment

If `Sync Required: true`, do not treat the review as fully closed until the
follow-up sync path is acknowledged.
