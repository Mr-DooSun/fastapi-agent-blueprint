# Ticket Workflow

This is an on-demand operating contract for issue #427, adopted by
[ADR 060](../../history/060-ticket-session-boundaries-and-review-packets.md).
It makes no measured claim of lower review time, hallucination, or quota use.

## Work units and handoff

- **Epic**: a parent issue whose tickets share one approved Execution Packet.
- **Ticket**: one independently reviewable outcome, one PR, one worktree, one fresh
  execution session. Keep tightly coupled changes together; do not split merely
  to reduce line count. A resumed session for the same ticket is allowed.
- **Task**: a dependency-ordered step inside a ticket, not another tracking system.

Planning ends with the approved packet and native ticket sub-issues. Each ticket
brief is a projection of that packet, not a second implementation plan. Use the
[native issue template](../../../.github/ISSUE_TEMPLATE/ticket.yml).
A standalone ticket may carry its packet in its own body. The brief records:

1. Intent, explicit non-goals, observable done-when criteria.
2. Premises with code, test, issue, ADR, or runtime evidence pointers.
3. Parent packet/reference and approval evidence, predecessors, file set,
   Parallel Group, and Supervision L1/L2/L3 from
   [planning-checklists](planning-checklists.md#4-supervision-level-definitions).
4. Exact verification gates and review gates, including known unverified limits.

The human approves the brief and reviews the final diff at its risk depth.
Existing explicit approval remains valid; do not manufacture repeated approvals.
If GitHub write access is unavailable, emit the complete ticket bodies and report
that native publication remains pending; never pretend draft bodies are sub-issues.

Start `/execute-plan <ticket issue>` in a fresh session. Read the issue, its parent
packet, approval evidence, predecessors, and current PR/CI state. Try to falsify
its premises before editing, using the existence gate in
[fix-bug Phase 1](skills/fix-bug.md#phase-1-reproduce): distinguish observed,
inferred, and second-hand claims; a disproved premise needs a corrected contract,
not a speculative implementation. Check only relevant references, avoiding broad
repository rediscovery. Newly missing capability follows ADR 050.

Run sequentially by default. Parallel tickets require disjoint declared file sets,
no unresolved dependency, and available human review capacity. Discovery of overlap
returns the tickets to serial execution. No external orchestrator is introduced.

Issue scope and approval, PR diffs/reviews, and CI results are durable evidence.
Reconcile disagreements against the actual code and acceptance criteria; issue
closure or green CI alone does not prove success. The gitignored work ledger is
only local resumable state. Hydrate its existing fields from the approved ticket
before entering `executing`; keep ADR 054's explicit execute-plan boundary and
existing hooks. Do not make the ledger, or a stale SessionStart summary, the source
of approval or completion. No ledger schema change is needed.

## Review packet and depth

Run `uv run python tools/review_packet.py --base origin/main` on the final tracked diff
(stage new files first). It compares the merge-base of the base and HEAD with the
tracked working tree, including staged edits; unrelated base-tip commits are excluded.
The command reports changed files ranked by risk and
added/deleted counts; binary changes are high risk. It does not run verification.
The PR's first screen contains intent, derived risk + reasons, highest-risk files,
commands with concise observed output/exit status, and unverified limits. Put
supporting details below the collapsed section; keep the real Governor Footer
outside it. Never copy a template example as a test result.

Risk is a floor, independent of governor Tier A/B/C:

| Risk | Deterministic floor | Human review depth |
|---|---|---|
| High | Governor trigger, CI, migration, auth/security/credential path, binary diff | Read affected contracts and failure paths as well as the full diff |
| Medium | Runtime/build/dependency change, unknown file type, or total added+deleted >400 | Read the complete diff and verification evidence |
| Low | Only general documentation/assets/tests, at most 400 added+deleted | Inspect intent, focused diff, and relevant evidence |

A reviewer may raise risk with reasons. File names cannot prove the absence of
security or contract effects: discovered semantic risk raises the tier. Size never
lowers path risk, generated files are counted, and renamed/deleted paths are
examined on both sides. Existing mandatory security/architecture and governor
review obligations still apply.

Use one independent cross-vendor precision-filter round for implementation tickets
as specified in [review-protocol](review-protocol.md#7-independent-review--fallback).
Close known findings using verified evidence; do not start open-ended review loops.
Explicit full security/architecture audits retain their full severity coverage.
Fold guideline sync into the feature PR, before final review. Standalone sync PRs
are reserved for a release audit or independently discovered post-merge drift.
The merged-PR Footer audit in drift-checklist §1D runs at release; a feature PR
checks its own Footer and changed rules. This changes packaging, not sync quality.

## Measurement protocol

Use [ticket-metrics.csv](ticket-metrics.csv) as an empty collection schema. Unknown
values stay empty, never zero. One row per ticket; keep evidence URLs and sample
size. Record review rounds (including pre-PR rounds), distinct human corrections,
and post-merge fix-up PRs linked to the ticket within 14 calendar days. Zero
fix-ups is final only after that window, or record `observation_end` as censored.
A human correction is a distinct factual, scope, or behavior correction requiring
a change, not each message, clarification, preference, or repeated finding.

Human review active minutes require owner-provided start/stop intervals; exclude
breaks and machine waiting. Open-to-merge and CI durations are wait/lead-time
proxies only. Quota snapshots are optional manually recorded Claude `/usage` and
Codex usage-dashboard observations, with timestamp, plan/window, and overlapping
work noted. Session count or API prices do not measure subscription quota.

Compare a prospective sequential-ticket pilot with comparable historical tickets
by risk and size, disclosing non-random assignment and missing measurements.
Report medians, sample sizes, correction/fix-up counts, and censored windows;
small observational samples cannot establish causation. Decide whether to change
execution topology only after the owner reviews that evidence.

A transcript-derived owner-review/wait proxy is an investigation, not a result:
use an explicitly authorized, redacted sample; compare inferred intervals with
owner timings, record uncertainty, and discard the proxy if agreement is poor.
Do not collect transcripts automatically or treat silence as active review.

## Lightweighting follow-ups (#414)

Tier A changes do not establish Tier B safety or measured effectiveness. The
remaining work is explicitly **not implemented by this ticket**:

| Candidate | Execution packet prerequisite and done-when | Verification / rollback |
|---|---|---|
| B1 scoped rules | Keep layer-selection and cross-layer invariants unconditional; split conventions by repeated layer globs; fix Storage drift against container; move command reference, update language and cosmetic scopes | Measure unconditional bytes, link/language and hook tests; restore rule paths/config together |
| B2 verify hook removal | Preserve tokens, markers, safety, locale; remove all three adapters' call sites and update doctor C4/lifecycle coverage atomically | Full hook/doctor/lifecycle tests plus configured-command smoke; restore all call sites together |
| B3 generated inventory | Commit a path-to-bucket map; derive inventory tiers from matrix Verification scope, not governor review tiers; generated==committed gate | Filesystem completeness including Drop exceptions and counts; restore matrix+generator gate together |
| B4 archives | Move only migration/repo-facts and TOM A/C history; retain live TOM Appendix B Trace 2 and its consumers | Scan prose/backticks as well as links; revert moves and inbound links together |
| B5 project-dna | Block-level reductions, <=48 KB; retain §5 policy and §14 guardrails, section numbers/headings; verify each claimed derivable fact against code | All section consumers, language/link checks, byte measurement; restore blocks if conventions become undiscoverable |
| B6 wrapper generation | Keep every skill triple, required plan terms, legitimate tool-specific sync steps; preserve frontmatter and supported tools | Native workflow and cross-tool routing probes, generated==committed; restore wrappers+generator gate together |
| B8 security categories | Prove replacement coverage for each removed category; move logging rule into deterministic pygrep; keep code_safety while Antigravity consumes it | Real negative probes for all adapters and logging hook; restore previous safety rules together |
| B9 session summaries | Suppress only demonstrably stale completed state; preserve idle prompt-and-verify continuity and fix-bug records; no blanket idle suppression | Reproduce complete/idle/changed-files and worktree cases before behavior edits; restore summary predicate |

Each needs its own approved packet/native follow-up issue before implementation;
this table is a trackable backlog, not a claim that GitHub children were published.
B7 is implemented in this contract. Antigravity/Gemini removal remains a separate
owner product decision requiring ADR/product-promise changes. Do not perform the
three refuted removals in #414; keep doctor coverage, safe launcher behavior, and
review-protocol ownership. The parent audit can close only after its promised implementation and measurement
criteria are satisfied or explicitly re-scoped; this ticket alone does not establish that.
