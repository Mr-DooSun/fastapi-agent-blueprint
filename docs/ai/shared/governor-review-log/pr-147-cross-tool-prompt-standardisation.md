# PR #147 - Cross-Tool Prompt Template Standardisation

> Issue: [#144](https://github.com/Mr-DooSun/fastapi-agent-blueprint/issues/144)
> Pull Request: [#147](https://github.com/Mr-DooSun/fastapi-agent-blueprint/pull/147)
> ADR: ADR 045 and PR #143 Reasoning-Level Consistency Guards

## Summary

Adds canonical cross-tool review prompt templates to the four quality-gate
shared skill procedures: `/review-pr`, `/sync-guidelines`, `/security-review`,
and `/review-architecture`. The templates standardise the input and output
frame for read-only cross-tool reviews, including the original user question,
success metric, sources loaded, review angles, R-points, final verdict, and
the three canonical closure categories from AGENTS.md guard G:
`Fixed`, `Deferred-with-rationale`, and `Rejected`.

The canonical prompt bodies live only in `docs/ai/shared/skills/*.md`.
Claude and Codex wrapper skills were updated with pointer-only references so
the prompt body is not duplicated across tool-specific surfaces. The
governor-review-log README now links quality-gate reviewers to the per-skill
specialisations.

## Review Rounds

### Round 0 - Plan Review Attempt

- **Target**: issue #144 implementation plan, with Option A selected.
- **Reviewer**: Claude Opus 4.7 through Claude Code CLI.
- **Prompt focus**: canonical-source placement, inherited constraints
  IC-RG-1 through IC-RG-5, false-positive risk, wrapper drift risk, and scope
  separation from issues #145 and #146.
- **Result**: not executed. Claude Code returned
  `Not logged in - Please run /login`.
- **Final Verdict**: deferred with rationale. The implementation proceeded
  after local verification because the blocker was authentication state, not a
  finding against the plan.

### Round 1 - Implementation Review Attempt

- **Target**: local diff after adding the four shared prompt templates,
  wrapper pointers, and governor-review-log README cross-reference.
- **Reviewer**: Claude Opus 4.7 through Claude Code CLI.
- **Prompt focus**: canonical-source placement, exact closure category
  vocabulary, original user question and success metric slots, wrapper
  pointer-only behavior, and Tier 1 English-only policy.
- **Result**: not executed. Claude Code returned
  `Not logged in - Please run /login`.
- **Final Verdict**: deferred with rationale. The blocker must be closed by
  re-running Claude cross-review after login before this draft PR is marked
  ready for merge.

### Local Verification

- `python3 tools/check_language_policy.py` passed with 0 violations.
- `uv run pre-commit run --all-files` passed.
- `git diff --check` passed.
- Grep checks confirmed one `Cross-Tool Review Prompt Template` section in
  each of the four target shared skill procedures.
- Grep checks confirmed `original user question`, `success metric`, and the
  canonical `Fixed, Deferred-with-rationale, or Rejected` closure vocabulary
  in all four templates.

## Inherited Constraints

- **IC-RG-1** - Canonical body stays in shared sources. This PR places prompt
  bodies in `docs/ai/shared/skills/*.md`; wrappers only point to them.
- **IC-RG-2** - New review prompt slots are evidence-sourced from PR #143's
  documented miss patterns: stale facts, closure drift, effect/process drift,
  and self-review bias.
- **IC-RG-3** - Trigger remains narrow. Only the four quality-gate skills gain
  prompt specialisations.
- **IC-RG-4** - Closure vocabulary remains exactly `Fixed`,
  `Deferred-with-rationale`, and `Rejected`.
- **IC-RG-5** - This PR adds text prompt templates only. Mechanical closure
  linting remains issue #145.

No new inherited constraint is introduced by this PR.

## Self-Application Proof

- **Canonical-source check**: shared prompt bodies are present only in the four
  target files under `docs/ai/shared/skills/`.
- **Wrapper check**: `.claude/skills/**/SKILL.md` and
  `.agents/skills/**/SKILL.md` contain pointer-only references to the shared
  template sections.
- **Scope check**: no linter, parser, retrospective audit script, or legacy
  review-log backfill from issues #145 or #146 is included.
- **Language-policy check**: Tier 1 language policy passes with 0 violations.
- **Cross-tool limitation**: Claude Opus review is still required before merge
  readiness because both attempted Claude rounds were blocked by local
  authentication state.

## R-points Closure Table

| Source | R-point | Closure | Note |
|---|---|---|---|
| Round 0 | Claude plan review unavailable | **Deferred-with-rationale** | Claude Code was not logged in; rerun after login before marking the PR ready |
| Round 1 | Claude implementation review unavailable | **Deferred-with-rationale** | Same authentication blocker; not a plan or diff finding |
| Local verification | Tier 1 language policy | **Fixed** | `python3 tools/check_language_policy.py` and pre-commit language hook passed |
| Local verification | Required prompt slots present | **Fixed** | Four templates include original question, success metric, sources, R-points, final verdict, and closure vocabulary |
| Scope control | Issue #145 and #146 work not implemented | **Fixed** | This PR only adds text prompt templates and wrapper pointers |
