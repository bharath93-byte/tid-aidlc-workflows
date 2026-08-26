---
name: aidlc-jira-story-breakdown
description: Governed RPT prioritization phase. After design-completed, breaks approved HLD/LLD/EARS into tracer-bullet vertical slices, writes the state.json stories map (ears_ref, lld_ref, blockedBy), and advances status to prioritization-completed. Chained by aidlc-init as Phase D. Use when the user says "aidlc-jira-story-breakdown", "prioritize stories", "break down into tickets", or when pipeline status is design-completed.
---

# **AIDLC Jira Story Breakdown**

Governed **RPT Prioritization** phase. Break approved design (HLD / LLD / EARS) into a set of **tickets** — tracer-bullet vertical slices, each declaring the deliverable tickets that **block** it — then persist them to `EPIC_DIR/state.json`'s `stories` map and advance `status → prioritization-completed`.

Tickets may later be published to **Jira via the E-Tools MCP server** (`https://mcp.trimble.tools/mcp`). If the target Jira project key or triage label vocabulary hasn't already been provided in context, confirm it with the user before Step 5 — use `jira_list-projects` to help them identify the right project key. **`state.json` is the governance artifact**; Jira publishing is currently in testing mode.

## **Process**

### **0. Load pipeline state (state-loader)**

*Before doing anything, invoke the `state-loader` skill* to load `pipeline-config.json` and the epic's `state.json`. Use the resolved `EPIC_DIR`.

**Prerequisite:** `status` must be `design-completed` to start a new breakdown. Allow re-run at `prioritization-completed` to revise the stories map. If `status` is earlier than `design-completed`, stop and tell the user to finish `aidlc-design-driven-dev` (or re-run `aidlc-init`) first. If `status` is `implementation-in-progress` or later, stop — do not rewrite the map under an active implementation.

Print: `[aidlc-jira-story-breakdown] Step 0 complete — EPIC_DIR resolved, status legal.`

### **1. Gather context**

Read from `EPIC_DIR`, not only conversation paste:

- `vision.md`, `adr.md`, `high-level-design.md` (if present)
- every `designs/**/LLD.md` (Full tier) and every `designs/**/*-EARS.md` (or top-level `*-EARS.md` on Lightweight / EARS-only epics)
- `system-prompts/context.xml` and `system-prompts/adr_decisions.xml`

If the user also passes a reference (a spec path, an issue number or URL, or a specific EARS file) as an argument, fetch it and read its full body and comments. Ticket titles and descriptions must use the project's domain glossary vocabulary and respect ADRs, EARS, and vision.

### **2. Explore the codebase (optional)**

If you have not already explored the codebase, do so to understand the current state of the code. Ticket titles and descriptions should use the project's domain glossary vocabulary, and respect ADRs, EARS and vision in the area you're touching.

Look for opportunities to prefactor the code to make the implementation easier. "Make the change easy, then make the easy change."

### **3. Draft vertical slices**

Break the work into **tracer bullet** tickets.

- Each slice cuts a narrow but COMPLETE path through every layer (schema, API, UI, tests) — vertical, NOT a horizontal slice of one layer
- A completed slice is demoable or verifiable on its own
- Each slice is sized to fit in a single fresh context window
- Any prefactoring should be done first
- **Each slice maps to exactly one EARS file** (`ears_ref`) and its parent LLD (`lld_ref`). On Lightweight / EARS-only epics, set `lld_ref` to `""`.

Give each ticket its **blocking edges** — the other tickets that must complete before it can start. A ticket with no blockers can start immediately.

**Wide refactors are the exception to vertical slicing.** A **wide refactor** is one mechanical change — rename a column, retype a shared symbol — whose **blast radius** fans across the whole codebase, so a single edit breaks thousands of call sites at once and no vertical slice can land green. Don't force it into a tracer bullet; sequence it as **expand–contract**. First expand: add the new form beside the old so nothing breaks. Then migrate the call sites over in batches sized by blast radius (per package, per directory), each batch its own ticket blocked by the expand, keeping CI green batch to batch because the old form still exists. Finally contract: delete the old form once no caller remains, in a ticket blocked by every migrate batch. When even the batches can't stay green alone, keep the sequence but let them share an integration branch that all block a final integrate-and-verify ticket — green is promised only there.

