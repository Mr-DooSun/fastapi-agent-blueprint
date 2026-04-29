# Quickstart — run the blueprint in 60 seconds

Zero external infrastructure. No Docker. No Postgres. No cloud credentials.
Just Python + `uv` + one command.

## Prerequisites

- Python `>=3.12.9`
- [`uv`](https://docs.astral.sh/uv/) (package manager)

## Run it

```bash
make setup         # first time only — create venv + install deps
make quickstart    # boots FastAPI on SQLite + InMemory broker
```

The server comes up on `http://127.0.0.1:8001`:

| Endpoint | URL |
|----------|-----|
| Swagger docs | http://127.0.0.1:8001/docs-swagger |
| ReDoc        | http://127.0.0.1:8001/docs-redoc |
| Admin UI     | http://127.0.0.1:8001/admin (admin / admin) |
| Health       | http://127.0.0.1:8001/health |

## Exercise the API

In a second terminal:

```bash
make demo
```

This hits the `user` domain via `curl`: health check → create → get → list →
update → delete. Raw script is at [`scripts/demo.sh`](../scripts/demo.sh).

## What does `quickstart` actually configure?

`make quickstart` loads [`_env/quickstart.env`](../_env/quickstart.env.example)
(auto-copied from the committed template on first run).

| Setting | Value |
|---------|-------|
| `ENV` | `quickstart` |
| `DATABASE_ENGINE` | `sqlite` → `./quickstart.db` |
| `BROKER_TYPE` | `inmemory` (no queue server needed) |
| `STORAGE_TYPE` | _(unset — object storage disabled)_ |
| `LLM_PROVIDER` / `EMBEDDING_PROVIDER` | _(unset — AI features disabled)_ |
| `ADMIN_BOOTSTRAP_USERNAME` / `ADMIN_BOOTSTRAP_PASSWORD` | `admin` / `admin` |

On startup the server auto-creates the SQLite schema from `Base.metadata`
(see [`src/_apps/server/bootstrap.py`](../src/_apps/server/bootstrap.py)) —
no migrations required.

**This path is for evaluation only.** `ADMIN_BOOTSTRAP_PASSWORD=admin` and
the shared `ADMIN_STORAGE_SECRET` will not pass the `stg`/`prod` safety check
in [`src/_core/config.py`](../src/_core/config.py). NiceGUI admin login uses
the DB-backed auth domain after the bootstrap user is created or promoted.

## Next steps

- **Real local development** — copy `_env/local.env.example` to
  `_env/local.env`, edit values, then run `make dev` (spins up PostgreSQL
  via Docker Compose).
- **Add a domain** — see [AGENTS.md](../AGENTS.md) and
  [docs/ai-development.md](ai-development.md), or invoke the
  `/new-domain` skill if you use Claude Code / Codex.
- **Enable AI features** — set `LLM_PROVIDER` / `EMBEDDING_PROVIDER` (and
  the matching credentials) in your env file. The `classification` domain
  demonstrates the PydanticAI Agent integration.

## Troubleshooting

- **Port 8001 already in use** — kill the previous server:
  `pkill -f run_server_local.py`
- **Fresh schema** — delete the SQLite file: `rm -f ./quickstart.db`, then
  re-run `make quickstart`
- **Regenerate the env file** — delete `_env/quickstart.env` and run
  `make quickstart` again
