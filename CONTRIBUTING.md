# Contributing to FastAPI Blueprint

Thank you for your interest in contributing! This guide will help you get started.

## Development Setup

```bash
# Clone the repository
git clone https://github.com/Mr-DooSun/fastapi-blueprint.git
cd fastapi-blueprint

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

# Set up environment variables
cp _env/local.env.example _env/local.env

# Start PostgreSQL
docker compose -f docker-compose.local.yml up -d postgres

# Run migrations and start the server
uv run alembic upgrade head
uv run python run_server_local.py --env local
```
</details>

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

These rules are enforced by pre-commit hooks:

- **Domain layer cannot import from Infrastructure** -- dependency inversion via Protocol
- **Model objects never leave the Repository** -- convert to DTO using `model_validate()`
- **No separate Mapper classes** -- use inline conversion
- **No Entity pattern** -- use DTOs only (see [ADR 004](docs/history/004-dto-entity-responsibility.md))

## Note on Commit History

This project was migrated from a private repository. Issue numbers in early commit messages (e.g., `[#57]`, `[#64]`) refer to the original repository and do not correspond to issues in this repository.

## Commit Convention

```
feat: new feature
fix: bug fix
refactor: code restructuring
docs: documentation changes
chore: build/tooling changes
test: test additions or changes
```

## Pull Request Process

1. Create a feature branch from `main`
2. Make your changes following the architecture rules above
3. Run `make check` (lint + format check + tests)
4. Submit a PR using the [PR template](.github/pull_request_template.md)

## Code of Conduct

Please read our [Code of Conduct](CODE_OF_CONDUCT.md) before contributing.
