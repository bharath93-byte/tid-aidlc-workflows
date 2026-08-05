---
name: tp-ai-kit-delivery-planning
description: Turn PRDs, technical designs, API specs, and ADRs into agent-ready implementation plans with numbered units (U-IDs), explicit dependencies, parallel vs sequential execution groups, and epic split recommendations. Use when breaking work into reviewable PR-sized units before implementation. Triggers on /tp-ai-kit-delivery-planning, "break this into implementation units", "create a delivery plan from this PRD", or "task breakdown for this feature".
disable-model-invocation: true
category: sdlc-planning
sdlc_phase: planning
status: stable
owner: platform-ai-team
tags: [planning, delivery, breakdown, tasks]
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

# Delivery Planning

**Announce at start:** "I'm creating a **delivery plan** for **`{feature}`**."

Convert planning artifacts into a **non-ambiguous, agent-ready** implementation plan. This skill **writes plans only** — it does not create Jira tickets (use `tp-ai-kit-jira-work-breakdown` after the plan is approved).

## Prerequisites

- `sdlc-core` installed in the same project; read the `tp-ai-kit-scoped-questioning` skill (Cursor: `.cursor/skills/tp-ai-kit-scoped-questioning/SKILL.md`; Copilot: `.github/skills/tp-ai-kit-scoped-questioning/SKILL.md`) to apply its interview pattern in Phase 2
- Inputs: at least one of PRD, TDD, OpenAPI spec, or explicit user requirements

## Inputs (repo-first)

| Input | Typical path |
| --- | --- |
| PRD | `docs/plans/{feature}/PRD.md` or user-provided path |
| TDD | `docs/plans/{feature}/technical-design.md` or `docs/architecture/designs/TDD-*.md` |
| API spec | `openapi.yaml`, `kb/services/*/openapi.yaml`, or linked spec |
| ADRs | `docs/architecture/decisions/` |
| User override | "single epic", scope cuts, deadline constraints |

Read existing artifacts before asking questions. Use scoped-questioning for **blocking** gaps only.

## Output

Write to:

```text
docs/plans/YYYY-MM-DD-NNN-<type>-<descriptive-name>-plan.md
```

- `NNN`: next sequence for the date (001, 002, …)
- `type`: `feat`, `fix`, or `refactor`
- Include YAML frontmatter: `status: active`, `date`, `type`, optional `origin:` path

## Workflow

### Phase 1 — Ingest

1. Load PRD, TDD, API spec, relevant ADRs
2. Extract requirements (assign R1, R2, … if not already IDed)
3. Note scope boundaries and non-goals from PRD

### Phase 2 — Clarify (blocking only)

Apply scoped-questioning **one topic at a time** when:

- Auth, versioning, or migration strategy is unspecified and affects unit boundaries
- Acceptance criteria conflict across documents
- User has not stated whether work spans multiple epics/products

Stop clarifying when the user confirms or explicitly accepts documented assumptions.

### Phase 3 — Decompose into units

Each unit **U1, U2, …** must be:

- **One PR-sized** slice (typically one logical commit / one reviewable PR)
- **Independently verifiable** with explicit test scenarios
- Assigned a **stable U-ID** (never renumbered; gaps OK after deletion)

Per unit include:

- **Goal** — one sentence
- **Requirements** — which R-IDs this advances
- **Dependencies** — U-IDs only (e.g., `Dependencies: U2`)
- **Files** — repo-relative paths to create/modify/test
- **Approach** — key decisions, no placeholder TBDs
- **Test scenarios** — input / action / expected outcome (happy path + edges that apply)
- **Verification** — how to know the unit is done

For units with no behavioral change (scaffold-only config), use: `Test expectation: none — [reason]`.

### Phase 4 — Order execution

For each unit set:

- `execution: sequential` with `blocked_by: [U2]` when hard dependency exists
- `parallel_group: A` (shared letter) when units may run concurrently **after** shared prerequisites

Document parallel groups in a summary table:

| After | Parallel units |
| --- | --- |
| U2 | U3, U4 |

Include a mermaid dependency graph when ≥4 units.

### Phase 5 — Epic recommendations

Analyze units by **domain, release train, or team boundary**.

**Default:** If units clearly span distinct epics (e.g., KB content vs MCP server vs CI), output:

```markdown
## Epic recommendations

| Epic | Units | Rationale |
| --- | --- | --- |
| [Epic title A] | U3, U4 | … |
| [Epic title B] | U5, U6 | … |
```

**User override:** If the user says **single epic** (or "all under one epic"):

- Set in YAML frontmatter: `epic_mode: single`
- Set `epic_title: [name]`
- Map all units to that epic
- **Omit** multi-epic recommendation section

Do **not** create Jira issues in this skill.

### Phase 6 — Write plan file

Required sections:

1. Summary
2. Problem Frame
3. Requirements (table with R-IDs)
4. Key Technical Decisions
5. Assumptions (decisions accepted without explicit confirmation; link to Phase 2 discussion)
6. Implementation Units (`### U1. …` headings — not bullet lists)
7. Unit dependency graph
8. Scope Boundaries (in / deferred / out)
9. Risks (if non-trivial)

## Plan quality bar

- No TBD, TODO, or "implement later" in unit bodies
- Every file path is **repo-relative**
- Test scenarios name concrete inputs and expected outputs
- Requirements trace: each R-ID maps to at least one U-ID or is explicitly deferred

## Handoff

After the plan is written, tell the user:

1. Review units and epic recommendations
2. Run `/tp-ai-kit-jira-work-breakdown` to sync to Jira (optional)
3. Run `/tp-ai-kit-feature-developer` per unit or use `/ce-work` equivalent workflow
