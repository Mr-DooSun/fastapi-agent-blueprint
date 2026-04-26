# Guideline Synchronization Quality Gate

## Default Flow Position

This skill participates in the [Default Coding Flow](../../../../AGENTS.md#default-coding-flow) at the **`completion gate`** step (or as a follow-up to `self-review` when drift is detected).

It is invoked when any of:
- A `self-review` skill (`/review-architecture`, `/security-review`, `/review-pr`) reported `Drift Candidates` or `Sync Required: true`.
- The change touched shared rule sources (`AGENTS.md`, `docs/ai/shared/`, `.claude/rules/`, `.codex/rules/`, ADRs).
- An ADR was created or amended in the session.

Recursion guard: do **not** invoke `/sync-guidelines` recursively from within itself, and do not invoke `/plan-feature` from inside this skill. This skill is the closure step of the flow; it does not re-enter the flow.

Use this skill to close the documentation and workflow side of the quality gate
after architecture, security, or workflow changes.

## Operating Modes

`/sync-guidelines` supports two modes:

- standalone inspection mode - discover drift directly from the repo state
- review follow-up mode - consume incoming drift candidates from
  `/review-pr`, `/review-architecture`, or `/security-review`, then verify and
  close them

## Input Contract

If a previous review already produced `Drift Candidates`, consume them first.
Each candidate should preserve:

- `target`
- `reason`
- `auto-fix`
- `sync-required`

If no candidates are provided, derive them from the repo diff and code/reference
inspection.

## Gate Triggers

Treat sync as required when at least one of the following changed or drifted:

- `AGENTS.md`
- `docs/ai/shared/`
- `docs/ai/shared/project-dna.md`
- shared checklists
- shared skill procedures or tool wrappers
- harness docs (`CLAUDE.md`, `.claude/rules/`, `.codex/`)
- base classes, shared architecture wiring, or other documented reference
  patterns

## Sync Contract

The result is not complete until it includes all of:

- `Mode` - standalone or review follow-up
- `Input Drift Candidates` - consumed list, or `none`
- `project-dna` - updated or unchanged
- `AUTO-FIX` - applied mechanical fixes, or `none`
- `REVIEW` - policy or judgment items that still require human review, or `none`
- `Remaining` - unresolved drift that still exists, or `none`
- `Next Actions` - follow-up expected from the caller

If any `REVIEW` item exists, do not close with "nothing to change" or similar
language.

## Phase 0: Intake and Reference Scan

1. Determine the operating mode.
2. Collect incoming `Drift Candidates` if they already exist.
3. Read the reference domain (`src/user/`) and shared/base modules to anchor the
   current implementation shape.
4. Load the governing sources:
   - `AGENTS.md`
   - `docs/ai/shared/project-dna.md`
   - `docs/ai/shared/drift-checklist.md`
   - the affected shared procedures, checklists, wrappers, and harness docs

## Phase 1: Reconcile Drift Candidates with Code and References

Process incoming drift first.

- verify whether each candidate is still real
- promote still-valid candidates into `AUTO-FIX` or `REVIEW`
- mark resolved candidates as closed instead of re-reporting them blindly

If no incoming candidates exist, run the full drift inspection from
`docs/ai/shared/drift-checklist.md`.

## Phase 2: Refresh `project-dna` and Shared References

Update or confirm `project-dna` based on actual code.

- regenerate when drift exists or the caller explicitly requests it
- re-check shared references that depend on `project-dna`
- keep mechanical updates separate from policy-review updates

When a shared reference depends on product or policy judgment, report it under
`REVIEW` even if the code facts are clear.

## Phase 3: Verify Hybrid C and Close the Gate

Before closing:

- verify shared procedure existence for migrated skills
- verify both Claude and Codex wrappers reference the same shared procedure
- verify both wrappers keep the same Phase/Step overview count as the shared
  procedure
- verify shared procedures do not contain tool-specific instructions

Emit the full sync contract and clearly state whether the quality gate is closed
or waiting on review follow-up.

## Quality Gate Scenarios

Use these scenarios as regression examples for the workflow.

1. Architecture-changing PR
   - `/review-pr` should produce code findings and/or drift candidates
   - `/sync-guidelines` should refresh references before the gate closes
2. Security feature activation not reflected in `project-dna`
   - `/security-review` should not end in `SKIP`
   - it should raise a stale-reference drift candidate and require sync
3. Shared procedure changed but wrapper did not
   - `/sync-guidelines` should detect Hybrid C drift for both Claude and Codex
     wrappers
4. Docs-only change that alters checklist meaning
   - `/sync-guidelines` should classify it under `REVIEW`, not a silent auto-fix

## Completion Example

```text
Mode: review follow-up
Input Drift Candidates: 2 consumed
project-dna: updated (feature status refreshed)
AUTO-FIX: 2 items applied (planning-checklists, skill wrappers)
REVIEW: 1 item (security checklist wording changed and needs human approval)
Remaining: none
Next Actions: rerun the originating review or acknowledge the open review item
```
