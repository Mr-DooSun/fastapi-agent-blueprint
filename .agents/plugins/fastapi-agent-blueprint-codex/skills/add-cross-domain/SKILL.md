---
name: add-cross-domain
description: Wire one domain to another using Protocol-based dependency inversion instead of direct implementation imports.
metadata:
  short-description: Add cross-domain dependency
---

# Add Cross Domain

1. Read `AGENTS.md` and `docs/ai/shared/project-dna.md`.
2. Identify the consumer and provider domains plus the exact provider capability needed.
3. Verify or extend the provider Protocol and Repository implementation first.
4. Inject the provider Protocol into the consumer Service.
5. Perform concrete implementation wiring only inside DI Container code.
6. Reject these anti-patterns:
   - consumer Domain importing provider Infrastructure
   - Service-to-Service direct dependency
   - new Mapper or Adapter layers for simple DTO movement
7. Verify the final dependency direction with grep or tests.
