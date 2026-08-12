---
name: aidlc-vision
description: AIDLC Phase 1 Vision workflow. Activates when the user says '/aidlc-vision start', 'start vision workflow', 'run aidlc vision', or 'begin vision phase for <epic>'. Pulls Jira epic context or processes pasted requirements, runs a 6-category completeness check with one-at-a-time gap questions, previews a vision.md draft in chat, and writes to aidlc-docs/ only after explicit user approval. Two approval gates. Nothing is written until Gate 2 passes.
disable-model-invocation: true
---

# AIDLC Vision — Phase 1 Orchestrator

Self-contained. All logic is inline — no inter-skill calls.
Execute steps in order. **User approval is required at Steps 4 (Gate 1) and 6 (Gate 2).**

---

## Step 1: Get input

Ask:

> "Provide the Jira epic link or key (e.g. `IAM-123`) — or paste your requirements text directly."

**Detect input type:**
- Contains a Jira key pattern (`[A-Z]+-\d+`) → **Jira path**. Extract `EPIC_KEY`. Set `INPUT_SOURCE = jira`.
- Free text only → **Manual path**. Ask: *"What short identifier should I use as the directory name? (e.g. `IAM-999` or `user-provisioning`)"* → set `EPIC_KEY`. Set `INPUT_SOURCE = manual`.

Store `EPIC_KEY`, `INPUT_SOURCE`.

---

## Step 2: Load context

### Jira path

Call `jira_get-issue` with `issueKey: <EPIC_KEY>`. Extract:
- `fields.summary` → title
- `fields.description` → full description
- `fields.status.name` → current status
- Any non-null `fields.customfield_*` → acceptance criteria, definition of done

Call `jira_get-epic-issues` with `epicKey: <EPIC_KEY>`. Extract child story summaries and descriptions.

If a call fails, note it and continue with the data returned.

### Manual path

Use the pasted text as-is. `INPUT_SOURCE = manual`.

---

## Step 3: 6-category completeness check

Score each category: **Present** / **Partial** / **Missing**.

| # | Category | What to look for |
|---|----------|-----------------|
| 1 | Functional Scope | What the feature does; key user flows |
| 2 | Actors / Personas | Who uses it; roles; internal vs external |
| 3 | Constraints | Technical, regulatory, timeline, or budget limits |
| 4 | Data | CRUD operations; which entities |
| 5 | Integrations | External systems, APIs, or services touched |
| 6 | Success Criteria | Definition of done; measurable outcomes |

Apply the mechanics from `tp-ai-kit-scoped-questioning` when that skill is
available. Do not invoke it as a separate workflow; this orchestrator remains
self-contained.

Keep questioning strictly within the six vision categories. Do not expand
into API contracts, event schemas, implementation design, testing, or rollout
unless the source material makes one of them a material vision-level
constraint.

For all Missing or Partial categories:

1. Rank gaps by decision risk and start with the highest-risk unknown.
2. Check Jira, child stories, repository docs, and prior artifacts first.
   Do not ask the user what available evidence already answers.
3. Ask one focused question at a time.
4. Offer 2–3 concrete options with trade-offs and an evidence-based
   recommendation.
5. Record each decision, update the context, re-score, and move to the next
   unresolved branch.

```
Category: <name> — Missing / Partial

<Focused question about the gap>

Options:
- Option A: <repo-aligned or common IAM pattern>. <trade-off>
- Option B: <alternative>. <trade-off>
- Option C: I'll describe it myself

Recommendation: Option A — <evidence-based reason>.
```

Repeat until the six-category design tree is sufficiently covered and the
user confirms it is complete. If the user says "skip", "enough", or
"proceed" early, identify the highest-risk unresolved unknown and explain its
impact before moving to Gate 1.

---

## Step 4: Gate 1 — Context approval

Present the completeness scorecard:

```
## Completeness Scorecard — <EPIC_KEY>

| Category | Score |
|----------|-------|
| Functional Scope | Present / Partial / Missing |
| Actors / Personas | ... |
| Constraints | ... |
| Data | ... |
| Integrations | ... |
| Success Criteria | ... |

Source: <Jira <EPIC_KEY> | Manual input>

### Decisions Agreed
| Topic | Decision | Rationale |
|-------|----------|-----------|
| <topic> | <decision> | <trade-off or evidence> |

### Remaining Risks
- <highest-risk unresolved unknown, or "None">
```

