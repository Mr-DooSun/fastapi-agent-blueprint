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

1. Read `.claude/rules/architecture-conventions.md` -- confirm current DO/DON'T rules
2. Read `.claude/rules/project-status.md` -- confirm work currently in progress
3. Read `.claude/rules/project-overview.md` -- confirm tech stack and structure
4. Identify current domain list: use Glob pattern `src/*/` and exclude `_core`, `_apps` prefixes

## Procedure Overview
1. Requirements Interview — 3-5 questions from 5 categories (Phase 0)
2. Approach Options — propose 2-3 candidates with trade-offs, recommend one (Phase 1)
3. Architecture Impact Analysis — layer, domain, DTO, cross-domain (Phase 2)
4. Security Checkpoint — 6-item assessment matrix (Phase 3)
5. Task Breakdown — skill mapping, supervision levels, execution order (Phase 4)

Read `docs/ai/shared/skills/plan-feature.md` for detailed steps and output format.
Also refer to `docs/ai/shared/planning-checklists.md` for question bank and templates.
