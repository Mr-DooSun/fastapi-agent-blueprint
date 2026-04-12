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

## Procedure Overview
1. Identify audit scope — file, domain, or all
2. Run 8-category security checklist — injection, auth, data protection, input validation, config, errors, worker, S3
3. Apply conditional checks — [Always] items run unconditionally, [When applicable] items check feature usage first
4. Report — severity-rated findings with file/line references and mitigations

Read `docs/ai/shared/skills/security-review.md` for detailed steps and output format.
Also refer to `docs/ai/shared/security-checklist.md` for the full checklist.
