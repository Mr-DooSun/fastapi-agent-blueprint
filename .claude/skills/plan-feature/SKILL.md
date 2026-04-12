---
name: plan-feature
argument-hint: feature description
description: |
  This skill should be used when the user asks to
  "plan feature", "design feature",
  or wants to plan and design a new feature before implementation.
---

# Feature Implementation Planning

Description: $ARGUMENTS

## Preparation

1. Read `.claude/rules/architecture-conventions.md` -- confirm current DO/DON'T rules
2. Read `.claude/rules/project-status.md` -- confirm work currently in progress
3. Read `.claude/rules/project-overview.md` -- confirm tech stack and structure
4. Identify current domain list: use Glob pattern `src/*/` and exclude `_core`, `_apps` prefixes

## Phase 0: Requirements Interview

Ask the user 3-5 questions from the following categories.
Refer to the "Question Bank" in `docs/ai/shared/planning-checklists.md`, but select questions appropriate for the feature.

**Required question categories**:
1. **Data Model** -- What are the core entities and fields?
2. **Business Rules** -- Are there validation/constraint requirements?
3. **User Types** -- Who uses this feature? (Authentication required?)
4. **External Integrations** -- External APIs, file storage, message queues?
5. **Async Processing** -- Are there tasks requiring immediate response vs. background processing?

After receiving user responses, organize the following:
- [ ] Functional requirements checklist
- [ ] Non-functional requirements (performance, security, scalability)
- [ ] Identified edge cases

## Phase 1: Architecture Impact Analysis

### 1.1 Layer Impact Analysis
Determine whether changes/additions are needed for each layer:
- **Domain**: New DTO, Protocol, Service, Exception needed?
- **Application**: New UseCase method needed? Existing UseCase modification?
- **Infrastructure**: New Model, Repository, DI Container needed? DB migration?
- **Interface**: New Router, Request/Response DTO, Worker Task needed?

### 1.2 Domain Impact Analysis
- Is modifying existing domains sufficient? -> Which layer of which domain?
- Is a new domain needed? -> Suggest domain name with rationale
- Search related existing code

### 1.3 DTO Decision
Decide based on the Write DTO criteria in `AGENTS.md`:
- Request fields == Domain fields? -> No separate DTO needed, pass Request directly
- Request fields != Domain fields? -> Separate Create/Update DTO needed, location: `application/` or `domain/dtos/`

### 1.4 Cross-Domain Dependencies
- Does the new feature reference data from existing domains?
- Is Protocol-based DIP needed? -> Apply `/add-cross-domain` pattern

## Phase 2: Security Checkpoint

Evaluate 6 items according to the "Security Assessment Matrix" in `docs/ai/shared/planning-checklists.md`:

| Item | Applicable | Required Action |
|------|-----------|----------------|
| Authentication/Authorization | Y/N | |
| Payment Processing | Y/N | |
| Data Mutation (CUD) | Y/N | |
| External API Integration | Y/N | |
| Sensitive Data (PII) | Y/N | |
| File Upload/Download | Y/N | |

Derive specific security requirements for any applicable items.
**If 1 or more items apply**: Confirm security requirements with the user before proceeding to the next Phase.

## Phase 3: Task Breakdown

### 3.1 Task Identification
Break down Phase 1 analysis results into actionable task units.
Map each task to an existing Skill (refer to the "Skill Mapping Table" in `docs/ai/shared/planning-checklists.md`):

| Task Type | Mapped Skill | Example |
|-----------|-------------|---------|
| New domain creation | `/new-domain {name}` | `/new-domain order` |
| Add API endpoint | `/add-api {desc}` | `/add-api "add POST /orders to order"` |
| Add async task | `/add-worker-task {domain} {task}` | `/add-worker-task order send_notification` |
| Cross-domain connection | `/add-cross-domain from:{a} to:{b}` | `/add-cross-domain from:order to:user` |
| Test generation | `/test-domain {domain} generate` | `/test-domain order generate` |
| Architecture verification | `/review-architecture {domain}` | `/review-architecture order` |
| **Not mappable** | Manual implementation | External API integration, custom middleware, etc. |

### 3.2 Supervision Level Determination
For each task (refer to "Supervision Level Definitions" in `docs/ai/shared/planning-checklists.md`):
- **L1 (AI Delegation)**: 100% mapped to existing Skill, pattern is clear
- **L2 (Confirm then Delegate)**: Business logic decisions, new domain field composition, etc.
- **L3 (Supervision Required)**: Security-related, payment processing, external API integration, DB design decisions

### 3.3 Execution Order and Parallelization
- Create dependency graph (which tasks must precede others)
- Identify task groups that can be executed in parallel
- Identify the critical path

## Output: Feature Implementation Plan

Organize the results of Phases 0-3 above in the following format and present to the user
(refer to the "Output Plan Template" in `docs/ai/shared/planning-checklists.md`):

```
# Feature Implementation Plan: {Feature Name}

## 1. Requirements Summary
(Phase 0 results)

## 2. Architecture Impact Analysis
(Phase 1 results -- per-layer change table)

## 3. Security Assessment
(Phase 2 results -- security matrix table)

## 4. Execution Task List
| # | Task | Skill | Supervision Level | Preceding Tasks | Parallel Group |
|---|------|-------|--------------------|-----------------|----------------|
(Phase 3 results)

## 5. Execution Order
(Dependency graph in text representation)

## 6. Verification Plan
- Run /review-architecture {domain}
- Run /test-domain {domain} generate -> run
- Run full pre-commit
```

## After Plan Approval

When the user approves the plan:
1. Suggest executing from the first task in order
2. Guide the corresponding Skill before each task execution
3. Request user confirmation before executing "L3 Supervision Required" tasks
