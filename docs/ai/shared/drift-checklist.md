# Guideline Synchronization Inspection Items (Detailed)

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

## 1A. CLAUDE.md ↔ Claude Harness Consistency Check

Read CLAUDE.md and verify Claude-only guidance still matches the harness:

- [ ] `.mcp.json` role is described as Claude-only MCP configuration
- [ ] `.claude/settings.json` hooks and `pyright-lsp` guidance still match current files
- [ ] Slash skill list matches the actual `.claude/skills/` directory

## 1B. `.claude/rules/absolute-prohibitions.md` ↔ AGENTS.md Sync Check

- [ ] Compare the 5 prohibition rules in `.claude/rules/absolute-prohibitions.md` against `AGENTS.md` "Absolute Prohibitions" section
- [ ] Verify the Note line (Domain → Interface schema imports) is identical in both files
- [ ] If mismatch found: update `.claude/rules/absolute-prohibitions.md` to match `AGENTS.md` (AGENTS.md is canonical)

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
- [ ] Data flow: RDB + DynamoDB 양쪽 variant 포함?
- [ ] BaseService/BaseDynamoService generic signature가 실제 코드와 일치?
- [ ] Object Roles: DTO, Schema, Model, DynamoModel, Admin Page 모두 포함?
- [ ] Broker Selection 섹션이 core_container.py Selector 설정과 일치?

### project_status
- [ ] Recent Major Changes: "Last synced" 이후 머지된 주요 PR/feature 포함?
- [ ] Architecture Violation Status: grep 체크 실행 결과와 일치?
- [ ] Not Yet Implemented: project-dna.md §8 "Not implemented" 항목과 일치?

### project_overview
- [ ] Infrastructure Options: `src/_core/infrastructure/` 하위 디렉터리와 일치?
- [ ] App Entrypoints: `src/_apps/` 하위 디렉터리와 일치?
- [ ] Environment Config: `src/_core/config.py` Settings validators와 일치?

### commands (`.claude/rules/commands.md`)
- [ ] Run 명령: 현재 entrypoint 파일과 일치?
- [ ] Architecture 검증 grep: 현행 위반 규칙 탐지 (구시대 패턴 아님)?
- [ ] Test 명령: 인프라 variant별 커버 (RDB, DynamoDB, Broker)?

### All rules files
- [ ] 각 rules 파일의 "Last synced" 날짜가 2주 이내?

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
  - Count Phase/Step overview items in `.claude/skills/{name}/SKILL.md` wrapper
  - On mismatch: flag as [DRIFT] — shared procedure may have been updated without updating the wrapper overview

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
  - Extract the feature list from items marked `[when applicable]` in `docs/ai/shared/security-checklist.md`
  - Check whether security inspection items exist for newly activated features
  - On uncovered features: confirm with the user whether security inspection items need to be added for those features
