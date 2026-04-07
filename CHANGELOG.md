# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- Branch name validation in CI for pull requests (`{type}/{description}` format enforcement)

### Removed

- `/create-pr` skill — branch name validation moved to CI; PR creation handled by Claude Code built-in capability

## [0.2.0] - 2026-04-07

### Added

- Worker Payload Schema: `BasePayload` and `PayloadConfig` for worker message contract validation ([#45](https://github.com/Mr-DooSun/fastapi-agent-blueprint/pull/45))
- Database health check endpoint with `HealthService` ([#19](https://github.com/Mr-DooSun/fastapi-agent-blueprint/pull/19))
- `/create-pr` and `/review-pr` GitHub collaboration skills ([#31](https://github.com/Mr-DooSun/fastapi-agent-blueprint/pull/31))
- Conventional commit message validation hook ([#31](https://github.com/Mr-DooSun/fastapi-agent-blueprint/pull/31))
- `make help` as default Makefile target ([#31](https://github.com/Mr-DooSun/fastapi-agent-blueprint/pull/31))
- 9 missing ADRs (017-025) from full commit history analysis
- ADR 014 (OMC vs Native decision) and ADR 015 (rebranding) and ADR 016 (Worker Payload Schema)

### Changed

- Rebrand project to **AI Agent Backend Platform** (`fastapi-agent-blueprint`) ([#43](https://github.com/Mr-DooSun/fastapi-agent-blueprint/pull/43))
- Rename `interface/dtos/` to `interface/schemas/` for terminology consistency ([#38](https://github.com/Mr-DooSun/fastapi-agent-blueprint/pull/38))
- Unify exception handling with `app.add_exception_handler` ([#35](https://github.com/Mr-DooSun/fastapi-agent-blueprint/pull/35))
- Consolidate sync hook to single git-diff-based Stop hook ([#40](https://github.com/Mr-DooSun/fastapi-agent-blueprint/pull/40))
- Strengthen harness hook security checks and expand detection scope ([#47](https://github.com/Mr-DooSun/fastapi-agent-blueprint/pull/47))
- Extract `HealthService` to follow Router -> Service pattern ([#19](https://github.com/Mr-DooSun/fastapi-agent-blueprint/pull/19))
- Move health check logic into `Database.check_connection()` ([#29](https://github.com/Mr-DooSun/fastapi-agent-blueprint/pull/29))
- Translate all documentation to English (ADRs, skills, references, config, code comments) ([#25](https://github.com/Mr-DooSun/fastapi-agent-blueprint/pull/25))
- Improve ADR template with anti-rationalization principles ([#48](https://github.com/Mr-DooSun/fastapi-agent-blueprint/pull/48))
- Align all 17 existing ADRs with improved template structure ([#48](https://github.com/Mr-DooSun/fastapi-agent-blueprint/pull/48))

### Removed

- Domain Event infrastructure (unused) ([#38](https://github.com/Mr-DooSun/fastapi-agent-blueprint/pull/38))

### Fixed

- Correct `error_code` attribute in `ExceptionMiddleware` ([#26](https://github.com/Mr-DooSun/fastapi-agent-blueprint/pull/26))
- Sync flag file path for sandbox compatibility ([#38](https://github.com/Mr-DooSun/fastapi-agent-blueprint/pull/38))

## [0.1.0] - 2026-03-26

### Added

- Initial project structure with 3-tier hybrid layer architecture
- Domain auto-discovery system (`DynamicContainer` + factory function)
- `BaseService` and `BaseRepository` with generic CRUD operations
- User domain as reference implementation
- Alembic migration support
- Taskiq worker integration with RabbitMQ broker
- SQLAdmin dashboard
- Docker Compose for local development
- GitHub Actions CI workflow
- Ruff for unified linting and formatting
- Claude Code skills: `/new-domain`, `/add-api`, `/add-worker-task`, `/add-cross-domain`, `/review-architecture`, `/security-review`, `/test-domain`, `/fix-bug`, `/onboard`
- ADR documentation (001-013)
- CONTRIBUTING guide and issue templates

[Unreleased]: https://github.com/Mr-DooSun/fastapi-agent-blueprint/compare/v0.2.0...HEAD
[0.2.0]: https://github.com/Mr-DooSun/fastapi-agent-blueprint/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/Mr-DooSun/fastapi-agent-blueprint/releases/tag/v0.1.0
