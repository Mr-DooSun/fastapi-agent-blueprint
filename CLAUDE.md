# FastAPI Layered Architecture — Claude Work Guide

## Project Scale
This project targets enterprise-grade services with 10+ domains and 5+ team members.
All proposals and designs must consider scalability, maintainability, and team collaboration at this scale.

## Pre-work Checklist
1. Check current Phase via Serena `refactoring_status` memory
2. Check DO/DON'T via Serena `architecture_conventions` memory

## Absolute Prohibitions
- No Infrastructure imports from the Domain layer
- No exposing Model objects outside the Repository
- No separate Mapper classes (inline conversion is sufficient)
- No Entity pattern — unified to DTO (background: [ADR 004](docs/history/004-dto-entity-responsibility.md))
- No modifying/deleting CLAUDE.md or project-dna.md rules without cross-reference verification
  (Run: `grep -rl "KEYWORD" .claude/skills/` to check skill dependencies before any change)

## Layer Architecture (3-Tier Hybrid)
- Default: Router → Service (extends BaseService) → Repository (extends BaseRepository)
- Complex logic: Router → UseCase (manually written) → Service → Repository
- UseCase criteria: multiple Service composition, cross-transaction boundaries, etc.
- When in doubt: start without UseCase, add when complexity grows

## Terminology
- **Request/Response**: API communication schema (`interface/server/schemas/`)
- **DTO**: Internal data carrier between layers — Repository→Router (`domain/dtos/`)
- **Model**: DB table mapping, never exposed outside Repository (`infrastructure/database/models/`)

## Claude Collaboration Rules
- If diagnosis/review result is "adequate", do not force improvement suggestions
- Before proposing changes to project rules or structure:
  1. Grep `.claude/skills/` for keywords from the rule being changed
  2. If any skill references the rule, it is project-level — do not relocate or weaken
- Only propose modifying/deleting existing structures when benefits of the new structure are clear
- Skill SKILL.md frontmatter supported attributes: name, argument-hint, description, disable-model-invocation, compatibility (allowed-tools not supported)
- **Update related documentation when changing code** — before committing, check:
  1. Skills SKILL.md and references/ that reference the changed patterns
  2. Relevant sections of project-dna.md
  3. Serena memories (architecture_conventions, etc.)
  4. When delegating to agents, explicitly pass the list of changed files

## Security Principles
- Do not expose internal details (traceback, DB schema, query) in production error responses
- Prevent OWASP Top 10 violations when writing code (detailed checklist: `/security-review`)

## Conversion Patterns
### Write Direction (Request → DB)
- Router → Service: `entity=item` (pass Request directly)
- Service → Repository: pass entity as-is
- Repository → DB: `Model(**entity.model_dump(exclude_none=True))`

### Read Direction (DB → Response)
- DB → Repository: `DTO.model_validate(model, from_attributes=True)`
- Repository → Service → Router: pass DTO as-is
- Router → Client: `Response(**dto.model_dump(exclude={'password'}))`

## Write DTO Creation Criteria
- When fields match Request: pass Request directly, no separate Create/Update DTO needed
- When fields differ (auth context injection, derived fields, etc.): create separate DTO in `domain/dtos/`
  - Example: `CreateUserDTO(**item.model_dump(), created_by=current_user.id)`

## Skills (slash commands)
- `/plan-feature {description}` — Feature implementation planning (requirements interview → architecture analysis → security check → task decomposition)
- `/new-domain {name}` — Full domain scaffolding (14 content + 22 `__init__.py` + 3 tests = 39 files)
- `/add-api {description}` — Add API endpoint to existing domain
- `/add-worker-task {domain} {task}` — Add async Taskiq task
- `/add-cross-domain from:{a} to:{b}` — Wire cross-domain dependency
- `/review-architecture {domain|all}` — Architecture compliance audit
- `/security-review {domain|file|all}` — OWASP-based code security audit
- `/test-domain {domain} [generate|run]` — Generate or run tests
- `/fix-bug {description}` — Structured bug-fix workflow
- `/create-pr` — PR creation (branch validation → commit analysis → template-based PR)
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

> Serena and context7 are project-required MCP servers (configured via `.mcp.json`).

### Code Exploration / Reading (by priority)
1. **Serena symbol tools** (default): `get_symbols_overview` → `find_symbol(include_body=True)`
   - Understand file structure, read specific methods, navigate class hierarchy
   - Token-efficient, essential for large codebases
2. **Grep/Glob** (auxiliary): locate files, search string patterns, explore config files
3. **Read** (last resort): non-code files, config files, or when symbol exploration is insufficient

### Impact Analysis
- For refactoring/signature changes: prioritize Serena `find_referencing_symbols`
- For simple string search: Grep

### Editing
- Full symbol replacement (methods, classes): Serena `replace_symbol_body`
- Partial modification (few lines): Claude Code `Edit`
- New code insertion: Serena `insert_before/after_symbol` or `Edit`

### Routine Tasks
- Domain creation/API addition/tests/etc.: Skills (`/new-domain`, `/add-api`, etc.)

### Library Documentation
- **Proactively** use context7 whenever looking up library/framework/tool docs — do not wait for user to request it
- Applies to: API syntax, configuration, version migration, conventions (SQLAlchemy 2.0, Pydantic 2.x, Taskiq, Conventional Commits, etc.)
