# Guideline Synchronization Inspection Items (Detailed)

> This checklist defines drift work for `/sync-guidelines`.
>
> Taxonomy:
> - `AUTO-FIX` = auto-fixable drift that can be updated mechanically
> - `REVIEW` = policy-review drift that needs human judgment
> - `DRIFT` = unresolved mismatch discovered during inspection
> - `OK` = verified and aligned

## 1. AGENTS.md ↔ Code Consistency Check

Read AGENTS.md and compare each section against the actual code:

- [ ] **Absolute Prohibitions**: Verify no violations exist using Grep
  - `from src.*.infrastructure` in domain/ files
  - `class.*Mapper` definitions
  - Remaining Entity patterns (`to_entity(`, `from_entity(`, `class.*Entity`)
- [ ] **Conversion Patterns**: Verify the patterns described in AGENTS.md are used identically in actual code
  - Request → Service: direct pass-through via `entity=item`
  - Model → DTO: `model_validate(model, from_attributes=True)`
  - DTO → Response: `model_dump(exclude={...})`
- [ ] **Write DTO criteria**: Verify current Request/DTO usage matches the defined criteria
- [ ] **Language Policy** (AGENTS.md § Language Policy): Run `python3 tools/check_language_policy.py` and confirm zero violations across Tier 1 paths. Bilingual escape tokens (`[자명]`/`[긴급]`/`[탐색]`) and locale data files (`LOCALE_DATA_FILES`) are the two narrowly-scoped exceptions, scoped per-file in the checker. Flag any new non-English prose insertion as a sync-required drift candidate.

## 1A. CLAUDE.md ↔ Claude Harness Consistency Check

Read CLAUDE.md and verify Claude-only guidance still matches the harness:

- [ ] `.mcp.json` role is described as Claude-only MCP configuration
- [ ] `.claude/settings.json` hooks and `pyright-lsp` guidance still match current files
- [ ] Slash skill list matches the actual `.claude/skills/` directory

## 1B. `.claude/rules/absolute-prohibitions.md` ↔ AGENTS.md Sync Check

- [ ] Compare the 5 prohibition rules in `.claude/rules/absolute-prohibitions.md` against `AGENTS.md` "Absolute Prohibitions" section
- [ ] Verify the Note line (Domain → Interface schema imports) is identical in both files
- [ ] If mismatch found: update `.claude/rules/absolute-prohibitions.md` to match `AGENTS.md` (AGENTS.md is canonical)

## 1C. `harness-asset-matrix.md` ↔ Filesystem Sync Check (ADR 045)

- [ ] Enumerate actual filesystem assets in scope:
  - Tier 0: `AGENTS.md`, `CLAUDE.md`, `.codex/config.toml`, `.codex/hooks.json`, `.claude/settings.json`, `.claude/settings.local.json`, `.mcp.json`, plus every `docs/history/0XX-*.md` ADR (including ADR 045)
  - Tier 1: every `docs/ai/shared/*.md` (parent folder only, not `skills/`)
  - Tier 2: every skill triple — `docs/ai/shared/skills/{name}.md`, `.claude/skills/{name}/SKILL.md`, `.agents/skills/{name}/SKILL.md`
  - Tier 3: every file under `.claude/hooks/` and `.codex/hooks/`
  - Tier 4: every file under `.claude/rules/` and `.codex/rules/`
- [ ] Verify each enumerated asset has exactly one row in `docs/ai/shared/harness-asset-matrix.md`
- [ ] Verify the Bucket Distribution Summary count equals the row count (subtracting `.gitignore`d entries from the share-percentage denominator)
- [ ] Verify each row's `Bucket` is one of `Keep` / `Replace` / `Overlay` / `Drop` and matches the bucket definitions at the top of the matrix
- [ ] For any asset classified `Drop`: verify with `rg <asset> .claude/ .codex/` that no harness component still references it

