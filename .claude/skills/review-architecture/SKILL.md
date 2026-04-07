---
name: review-architecture
argument-hint: domain_name or all
description: |
  Audit architecture compliance for a domain.
  Use when the user asks to "review architecture", "compliance audit",
  or wants to check if a domain follows project architecture rules.
---

# Architecture Compliance Audit

Target: $ARGUMENTS (domain name or "all")

## Audit Target
When "all", audit all domain directories under `src/` (excluding `_core`, `_apps`).
When a specific domain name, audit only `src/{name}/`.

## Current Domain List
Identify domains using Glob pattern `src/*/` and exclude `_core`, `_apps` prefixes

## Audit Procedure

Inspect 6 categories with 20+ items using Grep-based checks.
Refer to `${CLAUDE_SKILL_DIR}/references/checklist.md` for the detailed checklist.

**Category Summary**:
1. **Layer Dependency Rules** — domain -> infrastructure/interface import violations
2. **Conversion Patterns Compliance** — Mapper class, Entity pattern remnants
3. **DTO/Response Integrity** — sensitive field exposure
4. **DI Container Correctness** — Singleton/Factory distinction
5. **Test Coverage** — required test file existence
6. **Bootstrap Wiring** — app-level registration status

## Output Format

```
[PASS] Layer dependency: no domain -> infrastructure imports found
[FAIL] Test coverage: tests/unit/{name}/domain/test_{name}_service.py missing
       -> Recommended: generate with `/test-domain {name} generate`
```

Final summary: `Passed: XX/20 | Failed: XX/20`

## Recommended Actions on Failure
- Layer dependency violation -> Refactor to Protocol-based approach
- Conversion Patterns violation -> Replace with inline conversion (model_dump, model_validate)
- Missing tests -> Run `/test-domain {name} generate`
- Bootstrap not registered -> Refer to Layer 5 in `/new-domain` reference
