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

## Procedure Overview
1. Identify audit target — single domain or all domains
2. Run 8-category checklist — layer deps, conversions, DTO integrity, DI, tests, worker, admin, bootstrap
3. Report — PASS/FAIL per item with recommended actions

Read `docs/ai/shared/skills/review-architecture.md` for detailed steps and output format.
Also refer to `docs/ai/shared/architecture-review-checklist.md` for the full checklist.
