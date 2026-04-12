---
name: plan-feature
description: Plan a feature before implementation by collecting requirements, mapping layer impact, checking security implications, and breaking the work into executable tasks.
metadata:
  short-description: Feature planning workflow
---

# Plan Feature

1. Read `AGENTS.md`, `docs/ai/shared/repo-facts.md`, `docs/ai/shared/project-dna.md`, and `docs/ai/shared/planning-checklists.md`.
2. Identify impacted domains by scanning `src/*/` and excluding `_core`, `_apps`.
3. Run a short requirements interview using the question bank from `planning-checklists.md`.
4. Decide, per layer, whether the feature needs:
   - new DTO, Service, Protocol, or Exception
   - optional UseCase
   - Repository or model change
   - Router, Request/Response, Worker, or Admin additions
5. Apply the Write DTO criteria from `AGENTS.md`.
6. Fill the security matrix from `planning-checklists.md`; stop for confirmation if security-sensitive items apply.
7. Break work into tasks and map each task to an existing skill where possible.
8. Produce an implementation plan with requirements, architecture impact, security, execution order, and verification steps.
