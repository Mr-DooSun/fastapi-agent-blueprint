---
name: onboard
argument-hint: "(no arguments)"
description: |
  This skill should be used when the user asks to
  "project introduction", "getting started",
  "how does this project work", "I'm new to this project",
  or is a new team member needing orientation to the project.
---

# Interactive Onboarding for New Team Members

## Default Flow Position
See [target-operating-model §1](../../../docs/ai/shared/target-operating-model.md) — `onboard` routing.
Recursion guard: Do not invoke this skill recursively or invoke plan-feature from inside it.

## Pre-check: Collect Project State

Execute the following to understand the current project state (do not output to the user):

1. Use `.claude/rules/project-overview.md` (auto-loaded); re-read only if the file is not visible in the current context.
2. Use `.claude/rules/project-status.md` (auto-loaded); re-read only if the file is not visible in the current context.
3. Use `.claude/rules/architecture-conventions.md` (auto-loaded); re-read only if the file is not visible in the current context.
4. Glob `src/*/` to identify current domain list (excluding `_core`, `_apps`)
5. `git log --oneline -5` to check recent activity

## Procedure Overview
1. Welcome — assess experience level and preferred format (Phase 0)
2. Methodology — architecture evolution history via ADRs (Phase 1)
3. Project Overview — structure, domains, tech stack (Phase 2)
4. Architecture Rules — Absolute Prohibitions and terminology (Phase 3)
5. Data Flow — conversion patterns with live code walkthrough (Phase 4)
6. Development Workflow — Skills and CLI commands (Phase 5)
7. Personalized Next Steps (Phase 6)

Read `docs/ai/shared/skills/onboard.md` for the full onboarding flow, including
Q&A/Explore mode rules, topic maps, and experience-level adjustments.

## Claude-Specific: Phase 2 and Phase 5 Sources
- Phase 2 tech stack: use `.claude/rules/project-overview.md` (auto-loaded); re-read only if the file is not visible in the current context.
- Phase 5 Skills list: use the native `.claude/skills/` index; include the two user-only skills named in `CLAUDE.md`.
- Phase 5 CLI commands: use `.claude/rules/commands.md` (auto-loaded); re-read only if the file is not visible in the current context.
- Phase 6 wrap-up: include `CLAUDE.md` as a key reference material
