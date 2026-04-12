---
name: add-cross-domain
description: Wire one domain to another using Protocol-based dependency inversion instead of direct implementation imports.
metadata:
  short-description: Add cross-domain dependency
---

# Add Cross Domain

1. Read `AGENTS.md` and `docs/ai/shared/skills/add-cross-domain.md` for the full procedure.
2. Read `docs/ai/shared/project-dna.md` for DI patterns and base class paths.
3. Identify the consumer and provider domains plus the exact capability needed.
4. Verify or extend the provider Protocol and Repository first.
5. Inject the provider Protocol into the consumer Service via DI Container.
6. Reject anti-patterns: Domain importing Infrastructure, Service-to-Service deps, Mapper layers.
7. Verify the final dependency direction with grep or tests.
