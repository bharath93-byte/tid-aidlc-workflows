# **aidlc-inception**

Atomic, standalone skill. Acts as the initial context loader and requirements gatherer for the AI-DLC pipeline. Can be run independently or as context preparation before generating the vision document.

---

## **Step 0: Load pipeline state (state-loader)**

Before anything else, if it hasn't already run in this session, invoke the **state-loader** skill to load `pipeline-config.json` and the `state.json` **of the currently-resolved epic** — i.e. the `state.json` inside this epic's own context directory (`aidlc-docs/<epic-name>/` or `aidlc-docs/<epic-name>_<epic-id>/`), not just any epic's file. If the epic context directory cannot be resolved from context, **ask the user which epic** (folder name or Jira key) before proceeding. Only once the correct epic and its `state.json` are loaded do you continue with this skill. This makes the work resumable across sessions and developers.

**Canonical directory:** if `aidlc-init` or state-loader already established an `EPIC_DIR` (or the epic identity was already provided), reuse that exact directory and identity for **all** outputs — `system-prompts/`, `state.json`, and `audit.md` — and skip re-asking in Step 1. Do **not** create a second directory (e.g. the `{epic-name}_{EPIC_KEY}` form) for an epic that already has one; one epic = one directory.

---

## **Step 1: Get input**

Ask:

 "Provide the Jira epic link or key (e.g. IAM-123), or paste your requirements text directly."

Detect input type:

URL or bare key matching [A-Z]+-\d+ → **Jira path**. Extract EPIC_KEY.
Free text (no key pattern) → **Manual path**. Ask: "What short identifier should I use for this epic? (e.g. IAM-999 or user-provisioning)" → set EPIC_KEY, INPUT_SOURCE = manual.

---

## **Step 2: Fetch Jira context (Jira path only)**

Call jira_get-issue with issueKey: <EPIC_KEY>.

Extract from the response:

fields.summary — epic title
fields.description — full description
fields.status.name — current status
Any non-null fields.customfield_* — acceptance criteria, definition of done

Call jira_get-epic-issues with epicKey: <EPIC_KEY>.

Extract child story summaries and descriptions to enrich context.

If either call fails, note the error and proceed with what was returned.

---

## **Step 3: 6-category completeness check**

Score each category: **Present** / **Partial** / **Missing**.


| **#** | **Category**      | **What to look for**                              |
| ----- | ----------------- | ------------------------------------------------- |
| 1     | Functional Scope  | What the feature/system does; key user flows      |
| 2     | Actors / Personas | Who uses it; roles; internal vs external users    |
| 3     | Constraints       | Technical or cost limits |
| 4     | Data              | What data is created, read, updated, or deleted   |
| 5     | Integrations      | External systems, APIs, or services involved      |
| 6     | Success Criteria  | How "done" is defined; measurable outcomes        |


---

## **Step 4: Intent-Driven Gap Discovery & Discussion**

Your primary focus is to deeply understand the **core intent, business goals, and boundaries** of the epic. The questioning process should be fluid, adaptive, and collaborative, aimed at building the most robust foundation possible for the final XML system prompts.

Keep the conversation grounded in the six completeness categories, but adapt your interaction style to best achieve understanding:

1. **Rank Gaps by Risk:** Identify which Missing or Partial categories pose the highest risk to the epic's success. Start there.
2. **Check Before Asking:** Consult the fetched Jira context, child stories, and prior artifacts first. Do not ask the user for information already present in the data.
3. **Adaptive Questioning:** Ask one focused question at a time. Use the format that best fits the gap:
   - **Open-Ended Questions:** Use short, direct questions to uncover missing business logic or intent.
   - **Multiple Choice:** Use this format when presenting specific architectural trade-offs or common IAM patterns to help the user decide.
   - **Open Discussion:** Converse naturally if the user wants to brainstorm, explore a requirement, or dictate custom rules.
4. **Dynamic Updates:** Listen closely. If the user organically brings up new prompts, constraints, or context during the discussion, instantly acknowledge and integrate it into your internal context map so it can also be updated in the final XML system prompts.

Stop when the six-category design tree is sufficiently covered, the intent is fully understood, and the user confirms readiness. If the user says "skip", "enough", or "proceed" early, identify all high risk unresolved unknown and explain its impact before moving to Step 5.

---

## **Step 5: The Review Gate (Context Summary)**

Trigger this step **only** when the user indicates they are ready to finish, says "enough", "proceed", or attempts to approve the discussion. You must present this summary for review *before* final XML generation is allowed.

Present a clean, highly scannable summary of the gathered context. Avoid verbose paragraphs and heavy markdown tables. Use status emojis (✅ Complete, ⚠️ Partial, ❌ Missing) to instantly communicate the health of each category.

Output the summary exactly in this format:

### 📋 Context Summary: <EPIC_KEY> — <Title>
*(Source: <Jira/Manual> | Status: <Jira Status>)*

