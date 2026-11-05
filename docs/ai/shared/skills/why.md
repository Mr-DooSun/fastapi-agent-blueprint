# Why — Read-Only Decision Provenance

## Default Flow Position
See [target-operating-model §1](../target-operating-model.md) — `why` routing.

## Procedure

Use on demand for the reason behind an existing architectural or workflow choice.
Run in an isolated/forked context with read-only tools. Report unavailable isolation
as a limitation; never imply a new context existed when it did not.

Locate the relevant ADR from [the history index](../../../history/README.md), then
read its problem, alternatives, decision, and consequences. Verify accepted versus
superseded status and current implementation; follow issue/PR history only when
needed to answer the question. Commit messages establish recorded intent, not
proof of a runtime effect. Distinguish contemporaneous evidence from a retroactive ADR.

Return: the original problem, alternatives actually considered, recorded trade-off,
current constraints, and evidence links/`file:line` citations. Separate recorded
reason, present behavior, and inference; say when intent is unavailable or code has
drifted. Do not invent a rationale to defend the current design. Do not edit,
rewrite history, prescribe a redesign, or update workflow state.

Removal budget: replaces onboard Phase 1.2's four scripted history stories.
Onboarding retains its required structural/DTO/layer/DI topics and uses source-based
explanations adapted to the contributor rather than a fixed retrospective narrative.