## 1D. `governor-review-log/` ↔ Governor-Changing PR Sync Check (ADR 045 Pillar 4)

The canonical definition of "governor-changing PR" is in [`governor-paths.md`](governor-paths.md). Do not duplicate the path list here; consult that file when running this check.

- [ ] Enumerate merged PRs touching the Tier A / B / C globs since the last sync run:
  ```bash
  gh pr list --state merged --search "merged:>=$(cat .last-sync-date 2>/dev/null || echo 2026-04-26)" --json number,title,files
  ```
- [ ] For every such PR, verify a `docs/ai/shared/governor-review-log/pr-{NNN}-{slug}.md` entry exists **and the `{NNN}` segment of the filename equals the PR number** (Round-4 R4.4 — prevents stale entries from satisfying the gate).
- [ ] Verify `governor-review-log/README.md` Index table includes a row for every entry (no missing rows, no orphan rows).
- [ ] Each entry contains the required sections: `Summary`, `Review Rounds` (each round with explicit `Final Verdict`), `Inherited Constraints`, `Self-Application Proof`. Empty sections are acceptable only when explicitly justified.
- [ ] Apply the exclusions from `governor-paths.md`: log-only backfill PRs that extend an existing entry are exempt from requiring a new entry of their own.
- [ ] If any entry is missing or incomplete: open an issue *Backfill governor-review-log for PR #NNN* and treat it as `REVIEW` drift, never silent `AUTO-FIX`.
- [ ] If a PR was merged that touched the trigger glob *and* had no cross-tool review captured: surface as `DRIFT` and recommend re-running cross-tool review on the merged commit retrospectively.

## 2. Skills ↔ Code Consistency Check

Read each skill's SKILL.md and compare against reference code:

- [ ] **`/new-domain`**: Verify the file list matches the actual `src/user/` structure
  - Whether newly added files are not yet reflected in Skills
  - Whether deleted files still remain in Skills
  - Whether import paths match actual base class locations
  - Whether class signatures (Generic type parameters, etc.) match
- [ ] **`/add-api`**: Verify the implementation order and patterns match current code
  - Router decorator patterns (`@inject`, `Depends(Provide[...])`)
  - SuccessResponse usage patterns
- [ ] **`/add-worker-task`**: Verify task patterns match current broker configuration
  - `@broker.task` decorator usage
  - DI wiring patterns
- [ ] **`/review-architecture`**: Verify checklist items cover all current rules
- [ ] **`/test-domain`**: Verify test patterns match actual test code
- [ ] **`/add-admin-page`**: Verify config/page patterns match current code
  - Config pattern: compare against `src/user/interface/admin/configs/user_admin_config.py`
  - Page pattern: compare against `src/user/interface/admin/pages/user_page.py`
  - Compare both against project-dna.md §11
- [ ] **`/add-cross-domain`**: Verify Protocol-based dependency patterns match current implementation
- [ ] **`/onboard`**: Verify the recommended Skills list in `docs/ai/shared/onboarding-role-tracks.md` matches the actual skill list
- [ ] **`/onboard`**: Verify format options (Guided, Q&A, Explore) are consistent between `SKILL.md` and `docs/ai/shared/onboarding-role-tracks.md`

## 3. `.claude/rules/` ↔ Current State Check

Read each `.claude/rules/` file and compare against current code:

### architecture_conventions
- [ ] Data flow: covers both RDB and DynamoDB variants?
- [ ] BaseService / BaseDynamoService generic signatures match the actual code?
- [ ] Object Roles: includes DTO, Schema, Model, DynamoModel, and Admin Page?
- [ ] Broker Selection section matches the Selector wiring in `core_container.py`?

### project_status
- [ ] Recent Major Changes includes every notable PR / feature merged since the documented "Last synced" date?
- [ ] Architecture Violation Status matches the live grep results?
- [ ] Not Yet Implemented matches project-dna.md §8 "Not implemented"?

