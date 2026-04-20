# Contributing to FastAPI Agent Blueprint

Thank you for your interest in contributing! This guide will help you get started.

## Development Setup

> First time evaluating the project? Run `make quickstart` instead — it
> boots the server on SQLite with no external infrastructure. See
> [`docs/quickstart.md`](docs/quickstart.md). The setup below is for
> actual contribution work against PostgreSQL + migrations.

```bash
# Clone the repository
git clone https://github.com/Mr-DooSun/fastapi-agent-blueprint.git
cd fastapi-agent-blueprint

# Setup (installs dependencies + pre-commit hooks)
make setup

# Set up environment variables
cp _env/local.env.example _env/local.env

# Start PostgreSQL + run migrations + start server
make dev
```

<details>
<summary>Manual setup (without Make)</summary>

```bash
# Create virtual environment and install dependencies
uv venv --python 3.12
source .venv/bin/activate
uv sync --group dev

# Install pre-commit hooks
uv run pre-commit install
uv run pre-commit install --hook-type commit-msg

# Set up environment variables
cp _env/local.env.example _env/local.env

# Start PostgreSQL
docker compose -f docker-compose.local.yml up -d postgres

# Run migrations and start the server
uv run alembic upgrade head
uv run python run_server_local.py --env local
```
</details>

## AI Collaboration Entry Points

Start from [AGENTS.md](AGENTS.md), which is the canonical source for shared rules.

Tool-specific harness files:
- Claude: [CLAUDE.md](CLAUDE.md), [.mcp.json](.mcp.json), [.claude/settings.json](.claude/settings.json)
- Codex: [.codex/config.toml](.codex/config.toml), [.codex/hooks.json](.codex/hooks.json), [.agents/skills](.agents/skills)

Do not duplicate shared architecture rules into tool-specific docs. Update `AGENTS.md` first, then adjust the harness docs that reference it.
Shared workflow references that both tools consume live under [docs/ai/shared](docs/ai/shared).
When running `/sync-guidelines` or `$sync-guidelines`, do not stop at automatic doc edits. The final result must explicitly include `project-dna`, `AUTO-FIX`, `REVIEW`, and `Remaining`.

## Claude Minimum Setup

```bash
uv sync --group dev
claude plugin install pyright-lsp
```

Verification:
- Confirm `.claude/settings.json` enables `pyright-lsp`
- Confirm `.mcp.json` contains `context7`
- Run Claude in the repo and verify hooks/plugins load normally

## Codex Minimum Setup

1. Trust the project in Codex.
2. Confirm `.codex/config.toml` is present and committed.
3. Confirm `.codex/hooks.json` and `.agents/skills/` are present and committed.
4. Run the following from the repository root:

```bash
codex mcp list
codex mcp get context7
codex debug prompt-input -c 'project_doc_max_bytes=400' "healthcheck" | rg "Shared Collaboration Rules|AGENTS\\.md"
codex execpolicy check --rules .codex/rules/fastapi-agent-blueprint.rules git push origin main
```

Verification targets:
- `context7` appears in `codex mcp list`
- `codex mcp get context7` resolves the configured server
- `codex debug prompt-input` includes `AGENTS.md` content when the project is trusted
- `codex execpolicy check` returns a non-`allow` decision for protected commands

Operational notes:
- Web search stays off by default. Use `codex -p research` or `codex --search` only for live external research.
- Codex memories are personal/session-local optimization and are not part of repository governance.

### Codex Local Exception: `~/.codex/sessions` Permission Issue

If `codex debug prompt-input` fails with a sessions permission error, use a temporary `CODEX_HOME` plus a minimal trust bootstrap:

```bash
TMP_CODEX_HOME="$(mktemp -d /tmp/codex-home.XXXXXX)"
printf '[projects."%s"]\ntrust_level = "trusted"\n' "$PWD" > "$TMP_CODEX_HOME/config.toml"
CODEX_HOME="$TMP_CODEX_HOME" codex mcp list
CODEX_HOME="$TMP_CODEX_HOME" codex mcp get context7
CODEX_HOME="$TMP_CODEX_HOME" codex debug prompt-input \
  -c "projects.\"$PWD\".trust_level=\"trusted\"" \
  -c 'project_doc_max_bytes=400' \
  "healthcheck" | rg "Shared Collaboration Rules|AGENTS\\.md"
```

`CODEX_HOME` alone is not enough. Without the temporary `config.toml` trust entry, Codex will ignore the repo's `.codex/config.toml`.

### Codex `context7` Real-Use Check

Run one interactive Codex session in the trusted repo and explicitly ask it to use `context7`, for example:

```text
Use context7 to look up the latest FastAPI lifespan guidance and summarize the result.
```

Confirm that the session shows a `context7` MCP startup or tool call before treating Codex MCP setup as complete.

## Project Structure

See [README.md](README.md#project-structure) for the full project structure.

Each domain follows a consistent layout:

```
src/{domain}/
├── domain/           # Business logic, DTOs, Protocols, Services
├── infrastructure/   # Repository, Model, DI Container
├── interface/        # Router, Request/Response DTOs, Admin, Worker
└── application/      # UseCase (optional, for complex orchestration)
```

## Adding a New Domain

Use the built-in Claude Code skill:

```
/new-domain {name}
```

Or follow the [manual steps in the README](README.md#adding-a-new-domain).

## Running Tests

```bash
make test

# With coverage
make test-cov
```

## Code Quality

Pre-commit hooks run automatically on commit. To run manually:

```bash
make lint        # Check for issues
make format      # Auto-format
make pre-commit  # Run all pre-commit hooks
```

## Architecture Rules

Shared rules live in [AGENTS.md](AGENTS.md). These rules are additionally enforced by pre-commit hooks:

- **Domain layer cannot import from Infrastructure** -- dependency inversion via Protocol
- **Model objects never leave the Repository** -- convert to DTO using `model_validate()`
- **No separate Mapper classes** -- use inline conversion
- **No Entity pattern** -- use DTOs only (see [ADR 004](docs/history/004-dto-entity-responsibility.md))

## Note on Commit History

This project was migrated from a private repository. Issue numbers in early commit messages (e.g., `[#57]`, `[#64]`) refer to the original repository and do not correspond to issues in this repository.

## Commit Convention

Format: `type: description` or `type(scope): description`
Issue reference (optional): `type: description (#N)`

```
feat: new feature
fix: bug fix
refactor: code restructuring
docs: documentation changes
chore: build/tooling changes
test: test additions or changes
ci: CI/CD changes
perf: performance improvement
style: code style (formatting, whitespace)
i18n: internationalization
```

This is enforced by a pre-commit hook (`commitlint`). Invalid messages will be rejected.

## Pull Request Process

1. Create a feature branch from `main`
2. Make your changes following `AGENTS.md` and any relevant tool-specific harness docs
3. Run `make check` (lint + format check + tests)
4. Submit a PR using the [PR template](.github/pull_request_template.md)

## Code of Conduct

Please read our [Code of Conduct](CODE_OF_CONDUCT.md) before contributing.