**The 6 Core Categories:**
* <Status Emoji> **Functional Scope:** <1-2 sentence crisp summary>
* <Status Emoji> **Actors / Personas:** <List of specific roles/users>
* <Status Emoji> **Constraints:** <Key technical, business, or architectural limits>
* <Status Emoji> **Data:** <Core data entities created/modified>
* <Status Emoji> **Integrations:** <External systems, APIs, or services>
* <Status Emoji> **Success Criteria:** <Measurable definition of done>

**Key Decisions & Custom Rules:**
* **<Topic>:** <Decision> *(Rationale)*
* *(List any specific rules, overrides, or custom prompts the user dictated during the discussion)*

**Unresolved Items:**
* <List any skipped or remaining risk areas, or state "None">

Ask: "Please review the summary above. Say 'approved' to lock this in and generate the XML system prompts, or let me know what needs adjustment."

---

## **Step 6: XML System Prompt Generation**

Trigger this step **only** when the user says "approved", "yes", or explicitly decides to end the skill's gap-filling work.

1. **Resolve EPIC_DIR:** If `aidlc-init` or state-loader already established `EPIC_DIR`, use it. Otherwise derive from `<EPIC_KEY>` and epic title as a lowercase, hyphen-separated name (e.g., `IAM-123: Rate Limiting` → `aidlc-docs/iam-123-rate-limiting/`).
2. **Set Target Path:** `{EPIC_DIR}/system-prompts/`
3. **Generate XML Content:** Transform the finalized context block, the fetched Jira data, and absolutely all constraints, rules, user prompts, and decisions discussed during the skill's execution into a dense, token-efficient XML format. 
4. **Tag Structure:** Use explicit XML tags for every category (e.g., `<domain_context>`, `<functional_scope>`, `<actors>`, `<constraints>`, `<data>`, `<integrations>`, `<success_criteria>`, `<user_decisions>`).
5. **No Data Loss:** Ensure that *no* user prompts, specific constraints, or discussed edge cases are missed. Append these under the relevant tags or a dedicated `<additional_user_prompts>` tag.
6. **File Creation:** Automatically create the directory if it does not exist, and save the XML content to a file (e.g., `context.xml`) inside the `system-prompts` folder.
7. **Completion Message:** Output a brief success message listing the created file(s) and their path. **Do not print the full XML in the chat to save space.**

---

## **Step 7: AI-DLC Governance (State & Audit Log Initialization)**

Immediately after successfully generating the XML files in Step 6, you must initialize the formal tracking mechanisms for the AI-DLC pipeline. Do not ask for permission to do this; it is a mandatory system action.

**1. Initialize the State Tracker (`state.json`)**
*   **Path:** `{EPIC_DIR}/state.json` (canonical directory from Step 0 — never create a second `{epic-name}_{EPIC_KEY}` directory when `EPIC_DIR` is already known)
*   **Purpose:** This file acts as the machine-readable state machine for future AI skills (e.g., the scoping and TDD agents).
*   **Action:** Create or update this file. Preserve existing `epic-id` and `epic-name` if already set by `aidlc-init`. It MUST contain the following exact JSON structure. Do not populate the `stories` object yet; leave it strictly as an empty object `{}`.
```json
{
  "epic-id": "<EPIC_KEY>",
  "epic-name": "<epic-name>",
  "status": "context-ready",
  "stories": {}
}
```

**2. Initialize the Compliance Log (`audit.md`)**
*   **Path:** `{EPIC_DIR}/audit.md`
*   **Purpose:** The human-readable, immutable ledger of approvals and state changes.
*   **Action:** 
    *   **If the file DOES NOT exist:** Create it and initialize the Markdown table header exactly like this:
        ```markdown
        # AI-DLC Audit Log: <EPIC_KEY>

        | Timestamp | Phase | Skill/Agent | Action | Approver |
        |---|---|---|---|---|
        ```
    *   **Append the Approval Record:** Add a new row to the table for this successful inception run. 
        *   *Timestamp:* Use the current UTC time in ISO 8601 format (e.g., `2026-07-29T07:17Z`).
        *   *Phase:* `inception`
        *   *Skill/Agent:* `aidlc-epic-scaffold`
        *   *Action:* `Context summary approved; context.xml written; status advanced to context-ready.`
        *   *Approver:* Use the current developer's system username/handle (or prompt for it if unknown).
        *   *Example Row:* `| 2026-07-29T07:17Z | inception | aidlc-epic-scaffold | Context summary approved; context.xml written; status advanced to context-ready. | varunt |`
        
**3. Final Hand-off Message**
*   Once all background file operations are completely finished, output a clean success message in the chat.
*   List the exact file paths of the artifacts created or updated: `context.xml`, `state.json`, and `audit.md`.
*   End the skill with this exact phrasing: *"✅ Context is ready (`status: context-ready`). Vision document generation is next in the pipeline (`aidlc-vision-doc`)."*