### project_overview
- [ ] Infrastructure Options matches the subdirectories under `src/_core/infrastructure/`?
- [ ] App Entrypoints matches the subdirectories under `src/_apps/`?
- [ ] Environment Config matches the Settings validators in `src/_core/config.py`?

### commands (`.claude/rules/commands.md`)
- [ ] Run commands still target the current entrypoint files?
- [ ] Architecture-verification greps still target current violation patterns (not legacy ones)?
- [ ] Test commands still cover each infra variant (RDB, DynamoDB, Broker)?

### All rules files
- [ ] "Last synced" date of every rules file is within the last two weeks?

## 4. project-dna.md ↔ Code Consistency Check

Compare each section of `docs/ai/shared/project-dna.md` against actual code:

- [ ] **Layer structure**: Verify the directory structure in project-dna.md §1 matches the actual `src/user/` structure
  - Compare against Glob `src/user/**/*.py` results
- [ ] **Base class paths**: Verify all import paths in §2 match actual file locations
  - Confirm each path can import the class from the corresponding module
- [ ] **Generic types**: Verify signatures in §3 match current Base class definitions
  - Check `BaseRepositoryProtocol`, `BaseRepository`, `SuccessResponse` class definitions
- [ ] **CRUD methods**: Verify the `BaseRepositoryProtocol` method list in §4 is up to date
  - Compare method lists against actual code
- [ ] **DI patterns**: Verify Singleton/Factory mappings in §5 match current `UserContainer` code
- [ ] **Conversion Patterns**: Verify `model_validate`/`model_dump` usage in §6 matches current implementation
- [ ] **Security tools**: Verify the tool list in §7 matches `pyproject.toml` and `.pre-commit-config.yaml`
  - In particular, check bandit skip list and flake8 ignore list
- [ ] **Active features**: Verify feature status in §8 is up to date
  - Use Grep to check whether imports for `jwt`, `UploadFile`, `RBAC`, `slowapi`, etc. exist
- [ ] **Admin Page Pattern**: Verify §11 matches actual admin infrastructure
  - Compare BaseAdminPage fields against `src/_core/infrastructure/admin/base_admin_page.py`
  - Compare file structure convention against `src/user/interface/admin/` layout (configs/ + pages/)
  - Verify auto-discovery convention in `src/_apps/admin/bootstrap.py`
- [ ] **Inheritance chain**: Verify BaseRequest/BaseResponse parent classes in §2 are accurate
  - Check the `ApiConfig` → `BaseModel` chain

## 5. Shared Documents ↔ Code Consistency Check

Inspect whether `docs/ai/shared/` documents match the current code.
(project-dna.md is already verified in Section 4)

### Automated Verification (Glob/Grep-based — [AUTO-FIX] targets)

- [ ] **`new-domain` file list** (`docs/ai/shared/scaffolding-layers.md`):
  - Exclude `__init__.py` from `Glob src/user/**/*.py` results
  - Extract `src/{name}/` paths from the numbered list (1~21) in `docs/ai/shared/scaffolding-layers.md`
  - Replace `{name}` → `user` and compare both sides
  - On drift: suggest adding missing files to the appropriate Layer section, suggest removing deleted files

- [ ] **`new-domain` admin file structure** (`docs/ai/shared/scaffolding-layers.md`):
  - Verify admin uses two-directory pattern: `configs/` + `pages/` (not single-file)
  - Glob `src/user/interface/admin/configs/*.py` → must include `user_admin_config.py`
  - Glob `src/user/interface/admin/pages/*.py` → must include `user_page.py`
  - On drift: update `docs/ai/shared/scaffolding-layers.md` Layer 4 admin section and `docs/ai/shared/project-dna.md` §11

