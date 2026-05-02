## Related Issue
- Fixes #
- Closes #

## Change Summary
-

## Type of Change
- [ ] feat: New feature
- [ ] fix: Bug fix
- [ ] refactor: Code restructuring
- [ ] docs: Documentation
- [ ] chore: Build/tooling
- [ ] test: Tests
- [ ] ci: CI/CD
- [ ] perf: Performance
- [ ] style: Code style

## Checklist
- [ ] Architecture rules followed (no Domain -> Infrastructure imports)
- [ ] Tests pass
- [ ] Linting passes (`ruff check src/`)

## How to Test
-

---

## Governor-Changing PR (delete this section if not applicable)

This section is **required** if your PR is *governor-changing* per [`docs/ai/shared/governor-paths.md`](../docs/ai/shared/governor-paths.md) (Tier A / B / C minus exclusions).
Otherwise delete the entire section.

Source of truth: [`AGENTS.md` § Default Coding Flow](../AGENTS.md#default-coding-flow) + [`docs/ai/shared/governor-paths.md`](../docs/ai/shared/governor-paths.md) + [`docs/ai/shared/governor-review-log/README.md`](../docs/ai/shared/governor-review-log/README.md).

### Triggered files

- [ ] At least one file in `changed_files` matches a Tier A / B / C path in `governor-paths.md`, and no full-set exclusion applies.

### Cross-tool review

- [ ] Codex `gpt-5.5 --sandbox read-only` review completed at least once (plan stage and/or implementation stage).
- [ ] All R-points addressed or explicitly deferred with rationale.
- [ ] Final Verdict captured (`merge-ready` / `minor fixes recommended` / `block merge`).

### Self-application proof

- [ ] `/review-architecture` (or its manual equivalent) output captured for the changed surface — `Findings` / `Drift Candidates` / `Sync Required`.
- [ ] `/sync-guidelines` (or its manual equivalent) output captured — `AUTO-FIX` / `REVIEW` / `Remaining`.

### Review trail artifact

- [ ] `docs/ai/shared/governor-review-log/pr-{NNN}-{slug}.md` added (or existing entry extended) with: Summary, Review Rounds, Inherited Constraints, Self-Application Proof.
- [ ] `governor-review-log/README.md` Index table updated.
- [ ] If this PR creates follow-up issues, each follow-up issue body links the new log entry under "Inherited Review Constraints".

### Doc-only escape hygiene

- [ ] If this PR is doc-only, confirm the changes do **not** touch policy / harness docs as listed in [`governor-paths.md`](../docs/ai/shared/governor-paths.md) Tier A. Touching those files disqualifies the doc-only auto-escape — see [`target-operating-model.md` §3](../docs/ai/shared/target-operating-model.md).

### Phase context (Phase 2~5 of #117 only)

- [ ] PR description links the relevant section of [`migration-strategy.md` §1](../docs/ai/shared/migration-strategy.md).
- [ ] Inherited Constraints (IC-1 ~ IC-9 in [`governor-review-log/pr-125-...`](../docs/ai/shared/governor-review-log/pr-125-hybrid-harness-target-architecture.md)) reviewed; any phase-specific tightening recorded in this PR's log entry.

---

## Governor Footer (pilot — ADR 047)

Required from PR B onward; documentation-only on PR A. From PR E onward this footer **replaces** the "Review trail artifact" checkboxes above; until PR E lands, it is dual-write alongside the existing log-entry workflow. See [ADR 047](../docs/history/047-governor-review-provenance-consolidation.md) for the migration plan.

Fill the block below verbatim and replace the placeholder values. Lint shape: each field on its own line, exact field name, single space after the colon. The closure-category labels must be exactly `Fixed`, `Deferred-with-rationale`, or `Rejected` (Guard G).

```
## Governor Footer
- trigger: yes/no
- reviewer: codex-cli/claude-code/...
- rounds: N
- r-points-fixed: N
- r-points-deferred: N
- r-points-rejected: N
- touched-adr-consequences: ADR{NNN}-G{N}, ADR{NNN}-G{N} / none
- pr-scope-notes: <one-line summary or "none">
- final-verdict: merge-ready/minor-fixes/needs-reinforcement/block
- links: <PR url>, <prior-log url or "n/a">
```

Field guidance:

- `trigger` — `yes` if `changed_files` matches any Tier A/B/C glob in [`governor-paths.md`](../docs/ai/shared/governor-paths.md) and no full-set Exclusion applies; otherwise `no` (and you may delete this footer).
- `reviewer` — the cross-tool reviewer that read the change. Multiple reviewers comma-separated.
- `rounds` — total cross-tool review rounds run on this PR (plan stage + implementation stage counts as 2).
- `r-points-fixed/deferred/rejected` — closure counts using exactly the three Guard G categories.
- `touched-adr-consequences` — list `ADR{NNN}-G{N}` slot IDs (the canonical form used by ADR 047 IC Classification Table; e.g. `ADR047-G3`, `ADR048-G1`) this PR amends; `none` if no durable-governance constraint changed. Comma-separated.
- `pr-scope-notes` — short prose for `pr-scope` invariants this PR self-imposes (e.g. "minimal RBAC scope; permission tables follow-up"). They are **not** promoted to ADR Consequences.
- `final-verdict` — last cross-tool review verdict.
- `links` — PR URL plus, while dual-write is in effect, the matching `governor-review-log/pr-{N}-*.md` entry URL.
