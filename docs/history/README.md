# Architecture Decision History

This document records the rationale behind technology stack choices for this project.
Each document captures the context and decision criteria for "why this technology was chosen."

## Table of Contents

| # | Title | Status | Written | Date |
|---|-------|--------|---------|------|
| [000](000-rabbitmq-to-celery.md) | Migration from RabbitMQ to Celery | Superseded by 001 | Done | 2025-09-10 |
| [001](001-celery-to-taskiq.md) | Migration from Celery to Taskiq | Accepted | Done | 2025-12-24 |
| [002](002-serena-adoption.md) | Serena MCP Server Adoption and Claude Code Parallel Strategy | Superseded by 030 | Done | 2026-03-18 |
| [003](003-response-request-pattern.md) | Response/Request Pattern Design | Accepted | Done | 2025-03 ~ 2025-09 |
| [004](004-dto-entity-responsibility.md) | DTO/Entity Responsibility Redefinition | Accepted | Done | 2025-07-15 |
| [005](005-poetry-to-uv.md) | Migration from Poetry to uv | Accepted | Done | 2025-04 |
| [006](006-ddd-layered-architecture.md) | Migration to Per-Domain Layered Architecture | Accepted | Done | 2025-07 ~ 2025-08 |
| [007](007-di-container-and-app-separation.md) | DI Container Layering and Per-Interface App Separation | Accepted | Done | 2025-09 ~ 2025-11 |
| [008](008-deploy-env-separation.md) | Deployment Environment Separation and Configuration Management | Accepted | Done | 2025-09 |
| [009](009-async-external-clients.md) | Async External Client Standardization | Accepted | Done | 2025-10 |
| [010](010-code-quality-tools.md) | Code Quality Tooling Systematization | Superseded by 012 | Done | 2025-10 |
| [011](011-3tier-hybrid-architecture.md) | Migration to 3-Tier Hybrid Architecture | Accepted | Done | 2026-03-23 |
| [012](012-ruff-migration.md) | pre-commit Linting Tool Ruff Integration | Accepted | Done | 2026-03-23 |
| [013](013-why-ioc-container.md) | Why IoC Container Over Inheritance | Accepted | Done | 2026-03-23 |
| [014](014-omc-vs-native-orchestration.md) | OMC vs Native Orchestration Decision | Accepted | Done | 2026-03-24 ~ 2026-04-05 |
| [015](015-rebrand-agent-platform.md) | Rebrand to AI Agent Backend Platform | Accepted | Done | 2026-04-03 |
| [016](016-worker-payload-schema.md) | Worker Payload Schema | Accepted | Done | 2026-04-06 |
| [017](017-exception-handling-strategy.md) | Exception Handling Strategy: Native Handler over Middleware | Accepted | Done | 2025-09 ~ 2026-03 |
| [018](018-domain-event-removal.md) | Domain Event Infrastructure Removal | Accepted | Done | 2026-04-02 |
| [019](019-domain-auto-discovery.md) | Domain Auto-Discovery System | Accepted | Done | 2026-03 |
| [020](020-aidd-skills-governance.md) | AIDD Methodology and Skills Governance System | Accepted | Done | 2026-03 |
| [021](021-architecture-governance-hooks-ci.md) | Architecture Governance via Pre-commit Hooks and CI | Accepted | Done | 2026-03 ~ 2026-04 |
| [022](022-underscore-prefix-convention.md) | Underscore Prefix Convention for Internal Modules | Accepted | Done | 2025-10 ~ 2025-11 |
| [023](023-object-storage-unification.md) | Object Storage Unification: MinIO to S3 via aioboto3 | Accepted | Done | 2025-10 |
| [024](024-session-lifecycle-management.md) | Session Lifecycle Management: Context Manager over Factory | Accepted | Done | 2025-08 ~ 2025-10 |
| [025](025-oss-preparation-strategy.md) | OSS Preparation and Internationalization Strategy | Accepted | Done | 2026-03 ~ 2026-04 |
| [026](026-nicegui-admin-dashboard.md) | NiceGUI Adoption for Admin Dashboard | Accepted | Done | 2026-04-08 |
| [027](027-flexible-rdb-configuration.md) | Flexible RDB Configuration with Multi-Engine Support | Accepted | Done | 2026-04-08 |
| [028](028-environment-config-validation.md) | Environment-Aware Configuration Validation | Accepted | Done | 2026-04-08 |
| [029](029-broker-abstraction-selector.md) | Broker Abstraction with providers.Selector for Multi-Backend Selection | Accepted | Done | 2026-04-09 |
| [030](030-serena-removal-pyright-rules.md) | Serena Removal: Migration to pyright-lsp and .claude/rules/ | Accepted | Done | 2026-04-11 |

## Future Considerations (Open Issues)

| Issue | Title | Label |
|-------|-------|-------|
| #8 | Add WebSocket router documentation library | enhancement |
| #11 | Add pytest | enhancement |
| #12 | Add locust | enhancement |
| #13 | Add auth functionality | enhancement |
| #18 | Database health check | enhancement |
| #28 | Add serverless | enhancement |
| #29 | Per-environment DB separation | enhancement, refactor |
| #31 | Per-message-broker environment separation | enhancement, refactor |
| #32 | Logging | enhancement |
| #35 | Add data CRUD validation | - |
| #36 | Add vector DB | enhancement |
| #45 | Add Vercel | enhancement |
| #46 | Improve ADR template for clearer intent communication | enhancement |
| #14 | Implement admin dashboard with NiceGUI | enhancement |
| #51 | Adopt PydanticAI | enhancement |
| #52 | Per-environment Alembic separation | refactor |
| #55 | Slack/Discord alerts on error | enhancement |

## Writing Guide

### Writing Principles

An ADR is **not** a document that justifies a decision already made.
It is a record of the **decision-making process** — the problem, the options, and why one was chosen.

**Anti-patterns (rationalization):**
- Starting from the conclusion and gathering evidence to support it
- "We chose X. Here's why X is good..." (conclusion → evidence)
- Omitting alternatives that were seriously considered
- Writing rationale that only lists benefits without trade-offs

**Correct approach (decision record):**
- "We faced problem Y. We considered A, B, C. Given our context, we chose X because..."
  (problem → process → conclusion)
- Being honest about the decision type: was this designed upfront, or corrected after experience?
- Acknowledging trade-offs and what was sacrificed

### Language

ADRs must be written in English.

### File Naming
```
{number}-{topic}.md
e.g.: 001-celery-to-taskiq.md
```

### Document Structure
```markdown
# {number}. {title}

- Status: Accepted / Deprecated / Superseded by {number}
- Date: YYYY-MM-DD
- Related issue: #{number}

## Summary
<!-- 1-2 sentences: "To solve {problem}, we chose {approach}" -->

## Background
<!-- Must include: -->
<!-- - Trigger: what made this decision necessary NOW -->
<!-- - Decision type: upfront design / experience-based correction / external factor -->

## Problem

## Alternatives Considered
<!-- For each alternative: why it does not fit the current project context -->
### A. {alternative}
### B. {alternative}

## Decision

## Rationale
<!-- Lead with architectural "why", not implementation details -->

### Self-check
- [ ] Does this decision address the root cause, not just the symptom?
- [ ] Is this the right approach for the current project scale and team situation?
- [ ] Will a reader understand "why" 6 months from now without additional context?
- [ ] Am I recording the decision process, or justifying a conclusion I already reached?
```

### Status Values
- **Accepted** — Currently in effect
- **Deprecated** — No longer valid
- **Superseded by XXX** — Replaced by another decision