- [ ] **`test-domain` Factory patterns** (`docs/ai/shared/test-patterns.md`):
  - Read `tests/factories/user_factory.py` and extract the function list (def lines)
  - Extract function signatures from code blocks in `docs/ai/shared/test-patterns.md`
  - Compare function names/parameters/import paths for consistency
  - On drift: suggest updating code blocks based on user_factory.py

- [ ] **`plan-feature` Skill mapping** (`docs/ai/shared/planning-checklists.md`):
  - Collect `name:` fields from each file via `Glob .claude/skills/*/SKILL.md` and `Glob .agents/skills/*/SKILL.md`
  - Extract `/skill-name` entries from the "Mapped Skill" column in `docs/ai/shared/planning-checklists.md` "3. Skill Mapping Table"
  - Compare both sets (additions/deletions/renames)
  - On drift: suggest adding/removing rows in the table

### Hybrid C Skill Structure Verification

- [ ] **Shared procedure existence** (`docs/ai/shared/skills/`):
  - For each Hybrid C skill, verify `docs/ai/shared/skills/{name}.md` exists and is non-empty
  - Compare the list against skills known to be migrated (check AGENTS.md Skill Split Convention)

- [ ] **Wrapper ↔ Shared procedure reference consistency**:
  - For each Hybrid C skill, verify `.claude/skills/{name}/SKILL.md` references `docs/ai/shared/skills/{name}.md`
  - For each Hybrid C skill, verify `.agents/skills/{name}/SKILL.md` references `docs/ai/shared/skills/{name}.md`
  - On missing reference: flag as [DRIFT] and suggest adding the reference

- [ ] **Phase count consistency**:
  - Count Phase/Step headings in `docs/ai/shared/skills/{name}.md`
  - Count Phase/Step overview items in both `.claude/skills/{name}/SKILL.md` and `.agents/skills/{name}/SKILL.md`
  - On mismatch: flag as [DRIFT] — shared procedure may have been updated without updating one or both wrappers

- [ ] **No tool-specific instructions in shared procedure**:
  - Grep `docs/ai/shared/skills/*.md` for `.claude/rules/`, `.claude/skills/`, `.agents/skills/`
  - Shared procedures must not contain tool-specific file paths or instructions
  - On violation: move tool-specific content to the appropriate wrapper

### Manual Inspection (Change-history-based — [REVIEW] targets)

- [ ] **`review-architecture` checklist** (`docs/ai/shared/architecture-review-checklist.md`):
  - Compare the **code-auditable** Absolute Prohibitions in AGENTS.md against the related inspection items in `docs/ai/shared/architecture-review-checklist.md`
  - Exclude the "No modifying or deleting shared rule sources without cross-reference verification" rule from this count; it remains in AGENTS.md / harness docs because it is process-oriented rather than a code-audit grep target
  - On mismatch: confirm with the user whether checklist coverage should be expanded for any newly code-auditable rule

- [ ] **`security-review` security checklist** (`docs/ai/shared/security-checklist.md`):
  - Extract the "active" feature list from `docs/ai/shared/project-dna.md` §8
  - Extract the feature list from items marked `[When applicable]` in `docs/ai/shared/security-checklist.md`
  - Check whether security inspection items exist for newly activated features and whether the live code differs from `project-dna`
  - On uncovered features: confirm with the user whether security inspection items need to be added for those features

## 6. Quality Gate Scenarios

Use these scenario checks when validating the redesigned workflow:

- [ ] Architecture-changing PR -> `/review-pr` should produce findings and/or drift candidates, and `/sync-guidelines` should be required before closure
- [ ] Security feature active in code but stale in `project-dna` -> `/security-review` should continue auditing and report stale-reference drift instead of ending in `SKIP`
- [ ] Shared procedure changed without wrapper updates -> `/sync-guidelines` should detect Hybrid C drift for both Claude and Codex wrappers
- [ ] Docs-only checklist meaning change -> `/sync-guidelines` should classify it as `REVIEW`, not a silent `AUTO-FIX`
