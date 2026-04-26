# Governor-Changing Paths (Canonical Source)

> Last synced: 2026-04-26 (introduced in Round-4 self-coherence review of PR #125 to reconcile path lists across AGENTS.md / target-operating-model.md / migration-strategy.md / drift-checklist.md / .github/pull_request_template.md).
> All references to "governor-changing paths" in any harness document **must** link this file rather than re-declare the list. Drift between copies is the failure mode this file exists to prevent.

## Purpose

ADR 045 introduced the concept of *governor-changing PRs* — PRs whose changed-files intersect a specific glob. Five separate documents reference this concept; before this file existed, each had its own slightly different list. Round 4 of the cross-tool review found the divergence and recommended canonicalisation. The hook and parser implementations of Phase 2~5 will eventually read this file (or its parsed form) as the single source.

## The Path List

A PR is **governor-changing** if its `changed_files` intersects any path below.

### Tier A — Constitutional / Policy Documents (always trigger)

- `AGENTS.md`
- `docs/ai/shared/**` (every file under the shared reference directory, including `governor-review-log/**`)
- `docs/history/**` (every ADR and archive entry)
- `.claude/rules/**`
- `.codex/rules/**`
- `.github/pull_request_template.md`

The doc-only auto-escape (`target-operating-model.md` §3) does **not** apply to Tier A. Even a one-line edit triggers `framing → plan → verify → self-review → completion gate`.

### Tier B — Tool-Specific Harness Surfaces (always trigger)

- `.claude/**` (settings, skills, hooks — entire directory)
- `.codex/**` (config, hooks, settings — entire directory; rules already in Tier A)
- `.agents/**` (skills, future shared modules — entire directory)

Tier B includes Tier A's `.claude/rules/**` and `.codex/rules/**` (those are the policy subset of Tier B). Mentioning both `Tier A` and `Tier B` separately is intentional: Tier A captures the *policy* lens (carve-out from doc-only escape), Tier B captures the *tool surface* lens (full directory triggers cross-tool review).

### Tier C — Other Repo-Level Governance Artefacts (trigger if introduced)

- `.github/workflows/**` (CI as governance)
- `pyproject.toml`'s `[tool.ruff]`, `[tool.mypy]`, or other linting/typing/policy sections
- `pre-commit-config.yaml`
- Any new file at the repo root that defines policy (future ADR will add)

Tier C is intentionally narrow today; the list grows only when an ADR explicitly extends it.

## Exclusions (NOT governor-changing even though path-glob looks close)

- **Log-only backfill PRs**: a PR whose `changed_files` is **entirely under** `docs/ai/shared/governor-review-log/` (extending or correcting an existing entry, or adding a backfill entry for a previously-merged PR) does **not** require its own new self-log entry. Such a PR may extend the *existing* entry's `Review Rounds` and `Self-Application Proof` sections instead. This exception breaks the recursion that would otherwise require every log-edit PR to log itself.
- **Generated artefact regeneration**: `docs/assets/architecture/*.svg` regenerated via `make diagrams` after a `docs/ai/shared/architecture-diagrams.md` source edit. The source edit itself triggers; the regenerated SVGs do not double-trigger.
- **`.gitignore`d entries**: `.claude/settings.local.json` and similar — never in PR diffs by definition.

## Identification Rules

A reviewer or hook decides "is this PR governor-changing?" by:

1. Compute `changed_files = git diff --name-only main..HEAD` (or the PR diff equivalent).
2. For each path in `changed_files`, test against every Tier A / B / C glob.
3. Apply Exclusions in order; if any rule applies and matches the entire change set, the PR is **not** governor-changing.
4. Otherwise, if at least one Tier A / B / C glob matches, the PR **is** governor-changing.

## Required artefacts when governor-changing

When the rules above classify a PR as governor-changing, the PR must produce:

- A `docs/ai/shared/governor-review-log/pr-{NNN}-{slug}.md` entry **whose filename's `{NNN}` equals the PR number**. The entry must contain Summary, Review Rounds (each with explicit `Final Verdict`), Inherited Constraints (or a link to the prior PR's Inherited Constraints when the new PR carries them forward), and Self-Application Proof.
- The Governor-Changing PR section of `.github/pull_request_template.md` filled (not deleted).
- At least one round of cross-tool review captured (per `target-operating-model.md` §5 Cross-Tool Review Cadence).

## Where this file is consumed

| Consumer | Purpose |
|---|---|
| `AGENTS.md` § Default Coding Flow → Self-Review trigger | Mandatory cross-tool review condition |
| `AGENTS.md` § Default Coding Flow → Doc-only carve-out | Auto-escape exclusion |
| `docs/ai/shared/target-operating-model.md` §3 | Auto-escape carve-out |
| `docs/ai/shared/target-operating-model.md` §5 Cross-Tool Review Cadence | Trigger detection |
| `docs/ai/shared/migration-strategy.md` Phase 4 acceptance | Hard reminder trigger |
| `docs/ai/shared/drift-checklist.md` §1D | Sync verification |
| `.github/pull_request_template.md` § Governor-Changing PR | Author self-classification |
| Phase 5 shared governor module | Programmatic detection |

If you add a new consumer, add the row above so the canonical surface stays visible.

## Updating this file

This file is itself governor-changing (Tier A, `docs/ai/shared/**`). Any edit must:

- Be reflected by all consumers above (verify their copies are still link-only, not duplicate-list).
- Add a `governor-review-log/` entry with Round 1 cross-tool review of the path-list change.
- Update `governor-review-log/README.md` Index table.

This recursion is intentional: a change to the canonical paths definition is a high-impact governor change.
