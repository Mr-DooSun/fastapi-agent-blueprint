# Architecture Decision History

This document records the rationale behind technology stack choices for this project.
Each document captures the context and decision criteria for "why this technology was chosen."

## Table of Contents

| # | Title | Status | Written | Date |
|---|-------|--------|---------|------|
| [000](000-rabbitmq-to-celery.md) | Migration from RabbitMQ to Celery | Superseded by 001 | Done | 2025-09-10 |
| [001](001-celery-to-taskiq.md) | Migration from Celery to Taskiq | Accepted | Done | 2025-12-24 |
| [002](002-serena-adoption.md) | Serena MCP Server Adoption and Claude Code Parallel Strategy | Accepted | Done | 2026-03-18 |
| [003](003-response-request-pattern.md) | Response/Request Pattern Design | Accepted | Done | 2025-03~09 |
| [004](004-dto-entity-responsibility.md) | DTO/Entity Responsibility Redefinition | Accepted | Done | 2025-07 |
| [005](005-poetry-to-uv.md) | Migration from Poetry to uv | Accepted | Done | 2025-04 |
| [006](006-ddd-layered-architecture.md) | Migration to Per-Domain Layered Architecture | Accepted | Done | 2025-07~08 |
| [007](007-di-container-and-app-separation.md) | DI Container Layering and Per-Interface App Separation | Accepted | Done | 2025-09~11 |
| [008](008-deploy-env-separation.md) | Deployment Environment Separation and Configuration Management | Accepted | Done | 2025-09 |
| [009](009-async-external-clients.md) | Async External Client Standardization | Accepted | Done | 2025-10 |
| [010](010-code-quality-tools.md) | Code Quality Tooling Systematization | Superseded by 012 | Done | 2025-10 |
| [011](011-3tier-hybrid-architecture.md) | Migration to 3-Tier Hybrid Architecture | Accepted | Done | 2026-03-23 |
| [012](012-ruff-migration.md) | pre-commit Linting Tool Ruff Integration | Accepted | Done | 2026-03-23 |
| [013](013-why-ioc-container.md) | Why IoC Container Over Inheritance | Accepted | Done | 2026-03-23 |
| [014](014-omc-vs-native-orchestration.md) | OMC vs Native Orchestration Decision | Pending | In Progress | 2026-03-24 |
| [015](015-rebrand-agent-platform.md) | Rebrand to AI Agent Backend Platform | Accepted | Done | 2026-04-03 |

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
| #46 | Add DynamoDB | enhancement |
| #47 | Adopt Replex and build internal admin page | enhancement |
| #51 | Adopt PydanticAI | enhancement |
| #52 | Per-environment Alembic separation | refactor |
| #55 | Slack/Discord alerts on error | enhancement |

## Writing Guide

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

## Background
## Problem
## Alternatives Considered
## Decision
## Rationale
```

### Status Values
- **Accepted** — Currently in effect
- **Deprecated** — No longer valid
- **Superseded by XXX** — Replaced by another decision
