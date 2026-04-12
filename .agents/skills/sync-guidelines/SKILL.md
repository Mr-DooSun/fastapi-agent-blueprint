---
name: sync-guidelines
description: Inspect drift between code, shared workflow references, and Claude or Codex harness assets after architecture or workflow changes.
metadata:
  short-description: Sync shared guidelines
---

# Sync Guidelines

1. Read `AGENTS.md`, `docs/ai/shared/project-dna.md`, and `docs/ai/shared/drift-checklist.md`.
2. Compare code against:
   - `AGENTS.md`
   - `README.md`
   - `docs/README.ko.md`
   - `CONTRIBUTING.md`
   - `CLAUDE.md`
   - `.codex/config.toml`
   - `.codex/hooks.json`
   - `.agents/skills/`
3. Use `src/user/` as the reference domain for current patterns.
4. Report drift clearly, then update the affected docs or workflow assets.
5. After updates, re-run the inspection until major drift is gone.
