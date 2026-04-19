.PHONY: help setup dev test lint format check clean

## Show available commands
help:
	@echo "Usage: make <command>"
	@echo ""
	@awk '/^## /{desc=substr($$0,4)} /^[a-zA-Z_-]+:/{if(desc){printf "  \033[36m%-15s\033[0m %s\n", $$1, desc; desc=""}}' $(MAKEFILE_LIST)

.DEFAULT_GOAL := help

## Setup development environment
setup:
	uv venv && uv sync --group dev && uv run pre-commit install && uv run pre-commit install --hook-type commit-msg

## Start local development (postgres + server)
dev:
	docker compose -f docker-compose.local.yml up -d postgres && \
	sleep 2 && \
	uv run alembic upgrade head && \
	uv run python run_server_local.py

## Start worker locally
worker:
	uv run python run_worker_local.py

## Run all tests (SQLite in-memory by default)
test:
	uv run pytest tests/ -v

## Run all tests against the local docker PostgreSQL (test_db -> postgresql)
test-pg:
	docker compose -f docker-compose.local.yml up -d postgres && \
	sleep 2 && \
	set -a && . _env/local.env && set +a && \
	TEST_DB_ENGINE=postgresql \
	TEST_DB_USER=postgres \
	TEST_DB_PASSWORD=postgres \
	TEST_DB_HOST=localhost \
	TEST_DB_PORT=5432 \
	TEST_DB_NAME=postgres \
	uv run pytest tests/ -v

## Run DynamoDB integration tests against local dynamodb-local
test-dynamo:
	docker compose -f docker-compose.local.yml up -d dynamodb-local && \
	sleep 2 && \
	set -a && . _env/local.env && set +a && \
	uv run pytest tests/integration/_core/infrastructure/dynamodb/ -v

## Run tests with coverage
test-cov:
	uv run pytest tests/ -v --cov=src --cov-report=term-missing

## Run linter
lint:
	uv run ruff check src/

## Run formatter
format:
	uv run ruff format src/

## Run all checks (lint + format check + tests)
check:
	uv run ruff check src/ && \
	uv run ruff format --check src/ && \
	uv run pytest tests/ -v

## Run pre-commit on all files
pre-commit:
	uv run pre-commit run --all-files

## Run database migrations
migrate:
	uv run alembic upgrade head

## Generate new migration
migration:
	@read -p "Migration message: " msg; \
	uv run alembic revision --autogenerate -m "$$msg"

## Clean up
clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null; \
	find . -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null; \
	find . -type d -name .ruff_cache -exec rm -rf {} + 2>/dev/null; \
	rm -rf .coverage htmlcov/
