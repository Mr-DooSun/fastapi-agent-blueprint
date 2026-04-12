---
name: security-review
description: Review a domain, file, or the full repository for OWASP-oriented security issues using the shared security checklist.
metadata:
  short-description: OWASP security audit
---

# Security Review

1. Read `AGENTS.md`, `docs/ai/shared/project-dna.md`, and `docs/ai/shared/security-checklist.md`.
2. Choose the scope: file, domain, or all.
3. Run the shared checklist with conditional checks only when the related feature is actually in use.
4. Focus on:
   - injection risk
   - auth and authorization gaps
   - sensitive data exposure
   - input validation
   - config and dependency safety
   - error handling and logging
   - worker and object storage security where applicable
5. Report file and line references, severity, and concrete mitigations.