### **4. Quiz the user**

Present the proposed breakdown as a numbered list. For each ticket, show:

- **Title**: short descriptive name
- **EARS ref**: path relative to `EPIC_DIR`
- **LLD ref**: path relative to `EPIC_DIR`, or "(none — Lightweight)"
- **Blocked by**: which other tickets (if any) must complete first
- **What it delivers**: the end-to-end behaviour this ticket makes work

Ask the user:

- Does the granularity feel right? (too coarse / too fine)
- Are the blocking edges correct — does each ticket only depend on tickets that genuinely gate it?
- Should any tickets be merged or split further?
- Does each `ears_ref` / `lld_ref` point at the right design artifact?

Iterate until the user approves the breakdown.

### **5. Persist the stories map, then publish (testing mode)**

On explicit approval of the numbered breakdown:

1. Write `EPIC_DIR/state.json` `stories` — keyed by the local `id` (e.g. `T1`). Preserve existing `epic-id` and `epic-name`. Set each entry:

```json
"T1": {
  "title": "Short descriptive ticket title",
  "status": "todo",
  "ears_ref": "designs/<feature>/<subfeature>-EARS.md",
  "lld_ref": "designs/<feature>/LLD.md",
  "blockedBy": []
}
```

   - `ears_ref` / `lld_ref` are paths relative to `EPIC_DIR`. `lld_ref` may be `""` on Lightweight / EARS-only epics.
   - `blockedBy` lists the `id`s of tickets that must complete first; empty array if the ticket can start immediately.
   - On a re-run at `prioritization-completed`, replace the `stories` map with the newly approved set. Do not silently merge with stale ids.

2. Advance `status` → `prioritization-completed`.

3. Append an `audit.md` row via `aidlc-approve` (`PHASE: prioritization`, skill `aidlc-jira-story-breakdown`, action summarizing the story count and that the map was written).

4. Output the full approved ticket set as a single JSON array in chat (testing-mode tracker payload — see schema below). **Do NOT call any Jira/GitHub MCP tools** until the testing-mode note is removed. `state.json` is the governance artifact; the JSON in chat is the future tracker payload.

