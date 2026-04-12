# FastAPI Agent Blueprint — Claude Harness Guide

Shared project rules live in [AGENTS.md](AGENTS.md).
This file intentionally keeps only Claude-specific setup and workflow guidance.

## Pre-work Checklist
1. Read shared project rules from `AGENTS.md` (not auto-loaded — read explicitly)
2. Read shared workflow references from `docs/ai/shared/` when the task needs deeper context (`project-dna.md`, checklists, onboarding tracks)
3. Check current project status via `.claude/rules/project-status.md` (auto-loaded)
4. Check DO/DON'T via `.claude/rules/architecture-conventions.md` (auto-loaded)

## Claude Collaboration Rules
- If diagnosis/review result is "adequate", do not force improvement suggestions
- Only propose modifying or deleting existing Claude-specific structures when the benefit is clear
- Skill `SKILL.md` frontmatter supported attributes: `name`, `argument-hint`, `description`, `disable-model-invocation`, `compatibility`
- Before changing shared rules or structure, follow the drift management rules in `AGENTS.md`
- Shared workflow references now live under `docs/ai/shared/`; Claude skills should point there instead of keeping private copies
- When delegating to agents, explicitly pass the list of changed files

## Skills (slash commands)
- `/plan-feature {description}` — Feature implementation planning (requirements interview → architecture analysis → security check → task decomposition)
- `/new-domain {name}` — Full domain scaffolding (15 content + 25 `__init__.py` + 4 tests = 44 files)
- `/add-api {description}` — Add API endpoint to existing domain
- `/add-worker-task {domain} {task}` — Add async Taskiq task
- `/add-admin-page {domain}` — Add NiceGUI admin page to existing domain
- `/add-cross-domain from:{a} to:{b}` — Wire cross-domain dependency
- `/review-architecture {domain|all}` — Architecture compliance audit
- `/security-review {domain|file|all}` — OWASP-based code security audit
- `/test-domain {domain} [generate|run]` — Generate or run tests
- `/fix-bug {description}` — Structured bug-fix workflow
- `/review-pr {number|URL}` — Architecture-aware PR review (existing rules applied to PR diff)
- `/sync-guidelines` — Synchronize guidelines after design changes + regenerate project-dna.md
- `/migrate-domain {generate|upgrade|downgrade|status}` — Alembic migration management
- `/onboard` — Interactive onboarding for new members (project structure → rules → workflow)

## Domain Auto-discovery
- `discover_domains()` in `src/_core/infrastructure/discovery.py` auto-detects domains
- Server/Worker App-level Containers use `DynamicContainer` + factory function
- **No need to modify `container.py` or `bootstrap.py` when adding a new domain** (auto-registered)
- Domain Containers themselves use `DeclarativeContainer`

## Tool Selection Guidelines

> Shared architecture rules, terminology, conversion patterns, and DTO criteria are defined in `AGENTS.md`.
> Shared workflow references live in `docs/ai/shared/`.
> Detailed shell commands are in `.claude/rules/commands.md` (auto-loaded); Makefile shortcuts are in `AGENTS.md`.
> context7 is a project-required MCP server for Claude (configured via `.mcp.json`).
> pyright-lsp plugin provides native LSP code intelligence.

### Code Exploration / Reading (by priority)
1. **pyright-lsp** (symbol navigation): goToDefinition, findReferences, documentSymbol, getDiagnostics
   - Most token-efficient for symbol definition, reference tracking, file structure
   - Required plugin — registered via `enabledPlugins` in settings.json
2. **Grep/Glob** (pattern search): string patterns, config files, non-code files
3. **Read** (full content): when full file content is needed

### Impact Analysis
- For refactoring/signature changes: pyright-lsp `findReferences`
- For simple string search: Grep

### Editing
- All edits: Claude Code `Edit` tool
- PostToolUse hook auto-formats `.py` files after edits (ruff format + check)

### Routine Tasks
- Domain creation/API addition/tests/etc.: Skills (`/new-domain`, `/add-api`, etc.)

### Library Documentation
- **Proactively** use context7 whenever looking up library/framework/tool docs — do not wait for user to request it
- Applies to: API syntax, configuration, version migration, conventions (SQLAlchemy 2.0, Pydantic 2.x, Taskiq, Conventional Commits, etc.)
