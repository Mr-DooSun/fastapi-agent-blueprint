---
name: plan-feature
argument-hint: feature description
description: |
  This skill should be used when the user asks to
  "plan feature", "design feature",
  or wants to plan and design a new feature before implementation.
---

# Feature Implementation Planning

Description: $ARGUMENTS

## Preparation

1. Use `.claude/rules/architecture-conventions.md` (auto-loaded); re-read only if the file is not visible in the current context.
2. Use `.claude/rules/project-status.md` (auto-loaded); re-read only if the file is not visible in the current context.
3. Use `.claude/rules/project-overview.md` (auto-loaded); re-read only if the file is not visible in the current context.
4. Identify current domain list: use Glob pattern `src/*/` and exclude `_core`, `_apps` prefixes

## Default Flow Position
See [target-operating-model §1](../../../docs/ai/shared/target-operating-model.md) — `plan-feature` routing.
Recursion guard: Do not invoke this skill recursively; implementation skills must not re-enter planning (ADR 050 scope expansion is separate).

## Procedure Overview
1. Requirements Interview — 3-5 questions from 5 categories (Phase 0)
2. Approach Options — propose 2-3 candidates with trade-offs, recommend one (Phase 1)
3. Architecture Impact Analysis — layer, domain, DTO, cross-domain (Phase 2)
4. Security Checkpoint — 6-item assessment matrix (Phase 3)
5. Task Breakdown — skill mapping, supervision levels, execution order (Phase 4)
6. Execution Packet — include Goal, Scope, Success Criteria, Selected Approach,
   Architecture Impact, Task List, Verification Gates, and Review Gates.
7. Work-ledger update — after task breakdown is confirmed, record goal/scope/plan to
   `.agents/state/current-work.json` via:
   ```python
   from work_ledger import update_goal_scope_plan, update_workflow_state
   update_goal_scope_plan(goal="<one-line goal>", scope="<domains/files>", plan="<task list>", updated_by="skill:plan-feature")
   update_workflow_state(stage="planned", plan_ref="<issue, PR, or plan file>", tasks=[{"id": "1", "title": "<task>", "status": "pending"}], updated_by="skill:plan-feature")
   ```

Read `docs/ai/shared/skills/plan-feature.md` for detailed steps and output format.
Also refer to `docs/ai/shared/planning-checklists.md` for question bank and templates.
For complex, architecture-changing, governor-changing, or multi-task work, hand
the approved Execution Packet to `/execute-plan` **as a separate step** — do not
implement within `/plan-feature`. Stopping at the packet is mandatory (ADR 054).
