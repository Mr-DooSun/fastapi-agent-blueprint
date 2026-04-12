# Bug Fix Workflow — Detailed Procedure

## Phase 1: Reproduce
1. Analyze the bug description to identify the affected domain and layer
2. If a GitHub issue number is provided, check details with `gh issue view {number}`
3. Check existing tests for a reproducible test case
4. If no reproduction test exists, write one first (confirm red state)

## Phase 2: Trace
1. Locate the relevant code
2. Trace the call path: Router → UseCase → Service → Repository
3. Inspect conversion boundaries:
   - Is there data loss when passing Request → UseCase?
   - Is the field mapping correct during Model → DTO conversion?
   - Are the excluded fields correct during DTO → Response conversion?
4. Inspect DI wiring:
   - Is the correct implementation being injected?
   - Is the Singleton/Factory distinction correct?

## Phase 3: Fix
1. Fix at the lowest possible layer (prefer domain > infrastructure)
2. Follow existing patterns when fixing — do not introduce new patterns (Conversion Patterns: `docs/ai/shared/project-dna.md` §6, Router: §9)
3. Confirm compliance with `AGENTS.md` Absolute Prohibitions

## Phase 4: Verify
1. Confirm the reproduction test from Phase 1 now passes (green)
2. Confirm existing tests are not broken:
   ```bash
   pytest tests/unit/{domain}/ tests/integration/{domain}/ -v
   ```
3. Run pre-commit hooks:
   ```bash
   pre-commit run --files {changed files}
   ```

## Phase 5: Commit
Commit convention: `{type}: {description} (#{issue})`

Types:
- `fix` — bug fix
- `feat` — new feature
- `refactor` — refactoring
- `test` — add/modify tests
- `docs` — documentation
- `chore` — miscellaneous

If no related issue exists, omit the issue reference: `{type}: {description}`

Propose a commit message to the user and commit after confirmation.
