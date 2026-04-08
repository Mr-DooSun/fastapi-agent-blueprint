# Guideline Synchronization Inspection Items (Detailed)

## 1. CLAUDE.md ↔ Code Consistency Check

Read CLAUDE.md and compare each section against the actual code:

- [ ] **Absolute Prohibitions**: Verify no violations exist using Grep
  - `from src.*.infrastructure` in domain/ files
  - `class.*Mapper` definitions
  - Remaining Entity patterns (`to_entity(`, `from_entity(`, `class.*Entity`)
- [ ] **Conversion Patterns**: Verify the 4 patterns described in CLAUDE.md are used identically in actual code
  - Request → Service: direct pass-through via `entity=item`
  - Model → DTO: `model_validate(model, from_attributes=True)`
  - DTO → Response: `model_dump(exclude={...})`
- [ ] **Write DTO criteria**: Verify current Request/DTO usage matches the defined criteria

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
- [ ] **`/add-cross-domain`**: Verify Protocol-based dependency patterns match current implementation
- [ ] **`/onboard`**: Verify the recommended Skills list in role-tracks.md matches the actual skill list
- [ ] **`/onboard`**: Verify format options (Guided, Q&A, Explore) are consistent between SKILL.md and role-tracks.md

## 3. Serena Memory ↔ Current State Check

Read Serena memory and compare against current code:

- [ ] **`architecture_conventions`**: Verify DO/DON'T rules match CLAUDE.md and actual code
- [ ] **`refactoring_status`**: Verify current progress is accurate
- [ ] **`project_overview`**: Verify tech stack, entry points, etc. are up to date

## 4. project-dna.md ↔ Code Consistency Check

Compare each section of `.claude/skills/_shared/project-dna.md` against actual code:

- [ ] **Layer structure**: Verify the directory structure in project-dna.md §1 matches the actual `src/user/` structure
  - Compare against Serena `get_symbols_overview` or Glob `src/user/**/*.py` results
- [ ] **Base class paths**: Verify all import paths in §2 match actual file locations
  - Confirm each path can import the class from the corresponding module
- [ ] **Generic types**: Verify signatures in §3 match current Base class definitions
  - Check `BaseRepositoryProtocol`, `BaseRepository`, `SuccessResponse` class definitions
- [ ] **CRUD methods**: Verify the `BaseRepositoryProtocol` method list in §4 is up to date
  - Serena `get_symbols_overview` → compare method lists
- [ ] **DI patterns**: Verify Singleton/Factory mappings in §5 match current `UserContainer` code
- [ ] **Conversion Patterns**: Verify `model_validate`/`model_dump` usage in §6 matches current implementation
- [ ] **Security tools**: Verify the tool list in §7 matches `pyproject.toml` and `.pre-commit-config.yaml`
  - In particular, check bandit skip list and flake8 ignore list
- [ ] **Active features**: Verify feature status in §8 is up to date
  - Use Grep to check whether imports for `jwt`, `UploadFile`, `RBAC`, `slowapi`, etc. exist
- [ ] **Inheritance chain**: Verify BaseRequest/BaseResponse parent classes in §2 are accurate
  - Check the `ApiConfig` → `BaseModel` chain

## 5. References ↔ Code Consistency Check

Inspect whether the content of each Skill's references/ files matches the current code.
(Sections referencing project-dna.md pointers are already verified in Section 4)

### Automated Verification (Glob/Grep-based — [AUTO-FIX] targets)

- [ ] **`new-domain` file list** (`scaffolding-layers.md`):
  - Exclude `__init__.py` from `Glob src/user/**/*.py` results
  - Extract `src/{name}/` paths from the numbered list (1~26) in scaffolding-layers.md
  - Replace `{name}` → `user` and compare both sides
  - On drift: suggest adding missing files to the appropriate Layer section, suggest removing deleted files

- [ ] **`test-domain` Factory patterns** (`test-patterns.md`):
  - Read `tests/factories/user_factory.py` and extract the function list (def lines)
  - Extract function signatures from code blocks in test-patterns.md
  - Compare function names/parameters/import paths for consistency
  - On drift: suggest updating code blocks based on user_factory.py

- [ ] **`plan-feature` Skill mapping** (`planning-checklists.md`):
  - Collect `name:` fields from each file via `Glob .claude/skills/*/SKILL.md`
  - Extract `/skill-name` entries from the "Mapped Skill" column in planning-checklists.md "3. Skill Mapping Table"
  - Compare both sets (additions/deletions/renames)
  - On drift: suggest adding/removing rows in the table

### Manual Inspection (Change-history-based — [REVIEW] targets)

- [ ] **`review-architecture` checklist** (`checklist.md`):
  - Count the items in CLAUDE.md's "Absolute Prohibitions" section (expected: 5) and compare against the number of related inspection items in checklist.md
  - On mismatch: confirm with the user whether Grep patterns need to be added for new rules

- [ ] **`security-review` security checklist** (`security-checklist.md`):
  - Extract the "active" feature list from project-dna.md §8
  - Extract the feature list from items marked `[when applicable]` in security-checklist.md
  - Check whether security inspection items exist for newly activated features
  - On uncovered features: confirm with the user whether security inspection items need to be added for those features
