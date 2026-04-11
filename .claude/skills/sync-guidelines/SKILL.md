---
name: sync-guidelines
disable-model-invocation: true
description: |
  This skill should be used when the user asks to "sync guidelines",
  "document inspection", "check skill updates",
  "update project-dna", "sync patterns", "verify code-document consistency",
  or after architecture changes to verify Skills/CLAUDE.md match the actual code.
---

# Guideline Synchronization Inspection

After design changes, inspect whether CLAUDE.md, Skills, and `.claude/rules/` are consistent with the actual code.

## Reference Code Analysis
Read `src/user/` as the reference domain to identify current actual patterns:
- Base class import paths
- Class inheritance structure
- Conversion Patterns (Model->DTO, DTO->Response)
- DI patterns (Singleton/Factory)
- File structure

## Inspection Targets (3 Categories)
1. **CLAUDE.md <-> Code** -- Absolute Prohibitions, Conversion Patterns, Write DTO criteria
2. **Skills <-> Code** -- Whether each skill's SKILL.md matches the current state (references are checked separately in Phase 5)
3. **`.claude/rules/` <-> Code** -- architecture-conventions, project-status, project-overview

Refer to `${CLAUDE_SKILL_DIR}/references/drift-checklist.md` for detailed inspection items.

## Output Format

```
=== Guideline Synchronization Inspection Results ===

[OK] CLAUDE.md: Absolute Prohibitions -- No violations found
[DRIFT] /new-domain: Base class import -- Path change detected
  -> Previous: src._core.infrastructure.database.base_repository
  -> Actual: src._core.database.base_repository
  -> Action: Update .claude/skills/new-domain/references/scaffolding-layers.md required

Sync required: X items / Total: Y items
```

## Actions When DRIFT Is Found
1. Show the list of discovered mismatches to the user
2. Suggest a fix for each mismatch
3. Update the relevant files after user approval
4. Re-run the inspection after updates to confirm all items are [OK]

## Phase 4: project-dna.md Regeneration

Regenerate `.claude/skills/_shared/project-dna.md` when DRIFT is found or the user requests it.

### Regeneration Procedure
1. Scan `src/user/` as the reference domain using Glob/Read
2. Extract `src/_core/` Base class signatures:
   - Import paths (actual file locations of all Base classes)
   - Generic parameters (TypeVar bounds, class definitions)
   - `__init__` signatures (BaseRepository, etc.)
   - Method list (BaseRepositoryProtocol)
3. Extract DI patterns: check `providers.Singleton` / `providers.Factory` mappings in each Container
4. Scan security tools: extract active tool list from `pyproject.toml` and `.pre-commit-config.yaml`
5. Scan active features: check whether `jwt`, `UploadFile`, `RBAC`, `slowapi`, `websocket` imports exist in the codebase
6. Regenerate `.claude/skills/_shared/project-dna.md` with the latest information (update date)
7. Compare each Skill's references/ files with project-dna.md -> report mismatches
8. Update `.claude/rules/architecture-conventions.md`
   (data flow, object roles, generic signatures 변경 반영)
9. Update `.claude/rules/project-status.md`
   (Recent Major Changes 테이블, 버전 컨텍스트, violation status 갱신)
   - `git log --oneline --since="{last_synced_date}"` 로 주요 변경 식별
   - project-dna.md §8 "Not implemented" 항목으로 Not Yet Implemented 갱신
10. Update `.claude/rules/project-overview.md`
    (인프라 옵션, 환경 설정, app entrypoint 변경 반영)
11. Update `.claude/rules/commands.md`
    (신규 CLI 명령, env vars, 테스트 명령, 검증 명령 반영)

All rules files: update "Last synced" date line to current date.

## Phase 5: References Drift Inspection

After project-dna.md regeneration is complete, inspect whether each Skill's references/ files are consistent with the current code.
Follow the "5. References <-> Code" section in `${CLAUDE_SKILL_DIR}/references/drift-checklist.md` for detailed inspection items.

### Automated Verification ([AUTO-FIX] Targets)
Items that can be mechanically extracted from code. When drift is found, generate a fix diff and present it to the user.

1. **File List** (`new-domain/references/scaffolding-layers.md`)
   - Compare `Glob src/user/**/*.py` results with the file list (items 1-26) in scaffolding-layers.md
   - Detect missing/deleted files

2. **Factory Pattern** (`test-domain/references/test-patterns.md`)
   - Read `tests/factories/user_factory.py` and compare with code blocks in test-patterns.md
   - Detect function signature and import path changes

3. **Skill Mapping** (`plan-feature/references/planning-checklists.md`)
   - Collect `name:` fields from `.claude/skills/*/SKILL.md`
   - Compare with the Skill column in the "Skill Mapping Table" of planning-checklists.md

### Manual Check ([REVIEW] Targets)
Policy/standard-based content. Only detect whether related sources have changed and request user review.

4. **Architecture Checklist** (`review-architecture/references/checklist.md`)
   - Compare the number of Absolute Prohibitions in CLAUDE.md vs. the number of check items in checklist.md
   - On mismatch, request confirmation on whether to add Grep patterns for the new rules

5. **Security Checklist** (`security-review/references/security-checklist.md`)
   - Compare project-dna.md section 8 active feature status with `[when applicable]` items
   - Request confirmation on whether security check items exist for newly activated features

### Phase 5 Output Format

```
--- References Drift Inspection ---

[AUTO-FIX] scaffolding-layers.md: File list
  -> Missing file detected: src/{name}/domain/value_objects/__init__.py
  -> Fix suggestion generated -- Would you like to apply it?

[OK] test-patterns.md: Factory pattern -- No changes
[OK] planning-checklists.md: Skill mapping -- No changes

[REVIEW] security-checklist.md: Active feature change detected
  -> "JWT/Authentication" toggled to active in project-dna.md section 8
  -> Please verify whether JWT-related security checks need to be added to [when applicable] items

References: AUTO-FIX X items | REVIEW X items | OK X items
```

### Post-Regeneration Verification
- Verify all import paths in project-dna.md match actual files using `Grep`
- Compare generated Generic signatures against source code definitions

## When to Run
- After architecture refactoring
- After changes to Base classes or shared modules
- After introducing new patterns or conventions
- When project-dna.md was last updated more than 2 weeks ago
- Periodic inspection (recommended once every 2 weeks)
