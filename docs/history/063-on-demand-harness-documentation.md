# 063. Consult Detailed References on Demand

- Status: Accepted
- Date: 2026-11-06
- Issue: [#414](https://github.com/Mr-DooSun/fastapi-agent-blueprint/issues/414) (B1, B4, B5)
- Related: [ADR 045](045-hybrid-harness-target-architecture.md), [ADR 047](047-governor-review-provenance-consolidation.md), [ADR 051](051-runtime-llm-guardrails.md)

## Context

Fixed context grew through copied command examples, migration history and source-derived catalogs. Reducing lines alone did not constrain bytes. The shared policy remains useful, while a complete import table or old phase checklist is more accurately obtained from its owning source when needed.

Moving a rule file also changes a governance boundary: ADR 047 D4 exempted timestamp-only updates to the auto-loaded command projection. That exemption must not follow a consulted shared reference merely because its basename is unchanged.

## Decision

1. Move the shell command reference to [shared commands](../ai/shared/commands.md). All tools consult it as needed. Path-scoped architecture and project overview rules remain Claude projections; shared policy stays in AGENTS and project-dna.
2. Remove both the obsolete `.claude/rules/commands.md` path and its relocated shared destination from the sync-cosmetic carve-out. Only the remaining project-status / project-overview cosmetic cases qualify. This narrows ADR 047 D4; no historical ADR047-G slot is rewritten.
3. Archive historical migration / repository-facts prose and TOM Appendices A/C. Keep live navigation stubs and update current consumers to their actual authority. Appendix B's sample workflows remain live; the fix-bug skill relies on Trace 2.
4. Keep project-dna as a policy and source-navigation reference, at most 48 KiB. Replace derivable blocks with links to their source; retain original section numbers/headings, the non-derivable §5 provider-lifetime policy, and §14 guardrail policy. Preserve removed examples once as a historical snapshot with relative links repaired.
5. Current sources take precedence over historical snapshots. Snapshots preserve evidence, not new policy, and are not required reading on every sync. Routine provenance belongs in git, CHANGELOG and the PR body.

## Consequences

- **ADR063-G1 — Source ownership:** consulted commands live in shared documentation; path-scoped projections do not become new canonical homes. A relocation never silently extends the cosmetic exemption.
- **ADR063-G2 — Stable policy anchors:** project-dna § numbers and headings, §5 provider policy and §14 guardrail invariants survive block-level compression. New source-derived catalogs should be pointers; real markdown anchors replace new free-text section references where practical.
- **ADR063-G3 — Archive boundaries:** historical migration notes and implementation examples do not govern current adapters. Appendix B remains a live contract. Archives retain per-source provenance, repaired links and original text; no routine archive writer is introduced.

The first migration also fixes confirmed drift: aggregate read contracts omitted `count_datas_by_day`; the LLM DI narrative instructed domain Services to construct SDK Agents despite ADR 043; the audit-log description still claimed an actor foreign key removed by ADR 057. Storage Selection's claim that no Selector exists was also stale against CoreContainer. These are documentation corrections, not runtime changes.

## Verification

- Meaningful regression tests cover the removed cosmetic exemption, scoped loading, retained policy/guardrail blocks and live sample workflows.
- Archive preservation is checked against the source snapshot, allowing only repaired relative links and explicit archival provenance.
- Documentation links, Tier 1 language policy, project-dna byte size and existing native-workflow / worktree-hook contracts remain verification gates.

Scope regression cases exercise every declared simple glob with positive and negative samples using Python fnmatch. They are smoke tests, not a measurement of Claude Code's native matcher; native matcher behaviour remains an explicitly unverified limit.
