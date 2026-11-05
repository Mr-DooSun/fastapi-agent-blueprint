# 059. Harness Context Byte Budgets

- Status: Accepted
- Date: 2026-11-06
- Related issues: #413, #414, #415, #416, #417

## Summary

Bound automatic session context with a blocking, index-selected byte checker.
Dates record content changes; they do not create periodic documentation work.

## Background

The #414 audit found that line-count and table-row-count limits allowed growth
inside individual lines. Long sync headers had become retrospective archives,
and AGENTS.md exceeded Codex's default project-document allowance (#413).
Shrinking those files once cannot prevent the same growth from recurring.

## Alternatives Considered

### A. Keep freshness dates and a manual line-count target

Rejected: neither measures the bytes injected into a session. Updating dates
for unchanged files also creates conflicts and gives histories another home.

### B. Delete governance hooks and shared architecture rules

Rejected: the audit did not establish equivalent replacements for those
responsibilities. Context savings do not justify removing product guarantees.

### C. Check bytes, keep policy, archive historical narrative once

Selected: sizes are deterministic facts. A full-index scan catches growth even
when the triggering change did not edit the file that consumes the budget.

## Decision

`tools/check_context_budget.py` is a blocking pre-commit check. It reads the
working-tree contents of index-selected files; untracked local files cannot
change the scan. It checks:

- The total bytes of CLAUDE.md and rules without nonempty `paths` frontmatter.
- Each rules file's full size, including scoped rules and fenced examples.
- Short sync headers (Last synced or Last updated) and whole Markdown rows,
  including pipes and links, inside the Recent Major Changes table.
- An absolute AGENTS.md budget below the default Codex document allowance.

Numeric limits live in the checker and its hook-registration comment only.
Fenced examples are excluded from line checks but still consume file/total
bytes. General shared-document prose and tables are outside line-cap scope;
their migration requires a later, measured ratchet rather than retroactive
failures across unrelated documents.

A rules file's sync date equals its most recent substantive content change.
Do not touch an unchanged file merely because its date is old. A sync header is
one short provenance line; detailed explanation belongs in CHANGELOG and the
PR body. Existing narrative is archived once with its source provenance.
Routine sync does not append to the historical archive, preserving ADR 047 D4.

The initial total and file ceilings leave headroom above the compacted tree.
At each quarterly review, measure the same tracked set, lower ceilings when
observed usage permits, and record before/after measurements in the PR.
Raising a ceiling is governor-changing: justify the need and include independent
review and a Governor Footer. Do not raise it to avoid moving a retrospective.

## Consequences

### Durable Governance Constraints

- **ADR059-G1**: Context-budget increases require governor-changing review.
  Preserve the index-selected scan, content-change dates, actionable
  `file:line` failures, and separate fenced-line vs full-file counting.

### Verification and fork policy

Run the checker, its unit tests, the language/link checks, and all pre-commit
hooks after synchronization. The closing sync output must itself fit the
limits; record that self-application measurement in the PR description.

Forks may use `SKIP=context-budget` for a deliberate local bypass. A bypass is
not a passing verification result and does not replace the review requirement
for changing this repository's policy. Existing safety, stage, locale and
review-provenance semantics are unchanged.
