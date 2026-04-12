# Alembic Migration Management — Detailed Procedure

## Pre-check
1. Verify `alembic.ini` exists
2. Verify `_env/local.env` file exists and contains DB connection info
3. Verify target domain's Model file exists: `src/{name}/infrastructure/database/models/{name}_model.py`

> **Note**: `load_models()` in `migrations/env_utils.py` **automatically discovers** all models
> under `src/*/infrastructure/database/models/`. No separate import configuration needed.

## Command Mapping

### generate (Create new migration)
```bash
alembic revision --autogenerate -m "{domain}: {description}"
```
- Message format: `"{domain}: {description}"` (e.g., `"user: add email_verified column"`)
- Always show the generated file to the user and request review

### upgrade (Apply migration)
```bash
alembic upgrade head    # Apply up to latest
alembic upgrade +1      # Apply one step only
```

### downgrade (Rollback migration)
```bash
alembic downgrade -1    # Rollback one step
```

### status (Check current state)
```bash
alembic current         # Currently applied revision
alembic history         # Full history
```

## Workflow

### Migration after adding a new domain
1. Confirm domain Scaffolding is complete via `/new-domain {name}`
2. Review Model file: `src/{name}/infrastructure/database/models/{name}_model.py`
3. `alembic revision --autogenerate -m "{name}: initial migration"`
4. Review generated file: latest file under `migrations/versions/`
5. Ask user to verify the upgrade/downgrade functions
6. After approval, apply with `alembic upgrade head`

### Migration after modifying an existing domain model
1. Verify Model changes (compare before/after)
2. `alembic revision --autogenerate -m "{name}: {change description}"`
3. Review the generated file
4. After user approval, `alembic upgrade head`

## Cautions
- **autogenerate is not 100% accurate** -- always review the generated file
- **Column renames are not detected** (generated as drop+add) -- manual correction needed
- Verify the `env` value in `alembic.ini` matches the environment (local/dev/stg/prod)
- **Always back up before applying to production**
- The `migrations/versions/` directory is auto-created on first revision if it doesn't exist

## Verification after upgrade/downgrade
1. `alembic current` -- verify applied revision
2. Run domain integration tests: `pytest tests/integration/{name}/ -v` (verify DB schema matches)
3. Report results to the user
