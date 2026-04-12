---
name: add-cross-domain
argument-hint: "from:consumer to:provider"
description: |
  This skill should be used when the user asks to
  "cross-domain dependency", "wire domain dependency", "domain reference",
  "connect domains", "Protocol dependency",
  or needs to wire one domain to depend on another domain's data via Protocol-based DIP.
---

# Cross-Domain Dependency Wiring

Request: $ARGUMENTS (format: "from:{consumer} to:{provider}", e.g.: "from:order to:user")

## Procedure Overview
1. Analysis — identify consumer/provider, determine needed functionality
2. Implementation — verify provider Protocol → modify consumer Service → wire DI Container → verify app container
3. Verification — grep for prohibited imports, run tests for both domains

Read `docs/ai/shared/skills/add-cross-domain.md` for detailed steps and code templates.
Also refer to `docs/ai/shared/project-dna.md` §5 for DI patterns and §2 for base class paths.
