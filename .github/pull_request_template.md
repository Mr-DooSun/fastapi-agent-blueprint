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

This section is **required** if your PR touches any of:
`AGENTS.md`, `docs/ai/shared/**`, `docs/history/**`, `.claude/**`, `.codex/**`, `.agents/**`, `.github/pull_request_template.md`, or other repo-level governance artifacts.
Otherwise delete the entire section.

Source of truth: [`AGENTS.md` § Default Coding Flow](../AGENTS.md#default-coding-flow) + [`docs/ai/shared/governor-review-log/README.md`](../docs/ai/shared/governor-review-log/README.md).

### Triggered files

- [ ] At least one file under the trigger glob list above is changed.

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

- [ ] If this PR is doc-only, confirm the changes do **not** touch policy / harness docs (`AGENTS.md`, `docs/ai/shared/**`, `docs/history/**`, `.claude/rules/**`, `.codex/rules/**`). Touching those files disqualifies the doc-only auto-escape — see [`target-operating-model.md` §3](../docs/ai/shared/target-operating-model.md).

### Phase context (Phase 2~5 of #117 only)

- [ ] PR description links the relevant section of [`migration-strategy.md` §1](../docs/ai/shared/migration-strategy.md).
- [ ] Inherited Constraints (IC-1 ~ IC-9 in [`governor-review-log/pr-125-...`](../docs/ai/shared/governor-review-log/pr-125-hybrid-harness-target-architecture.md)) reviewed; any phase-specific tightening recorded in this PR's log entry.
