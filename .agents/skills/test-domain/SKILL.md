---
name: test-domain
description: Generate or run tests for a domain using the repository's established factory, unit, integration, and admin test patterns.
metadata:
  short-description: Generate or run domain tests
---

# Test Domain

1. Read `docs/ai/shared/skills/test-domain.md` for the full procedure.
2. Read `docs/ai/shared/test-patterns.md` for factory patterns and test examples.
3. Decide whether the request is generate mode or run mode.
4. In generate mode: inspect the domain, compare existing tests to required file set, generate missing ones.
5. In run mode: execute the relevant pytest scope and analyze failures.
6. Keep factories and test names aligned with the shared test pattern file.