> **TEMPORARY — TESTING MODE:** Do NOT call any Jira/GitHub MCP tools to actually create issues right now. Instead, output the full approved ticket set as a single JSON array (see schema below) in your response. Skip the real-tracker steps further down until this note is removed.
>
> ```json
> [
>   {
>     "id": "T1",
>     "issueType": "Story",
>     "summary": "Short descriptive ticket title",
>     "whatToBuild": "The end-to-end behaviour this ticket makes work, from the user's perspective.",
>     "acceptanceCriteria": ["Criterion 1", "Criterion 2"],
>     "ears_ref": "designs/<feature>/<subfeature>-EARS.md",
>     "lld_ref": "designs/<feature>/LLD.md",
>     "labels": ["ready-for-agent"],
>     "parent": null,
>     "blockedBy": []
>   },
>   {
>     "id": "T2",
>     "issueType": "Story",
>     "summary": "...",
>     "whatToBuild": "...",
>     "acceptanceCriteria": ["..."],
>     "ears_ref": "designs/<feature>/<other>-EARS.md",
>     "lld_ref": "designs/<feature>/LLD.md",
>     "labels": ["ready-for-agent"],
>     "parent": null,
>     "blockedBy": ["T1"]
>   }
> ]
> ```
>
> - `id` is a local, stable placeholder (e.g. `T1`, `T2`) used only to express `blockedBy` edges before real tracker keys exist — not a Jira key. It is also the `state.json` stories-map key.
> - `whatToBuild` and `acceptanceCriteria` are kept as separate fields (matching the ticket template's `## What to build` / `## Acceptance criteria` sections) rather than merged into one blob — `acceptanceCriteria` is always an array, one criterion per entry.
> - `ears_ref` and `lld_ref` are paths relative to `EPIC_DIR`; `lld_ref` may be `""`.
> - `blockedBy` lists the `id`s of tickets that must complete first, in the same dependency order Step 4 was approved in; empty array if the ticket can start immediately.
> - `parent` is the parent epic/issue key if the source was an existing issue, else `null`.
> - Fields otherwise mirror what `jira_create-issue` would receive (`issueType`, `summary`, `description`, `labels`), minus `projectKey` (irrelevant while nothing is actually being created).

When testing mode is removed, publish the approved tickets. **How** depends on the tracker — the tickets are the same either way, only the shape of the blocking edges changes:

- **Jira (via the E-Tools MCP server)** → publish one issue per ticket in dependency order (blockers first) so each ticket's blocking edges can reference real keys:
  1. Confirm identity/access with `jira_myself`. Confirm the project key with the user (or `jira_list-projects`) if not already known.
  2. Call `jira_get-create-meta` once (`projectKeys`, `issuetypeNames`) to confirm the issue type name to use (typically `Story` or `Task`) and any required fields for the project — including the Epic Link / parent field, if the tickets belong under an existing epic.
  3. Create each ticket with `jira_create-issue`: `projectKey`, `issueType`, `summary` = ticket title, `description` = the ticket body (What to build / Acceptance criteria / Blocked by), `labels: ["ready-for-agent"]` unless instructed otherwise — the tickets are agent-grabbable by construction. If there's a parent epic, set it via the field discovered in step 2 through `additionalFields` (or record it under **Parent** in the ticket body if no structured field applies).
  4. Once both issues in a blocking pair exist, encode the edge with `jira_link-issues` (`linkType: "Blocks"`, `outwardIssueKey` = the blocking ticket, `inwardIssueKey` = the ticket it blocks) — this is Jira's native blocking relationship, not just prose in the description.
  5. If a link's direction is ever ambiguous, verify with `jira_get-issue-links` on the ticket in question.
- **A different issue tracker (e.g. GitHub)** → publish one issue per ticket in dependency order (blockers first) so each ticket's blocking edges can reference real identifiers. Use the platform's native blocking / sub-issue relationship where it has one; otherwise set each ticket's "Blocked by" to the blocking issues. Apply the `ready-for-agent` triage label unless instructed otherwise — the tickets are agent-grabbable by construction.

Do NOT close or modify any parent issue.

### **6. Hand off**

Print the state-loader banner (now at `prioritization-completed`). Tell the user:

- The stories map is the source of truth for implementation order.
- Next skill is **`aidlc-tdd`** (per-story worker). **aidlc-init** Phase E loops it across the frontier, then Phase F runs **`aidlc-gacr`**.
- Work the **frontier**: any story whose `blockedBy` ids are all `status=done` (at this point, those with empty `blockedBy`). For a purely linear chain that means top to bottom.

When invoked by **aidlc-init**, return control after this print so init can enter Phase E. Do not invoke `aidlc-tdd` yourself.

Print: `[aidlc-jira-story-breakdown] complete — status: prioritization-completed; N stories written.`

# **—**

**What to build:** the end-to-end behaviour this ticket makes work, from the user's perspective — not a layer-by-layer implementation list.

**Blocked by:** the numbers/titles of the tickets that gate this one, or "None — can start immediately".

**Status:** Backlog

- Acceptance criterion 1
- Acceptance criterion 2

Label: ready-for-agent

## **Parent**

A reference to the parent issue on the tracker (if the source was an existing issue, otherwise omit this section).

## **What to build**

The end-to-end behaviour this ticket makes work, from the user's perspective — not layer-by-layer implementation.

## **Acceptance criteria**

- Criterion 1
- Criterion 2

## **Blocked by**

- A reference to each blocking ticket, or "None — can start immediately".

In either form, avoid specific file paths or code snippets — they go stale fast. Exception: if a prototype produced a snippet that encodes a decision more precisely than prose can (state machine, reducer, schema, type shape), inline it and note briefly that it came from a prototype. Trim to the decision-rich parts — not a working demo, just the important bits. `ears_ref` / `lld_ref` in `state.json` are the durable design pointers; do not duplicate those paths in the ticket body.
