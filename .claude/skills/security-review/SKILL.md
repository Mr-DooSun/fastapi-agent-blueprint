---
name: security-review
argument-hint: "domain_name, file_path, or all"
description: |
  OWASP-based code security audit for a domain or file.
  Use when the user asks to "security review", "security audit", "OWASP check",
  or wants to audit code security for a domain or file.
---

# OWASP-Based Code Security Audit

Target: $ARGUMENTS (domain name, file path, or "all")

## Audit Target
- When "all", audit all directories under `src/` (including `_core`, `_apps`).
- When a specific domain name, audit only `src/{name}/`.
- When a file path, audit only that file.

## Current Domain List
Identify domains using Glob pattern `src/*/` (include all directories)

## Audit Procedure

Inspect 6 security categories with 24+ items using Grep-based checks.
Refer to `${CLAUDE_SKILL_DIR}/references/security-checklist.md` for the detailed checklist.

**Category Summary**:
1. **Injection Prevention** — SQL, Command, Template injection patterns
2. **Authentication & Authorization** — endpoint protection, credential management, JWT, RBAC
3. **Data Protection** — PII exposure, sensitive data in logs, encryption
4. **Input Validation** — Pydantic validation, file uploads, Path Traversal
5. **Dependencies & Configuration** — vulnerable packages, debug mode, CORS, secret management
6. **Error Handling & Logging** — stack trace exposure, Rate Limiting

## Audit Execution Method

Each checklist item is classified as `[Always]` or `[When applicable]`:

### Conditional Check Procedure
1. `[Always]` items: Execute Grep check unconditionally
2. `[When applicable]` items: First verify detection conditions (import/usage of the feature) via Grep
   - Feature not in use -> Output `[SKIP]` and skip
   - Feature in use -> Proceed with detailed check
3. False positive filtering — exclude test code, comments, config examples
4. Include specific file/line information for discovered issues
5. Severity indicators: [CRITICAL], [HIGH], [MEDIUM], [LOW]

## Output Format

```
=== OWASP Code Security Audit Results ===

--- 1. Injection Prevention ---
[PASS] SQL injection: no f-string SQL patterns found
[FAIL][HIGH] Command injection: subprocess.call(shell=True) detected
     -> File: src/example/infrastructure/services/export_service.py:42
     -> Recommended: use subprocess.run(shell=False) + shlex.split()

--- 2. Authentication & Authorization ---
[PASS] No hardcoded credentials found
[FAIL][CRITICAL] Missing endpoint authentication: POST /user has no auth dependency
     -> File: src/user/interface/server/routers/user_router.py:19
     -> Recommended: add Depends(get_current_user)

...

=== Summary ===
Passed: XX/24 | Failed: XX/24 | Skipped: XX/24
  - CRITICAL: X issues
  - HIGH: X issues
  - MEDIUM: X issues
  - LOW: X issues
  - SKIP: X items (feature not in use)
```

## External Tool Integration (Optional)
Run additionally if the tool is installed:
```bash
# Python security static analysis
bandit -r src/{name}/ -f json 2>/dev/null || echo "bandit not installed"

# Dependency vulnerability scan
pip audit 2>/dev/null || uv pip audit 2>/dev/null || echo "audit tool not installed"
```

## Recommended Actions on Failure
- Injection -> parameterized query, shell=False, Jinja2 autoescape
- Missing authentication -> add Depends(get_current_user) or RBAC middleware
- PII exposure -> apply model_dump(exclude={'password', ...})
- Hardcoded secrets -> migrate to Settings class (environment variables)
- CORS wildcard -> restrict to specific origins in production
- Stack trace exposure -> verify is_dev condition (generic_exception_handler in exception_handlers.py)
