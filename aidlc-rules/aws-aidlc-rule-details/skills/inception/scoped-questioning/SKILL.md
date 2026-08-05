---
name: tp-ai-kit-scoped-questioning
description: Interview the user one topic at a time until requirements, contracts, trade-offs, and edge cases are explicit enough to proceed safely. Use when a plan, API spec, event schema, technical design, or implementation task is still ambiguous. Triggers on "clarify this", "interview me", "grill me on", "what do we still need to decide", or whenever hidden assumptions remain before planning or coding starts.
disable-model-invocation: true
category: cross-cutting
sdlc_phase: any
status: stable
owner: platform-ai-team
tags: [cross-cutting, questioning, requirements, clarification]
supported_agents:
  - cursor
  - copilot
  - claude-code
requires_agents: false
security_reviewed: false
last_reviewed: "2026-06-13"
skill_card: ./SKILL_CARD.md
metadata:
  internal: false
---

# Scoped Questioning

Use this skill when a plan, requirement, API contract, event schema, or technical design still has open assumptions. The goal is not to ask more questions for its own sake — it is to surface hidden decisions before the wrong choice gets built.

## Core loop

1. Identify the single highest-risk unknown.
2. Check whether the repo, prior artifacts, or existing docs already answer it.
3. If not, ask one focused question.
4. Offer 2–3 concrete options with trade-offs and a recommended default.
5. Record the decision and move to the next unresolved branch.
6. Stop only when the design tree is covered well enough to proceed safely.

## Rules

- Ask **one major topic at a time**. Do not front-load a list of questions.
- **Repo-first answers.** If the codebase, planning docs, or standards already answer the question, use that evidence instead of asking the user.
- When asking, always provide 2–3 concrete options with trade-offs and a recommended default.
- Walk the design tree **branch by branch**. Resolve prerequisite decisions before dependent ones.
- Keep going until the user explicitly confirms the area is clear, or approves the alignment document.
- If the user wants to move on early, call out the most important remaining unknown and why it matters.

## Recommended answer pattern

```markdown
Question: Which auth model should this endpoint use?

Options:
- Option A: Reuse the existing JWT permission model. Best for consistency and lowest delivery risk.
- Option B: Project-scoped permission check only. Simpler, but easier to drift from the existing security pattern.
- Option C: New role model. Most flexible, highest rollout and testing cost.

Recommendation: Option A — unless there is a concrete requirement the existing permissions cannot express.
```

## Topics to cover

Cover only what is relevant. Do not force irrelevant categories.

- Problem and success criteria
- In-scope vs out-of-scope boundaries
- Users, actors, and permissions
- Acceptance criteria and failure modes
- API contract: paths, methods, auth, validation, pagination, versioning, error model, backward compatibility
- Event contract: payload fields, ordering, idempotency, retries, DLQ behavior, schema evolution
- Data model and migration concerns
- Performance and scale expectations
- Security and compliance constraints
- Testing expectations and evidence required
- Rollout, rollback, and feature-flag strategy

## Use by workflow

### PRD or requirements work

Clarify goals, acceptance criteria, edge cases, out-of-scope, and test expectations. Keep asking until the user confirms the requirements feel complete.

### API spec work

Focus on contract decisions that materially affect clients:
- auth and versioning
- idempotency and pagination
- error envelopes and backward compatibility

Do not advance to approval while any of those remain unclear.

### Technical design work

Focus on design decisions that have implementation consequences:
- component boundaries and dependencies
- data access patterns and storage choices
- async vs sync processing
- failure mode handling and retry strategy

### Implementation alignment (feature-developer Step 0)

The `feature-developer` skill uses this skill in Phase 3 of Step 0 — grounded in a prior codebase analysis. In that context:

- State what the code analysis already found; ask only what the code could not answer.
- Anchor every option to real patterns found in the repo: "Option A follows the pattern in `FooService.getBar()`."
- Surface edge cases from the analysis as concrete questions, not generic prompts.
- Produce a short `task-{id}-alignment.md` capturing every resolved decision and the agreed implementation scope.

## Output on completion

When all open questions are resolved, summarize what was decided:

```markdown
## Decisions agreed

| Topic | Decision | Rationale |
|-------|----------|-----------|
| Auth model | JWT (Option A) | Consistent with existing pattern |
| Pagination | Cursor-based `nextToken` | Matches existing list endpoints |
| Error on missing resource | 404 with structured error body | Standard across all endpoints |
```

Offer to write this as a `task-{id}-alignment.md` when used inside the `feature-developer` workflow.
