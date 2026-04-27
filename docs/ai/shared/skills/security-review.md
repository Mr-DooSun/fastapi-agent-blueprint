# Security Quality Gate Audit

## Default Flow Position

This skill participates in the [Default Coding Flow](../../../../AGENTS.md#default-coding-flow) at the **`self-review`** step.

It is invoked when the change touches security-sensitive surfaces: authentication, password handling, token issuance, sensitive-field exposure (admin pages, logs), file upload, external request handling, or migration of credentials.

After self-review, route to:
- `completion gate` — `/sync-guidelines` if drift candidates were detected, otherwise `/review-pr`

Recursion guard: do **not** invoke `/security-review` recursively, and do not invoke `/plan-feature` from inside this skill.

## Purpose

Use this skill to audit a file, domain, or the full repository for security
issues, while also checking whether shared references such as `project-dna` and
the security checklist are stale.

## When to Use

Run this skill whenever a change touches one or more of the following surfaces:

- Authentication, authorization, or session management
- Secrets, API keys, or credential handling
- Logging, structured log fields, or error responses
- Object storage (S3/MinIO), DynamoDB, or S3 Vectors
- AI providers (LLM, Embedding)
- Async workers or task payloads
- Any other security-sensitive surface

Also run when the user explicitly asks for a security audit.

## Review Contract

Every result must include:

- `Scope` - audit target, audited domains/files, important exclusions
- `Sources Loaded` - exact shared rule sources used for the audit
- `Findings` - only open issues; each item includes `severity`, `rule source`,
  `file:line`, `impact`, and `recommended fix`
- `Drift Candidates` - shared docs, checklists, wrappers, or `project-dna`
  targets that may need sync; each item includes `target`, `reason`,
  `auto-fix`, and `sync-required`
- `Next Actions` - remediation, verification, sync path
- `Completion State` - concise closure status for the audit
- `Sync Required` - explicit `true` or `false`

### Severity Taxonomy

- Review state: `OPEN`, `OK`, `SKIP`
- Severity: `BLOCKING`, `HIGH`, `MEDIUM`, `LOW`, `NOTE`

## Audit Target

- `all` -> audit all directories under `src/`, including `_core` and `_apps`
- `{domain}` -> audit only `src/{domain}/`
- `{file}` -> audit only that file

## Category Coverage

Inspect the 12 security checklist categories defined in
`docs/ai/shared/security-checklist.md`.

1. Injection Prevention
2. Authentication & Authorization
3. Data Protection
4. Input Validation
5. Dependencies & Configuration
6. Error Handling & Logging
7. Async Worker Security (Taskiq)
8. Object Storage Security (AWS S3)
9. DynamoDB Security
10. S3 Vectors Security
11. Embedding API Security
12. LLM API Security

## Phase 0: Feature Detection and Reference Freshness Preflight

Before the main audit, compare shared references against live code.

1. Load:
   - `AGENTS.md` — including § Language Policy. Hidden non-English rationale
     (HTML comments, encoded payloads, attribute values, metadata) in Tier 1
     paths is a security-adjacent governance risk; surface as a `Findings`
     violation with `Sync Required: true` if encountered during audit.
   - `docs/ai/shared/project-dna.md`
   - `docs/ai/shared/security-checklist.md`
2. Build a feature snapshot from `project-dna` section 8.
3. Re-detect the same features directly from code imports and wiring.
4. If the live code disagrees with `project-dna`, or `project-dna` is stale for
   the current security surface, continue the audit but add a
   `stale reference risk` drift candidate with `sync-required: true`.

Live code is authoritative. `project-dna` is a cached shared reference, not the
final source of truth.

## Phase 1: Run the 12-Category Audit

Each checklist item is either `Always` or `When applicable`.

Use a two-step applicability decision:
1. preflight expectation from `project-dna`
2. live code re-detection before deciding `SKIP`

Rules:
- if both sources say inactive -> `SKIP`
- if code says active -> audit as active, even if `project-dna` says inactive
- if code says inactive but `project-dna` says active -> note the drift and use
  judgment on whether the feature was removed or merely hard to detect

Include file and line references for every open issue and filter out false
positives from tests, comments, or config examples.

## Phase 2: Determine Drift Candidates and Sync Requirement

Mark `Sync Required: true` when:
- preflight detects stale or conflicting feature status
- the audit exposes a new active feature without matching checklist coverage
- the audited changes touch shared references, checklist files, or wrappers
- the audit finds code that is secure but no longer described correctly in
  `project-dna` or the checklist

Security review does not stop at `SKIP`. A stale shared reference is itself a
quality gate issue and must be reported.

## Phase 3: Report Using the Review Contract

Example:

```text
Scope
- Target: all
- Audited domains: docs, user, _core

Sources Loaded
- AGENTS.md
- docs/ai/shared/project-dna.md
- docs/ai/shared/security-checklist.md

Findings
- [OPEN][BLOCKING] Security checklist - src/user/interface/server/routers/user_router.py:19
  Impact: write endpoint has no authentication dependency and is exposed to unauthenticated callers.
  Recommended fix: add the project's auth dependency before allowing create/update/delete actions.
- [OK][BLOCKING] Security checklist §2 - Admin dashboard: require_auth() present in all @ui.page handlers
- [SKIP] Security checklist §4.2 - File Upload input validation: project-dna §8 and live code both confirm feature inactive

Drift Candidates
- target: docs/ai/shared/project-dna.md
  reason: code uses UploadFile validation paths, but section 8 still reports file upload as not implemented.
  auto-fix: yes
  sync-required: true
- target: docs/ai/shared/security-checklist.md
  reason: active LLM usage exists but the applicable checklist wording is stale.
  auto-fix: no
  sync-required: true

Next Actions
- Fix the endpoint authentication gap.
- Run `/sync-guidelines` to refresh feature status and checklist wording.

Completion State
- complete with findings

Sync Required
- true
```

When there are no security findings, still emit all sections. In particular, do
not omit `Drift Candidates` or `Sync Required`.
