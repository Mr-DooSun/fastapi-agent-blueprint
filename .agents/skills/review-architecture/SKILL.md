---
name: review-architecture
description: Audit a domain or the full repository for architecture compliance using the shared architecture checklist and repository rules.
metadata:
  short-description: Architecture compliance audit
---

# Review Architecture

## Default Flow Position
See [target-operating-model §1](../../../docs/ai/shared/target-operating-model.md) — `review-architecture` routing.
Recursion guard: Do not invoke this skill recursively or invoke plan-feature from inside it.

## Procedure
1. Read `AGENTS.md` and `docs/ai/shared/skills/review-architecture.md` for the full procedure.
2. Read `docs/ai/shared/architecture-review-checklist.md` and `docs/ai/shared/project-dna.md` as the shared architecture rule sources.
3. Resolve the audit target and load the shared rule sources (Phase 0).
4. Audit the target against the 10 architecture checklist categories (Phase 1).
5. Determine `Drift Candidates` and whether `Sync Required` is `true` or `false` (Phase 2).
6. Report using the protocol output contract: `Scope`, `Effect Answer`, `Sources Loaded`, `Findings` (open only), `Coverage` (OK/SKIP), `Drift Candidates`, `Verdict: N/A (audit-only scope)`, `Next Actions`, `Completion State`, `Sync Required` (Phase 3). `Effect Answer` is mandatory — see `docs/ai/shared/review-protocol.md` §3 for the contract and Guard H context.

For cross-tool review prompts, use the `Cross-Tool Review Prompt Template`
section in `docs/ai/shared/skills/review-architecture.md`; do not duplicate it here.
