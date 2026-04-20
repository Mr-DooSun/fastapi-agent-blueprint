# Guideline Synchronization — Detailed Procedure

After design changes, inspect whether `AGENTS.md`, `CLAUDE.md`, shared workflow references, Codex workflow assets, Claude skills, and `.claude/rules/` are consistent with the actual code.

## Reference Code Analysis
Read `src/user/` as the reference domain to identify current actual patterns:
- Base class import paths
- Class inheritance structure
- Conversion Patterns (Model->DTO, DTO->Response)
- DI patterns (Singleton/Factory)
- File structure

## Phase 1-3: Code ↔ Documentation Consistency

### Inspection Targets (5 Categories)
1. **AGENTS.md <-> Code** -- Absolute Prohibitions, Conversion Patterns, Write DTO criteria
2. **Shared references <-> Code** -- `docs/ai/shared/` content and the current implementation
3. **Harness docs <-> Workflow layers** -- `CLAUDE.md`, `.codex/config.toml`, `.codex/hooks.json`, `.agents/skills/`
4. **Skills <-> Code** -- Whether each skill's `SKILL.md` matches the current state (references are checked separately in Phase 5)
5. **`.claude/rules/` <-> Code** -- architecture-conventions, project-status, project-overview

Refer to `docs/ai/shared/drift-checklist.md` for detailed inspection items.

### Output Format

```
=== Guideline Synchronization Inspection Results ===

[OK] AGENTS.md: Absolute Prohibitions -- No violations found
[DRIFT] /new-domain: Base class import -- Path change detected
  -> Previous: src._core.infrastructure.persistence.rdb.base_repository
  -> Actual: src._core.database.base_repository
  -> Action: Update `docs/ai/shared/scaffolding-layers.md` and any dependent skill entry points

Sync required: X items / Total: Y items
```

### Actions When DRIFT Is Found
1. Show the list of discovered mismatches to the user
2. Suggest a fix for each mismatch
3. Update the relevant files after user approval
4. Re-run the inspection after updates to confirm all items are [OK]

## Phase 4: project-dna.md Regeneration

Regenerate `docs/ai/shared/project-dna.md` when DRIFT is found or the user requests it.

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
6. Regenerate `docs/ai/shared/project-dna.md` with the latest information (update date)
7. Compare each Skill's references with `docs/ai/shared/project-dna.md` -> report mismatches

### Post-Regeneration Verification
- Verify all import paths in project-dna.md match actual files using `Grep`
- Compare generated Generic signatures against source code definitions

## Phase 5: References Drift Inspection

After project-dna.md regeneration is complete, inspect whether `docs/ai/shared/` documents are consistent with the current code.
Follow the "5. References <-> Code" section in `docs/ai/shared/drift-checklist.md` for detailed inspection items.

### Automated Verification ([AUTO-FIX] Targets)
Items that can be mechanically extracted from code. When drift is found, generate a fix diff and present it to the user.

1. **File List** (`docs/ai/shared/scaffolding-layers.md`)
   - Compare `Glob src/user/**/*.py` results with the file list (items 1-26) in `docs/ai/shared/scaffolding-layers.md`
   - Detect missing/deleted files

2. **Factory Pattern** (`docs/ai/shared/test-patterns.md`)
   - Read `tests/factories/user_factory.py` and compare with code blocks in `docs/ai/shared/test-patterns.md`
   - Detect function signature and import path changes

3. **Skill Mapping** (`docs/ai/shared/planning-checklists.md`)
   - Collect `name:` fields from `.claude/skills/*/SKILL.md` and `.agents/skills/*/SKILL.md`
   - Compare with the Skill column in the "Skill Mapping Table" of `docs/ai/shared/planning-checklists.md`

### Manual Check ([REVIEW] Targets)
Policy/standard-based content. Only detect whether related sources have changed and request user review.

4. **Architecture Checklist** (`docs/ai/shared/architecture-review-checklist.md`)
   - Compare the number of Absolute Prohibitions in AGENTS.md vs. the number of check items in `docs/ai/shared/architecture-review-checklist.md`
   - On mismatch, request confirmation on whether to add Grep patterns for the new rules

5. **Security Checklist** (`docs/ai/shared/security-checklist.md`)
   - Compare `docs/ai/shared/project-dna.md` section 8 active feature status with `[when applicable]` items
   - Request confirmation on whether security check items exist for newly activated features

### Hybrid C Skill Structure Verification

For skills that have been migrated to Hybrid C:
- [ ] `docs/ai/shared/skills/{name}.md` exists and is non-empty
- [ ] Claude wrapper references `docs/ai/shared/skills/{name}.md`
- [ ] Codex wrapper references `docs/ai/shared/skills/{name}.md`
- [ ] Phase count in shared procedure matches Phase overview in Claude wrapper
- [ ] No tool-specific instructions leaked into shared procedure (grep for `.claude/rules/`, `.claude/skills/`, `.agents/skills/`)

### Phase 5 Output Format

```
--- References Drift Inspection ---

[AUTO-FIX] scaffolding-layers.md: File list
  -> Missing file detected: src/{name}/domain/value_objects/__init__.py
  -> Fix suggestion generated -- Would you like to apply it?

[OK] test-patterns.md: Factory pattern -- No changes
[OK] planning-checklists.md: Skill mapping -- No changes
[OK] Hybrid C: sync-guidelines -- Structure verified

[REVIEW] security-checklist.md: Active feature change detected
  -> "JWT/Authentication" toggled to active in project-dna.md section 8
  -> Please verify whether JWT-related security checks need to be added to [when applicable] items

References: AUTO-FIX X items | REVIEW X items | OK X items
```

## Sync Completion Contract

Do not treat the sync as complete until the closing summary includes all four sections below.

```text
project-dna: updated | unchanged
AUTO-FIX: ...
REVIEW: ...
Remaining: ...
```

- **project-dna**: Whether `docs/ai/shared/project-dna.md` was regenerated, updated, or confirmed unchanged.
- **AUTO-FIX**: Mechanically fixable drift targets and whether each fix was applied. If none: `AUTO-FIX: none`.
- **REVIEW**: Human-review targets — explain why policy or product judgment is needed. If none: `REVIEW: none`.
- **Remaining**: Unresolved drift that still remains after updates. If none: `Remaining: none`.

If one or more `REVIEW` items exist, the sync result must not conclude with "nothing to change" or equivalent wording.

Example:

```text
project-dna: updated (new Base class paths synced)
AUTO-FIX: 2 items applied (scaffolding-layers, planning-checklists)
REVIEW: 1 item (security-checklist lacks checks for newly active "Embedding")
Remaining: none
```

## When to Run
- After architecture refactoring
- After changes to Base classes or shared modules
- After introducing new patterns or conventions
- When project-dna.md was last updated more than 2 weeks ago
- Periodic inspection (recommended once every 2 weeks)
