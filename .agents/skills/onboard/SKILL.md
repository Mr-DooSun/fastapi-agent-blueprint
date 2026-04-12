---
name: onboard
description: Interactive onboarding for contributors who are new to this repository or need a guided refresher on architecture, workflow, and AI collaboration assets.
metadata:
  short-description: Guided repository onboarding
---

# Onboard

1. Read `AGENTS.md`, `docs/ai/shared/repo-facts.md`, `docs/ai/shared/project-dna.md`, `README.md`, and ADRs `020`, `021`, `031`, `032`.
2. Ask the user for experience level and preferred format only if they did not already indicate it.
3. Use `src/user/` as the reference domain and `src/_core/`, `src/_apps/` for shared infrastructure.
4. Adapt depth using `docs/ai/shared/onboarding-role-tracks.md`.
5. Cover, in order:
   - why this architecture exists
   - how Router/Service/Repository and optional UseCase work
   - absolute prohibitions and conversion patterns
   - workflow entrypoints for Claude and Codex
   - next practical steps for the user's level
6. When context feels too abstract, point to concrete files under `src/user/`.

Do not invent architecture rules. Use shared docs as the source of truth.