Say: *"Review the scorecard. If context is sufficient, say **'approved'**, **'looks good'**, or **'finalized'** to proceed. Or tell me what's missing and I'll ask more questions."*

**Do not proceed to Step 5 until the user explicitly approves.**

---

## Step 5: Generate vision.md draft in chat

Generate a complete draft using all gathered context. Structure:

---

```markdown
# Vision Document — <EPIC_KEY>

> **Phase:** Inception | **Status:** Draft | **Created:** <today's date>
> **Source:** <Jira: <EPIC_KEY> | Manual input>

## 1. Problem Statement
<derived from context — what problem, why it matters, what is broken today>

## 2. Goals
- <outcome-oriented goal 1>
- <goal 2>

## 3. Non-Goals (Out of Scope)
- <explicit boundary>

## 4. Personas & Actors
| Persona | Role | Primary Need |
|---------|------|-------------|
| <actor> | <role> | <need> |

## 5. Functional Scope
### Core capabilities
- <capability>

### Key user flows
1. <Actor does X → system responds with Y>

## 6. Data
| Entity | Operations | Storage / Owner | Notes |
|--------|-----------|-----------------|-------|
| <entity> | CRUD | <location> | <constraint> |

## 7. Integrations
| System | Direction | Data / Event | Notes |
|--------|-----------|-------------|-------|
| <system> | Inbound / Outbound / Both | <what> | <protocol> |

## 8. Constraints
- **Technical:** <...>
- **Regulatory:** <...>
- **Timeline:** <...>

## 9. Success Criteria
| Criterion | Measurement | Target |
|-----------|-------------|--------|
| <criterion> | <metric> | <value> |

## 10. Assumptions
- <assumption>

## 11. Open Questions
| # | Question | Owner | Target Date |
|---|----------|-------|------------|
| 1 | <question> | TBD | TBD |

---
*Generated by `aidlc-vision` — Phase 1 Inception.*
```

---

Render the full draft in chat. **Do NOT write any file.**

Say: *"Here is the vision.md draft for `<EPIC_KEY>`. Review it carefully. Say **'approved'**, **'looks good'**, or **'finalized'** to write it to disk — or tell me what to revise."*

---

## Step 6: Gate 2 — Vision doc approval

If the user requests changes: revise the draft in chat and present again.
Repeat until the user says "approved", "looks good", or "finalized".

**Do not proceed to Step 7 until explicitly approved.**

---

## Step 7: Write to disk

1. Create `aidlc-docs/<EPIC_KEY>/` if it does not exist.
2. Write the approved draft to `aidlc-docs/<EPIC_KEY>/vision.md`.
3. Confirm: "`aidlc-docs/<EPIC_KEY>/vision.md` written successfully."
4. Note: "The `aidlc-audit-stamp` hook will automatically create/update `aidlc-docs/<EPIC_KEY>/audit.md` with an initial log entry."

---

## Step 8: Final summary

| # | Step | Status |
|---|------|--------|
| 1 | Input received (`<INPUT_SOURCE>`) | ✓ |
| 2 | Context loaded | ✓ |
| 3 | 6-category completeness check + gap-filling | ✓ |
| 4 | Gate 1: Context scorecard approved | ✓ |
| 5 | vision.md draft generated in chat | ✓ |
| 6 | Gate 2: Vision doc approved | ✓ |
| 7 | vision.md written to `aidlc-docs/<EPIC_KEY>/` | ✓ |

---

## Notes

- **Nothing is written to disk before Gate 2.** This is non-negotiable.
- **Gate trigger phrases:** "approved" / "looks good" / "finalized" (case-insensitive).
- **Jira MCP:** Uses `jira_get-issue` and `jira_get-epic-issues` via the `user-etools` MCP server.
- **Audit trail:** The `aidlc-audit-stamp` hook fires automatically after `vision.md` is saved and writes `audit.md`.
- **Sub-skills:** `aidlc-context-loader` and `aidlc-vision-doc` exist as standalone skills for independent use. This orchestrator contains all logic inline — it does not call them.
