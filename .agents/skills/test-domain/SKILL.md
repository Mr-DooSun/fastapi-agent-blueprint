---
name: test-domain
description: Generate or run tests for a domain using the repository's established factory, unit, integration, and admin test patterns.
metadata:
  short-description: Generate or run domain tests
---

# Test Domain

1. Read `docs/ai/shared/project-dna.md` and `docs/ai/shared/test-patterns.md`.
2. Decide whether the request is generate mode or run mode.
3. In generate mode:
   - inspect the domain's Service, UseCase, Router, and worker/admin surfaces
   - compare existing tests to the shared required file set
   - generate only missing tests following the reference patterns
4. In run mode, execute the relevant pytest scope and analyze failures.
5. Keep factories and test names aligned with the shared test pattern file.
