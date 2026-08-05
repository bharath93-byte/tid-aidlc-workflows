---
name: tp-ai-kit-jira-work-breakdown
description: Create Jira epics and issues from an approved delivery plan using the e-tools MCP server (server name: e-tools, url: https://mcp.trimble.tools/mcp). Maps plan units (U-IDs) to Jira tickets with summaries and descriptions linking back to the plan. Use after delivery-planning. Triggers on /tp-ai-kit-jira-work-breakdown, "create Jira tickets from this plan", or "sync plan to Jira".
disable-model-invocation: true
category: sdlc-planning
sdlc_phase: planning
status: stable
owner: platform-ai-team
tags: [planning, jira, breakdown, tickets]
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

# Jira Work Breakdown

**Announce at start:** "I'm syncing **`{plan}`** to Jira."

Create Jira epics and issues from an **approved delivery plan**. This skill **does not** write or rewrite plan files — use `tp-ai-kit-delivery-planning` first.

## Prerequisites

- **e-tools MCP** (server name: `e-tools`) configured in `.cursor/mcp.json` pointing to `https://mcp.trimble.tools/mcp`
- An existing plan at `docs/plans/*.md` with `### U1.` … unit headings
- User provides **Jira project key** (required — ask if missing; if user does not know it, call `jira_list-projects` and present the list)

## MCP availability

At startup:

1. Check that `jira_` prefixed tools (e.g. `jira_create-issue`) are listed and callable via the `e-tools` MCP server
2. If unavailable: print setup steps from `skills/jira-integration/README.md` and **stop** — do not guess ticket keys

## Plan format contract

The skill expects plans produced by `tp-ai-kit-delivery-planning`. Required markers:

- Unit headings: `### U1. Title` (not bullet lists)
- Dependency line: `Dependencies: U2, U3` (or `none`)
- Optional frontmatter: `epic_mode: single`, `epic_title: …`
- Optional section: `## Epic recommendations` table with columns `Epic | Units | Rationale`

## Inputs

| Input | Notes |
| --- | --- |
| Plan path | User-provided or most recent `docs/plans/*-plan.md` |
| Project key | e.g. `PLAT` — ask if missing; offer `jira_list-projects` to discover |
| Parent epic | Optional existing epic key to attach under |
| Epic mode | From plan: `epic_mode: single`, epic recommendations table, or user choice at confirm step |

## Workflow

### Phase 1 — Parse plan

Extract from the plan file:

- Unit U-IDs, titles, goals, dependencies
- `## Epic recommendations` table OR `epic_mode: single` / `epic_title`
- Requirements IDs referenced per unit (for description)

### Phase 2 — Confirm with user

Ask **one confirmation block** (not a long questionnaire):

- Jira project key (present `jira_list-projects` results if user does not know)
- Epic strategy:
  - **A)** Use plan's epic recommendations (list epics + unit mapping)
  - **B)** Single epic (use plan's `epic_title` or ask for title)
  - **C)** Attach all issues under existing epic `[KEY]`
- Issue type preference: Story vs Task (default Story)

If plan recommends multiple epics and user has not chosen, **present the recommendation** and ask A vs B — do not silently split.

### Phase 3 — Create in Jira (via MCP)

Order:

1. Create epic(s) if needed (not for option C with existing parent):
   - Use `jira_create-issue` with `projectKey`, `issueType: Epic`, and `summary: [Epic title from recommendations or plan]`
   - Capture the returned epic key for use as `parentKey` in step 2
2. For each unit in dependency order (parents before dependents when linking matters):
   - Call `jira_create-issue` passing `projectKey` explicitly every call
   - **Summary:** `[U{n}] {unit title}`
   - **Description:** Goal, Files list, Dependencies (U-IDs), link to plan file path, R-IDs
   - **Labels:** `delivery-plan`, `u-id-U{n}` (if project allows)
   - **parentKey:** for multi-epic mode, look up the epic key for this unit using the recommendations table captured in Phase 1; for single-epic mode, use the one epic key created in step 1

Capture all returned issue keys.

### Phase 4 — Report

Output markdown table:

| U-ID | Jira key | Summary | Epic |
| --- | --- | --- | --- |
| U1 | PLAT-123 | … | PLAT-100 |

Save optional artifact: `docs/plans/{feature}/jira-sync-{date}.md` (user can request).

## Rules

- **Never** modify the delivery plan file
- **Never** create tickets without user confirmation of project + epic strategy
- If MCP create fails mid-run: report what succeeded, stop, do not retry blindly
- Idempotency: if user re-runs, call `jira_search-issues` with `summary ~ "[U{n}]" AND project = {projectKey}` to check for existing tickets before creating; ask whether to skip or update existing keys

## Handoff

Suggest next step: implement units via `/tp-ai-kit-feature-developer` or assign owners in Jira.
