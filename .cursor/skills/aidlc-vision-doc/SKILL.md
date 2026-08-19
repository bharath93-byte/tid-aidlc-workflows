---
name: aidlc-vision-doc
description: Standalone AIDLC vision document generator. Takes a context block from the current conversation (or from aidlc-context-loader), generates a structured vision.md using the canonical template, previews the draft in chat, and writes to disk only after explicit user approval. Use when the user wants to generate or regenerate a vision document for a Jira epic.
disable-model-invocation: true
---

# AIDLC Vision Doc

Atomic, standalone skill. Generates `vision.md` from loaded context.
When chained from `aidlc-init` after `aidlc-epic-scaffold`, conversation context from the scaffold session satisfies the context requirement — no separate `aidlc-context-loader` needed.

---

## Step 0: Load pipeline state (state-loader)

Before anything else, if it hasn't already run in this session, invoke the **state-loader** skill to load `pipeline-config.json` and the epic's `state.json`. Use the resolved `EPIC_DIR` as the output directory.

**Prerequisite:** `status` should be `context-ready` (or allow re-run at `inception-completed` for vision revisions). If `status` is `not-started`, stop and tell the user to run `aidlc-epic-scaffold` first.

---

## Step 1: Confirm context and output path

If `EPIC_DIR` is known from state-loader or `aidlc-init`, set:
`OUTPUT_PATH = {EPIC_DIR}/vision.md`

If a context block from `aidlc-context-loader` or `aidlc-epic-scaffold` is present in the conversation, confirm:
> "I'll use the context block for `<epic-id>`. Output: `{EPIC_DIR}/vision.md`. Shall I proceed?"

If no context exists, ask the user to run `aidlc-epic-scaffold` or `aidlc-context-loader` first, or paste the requirements so context can be inferred.

When not chained, fall back to `OUTPUT_PATH = aidlc-docs/<epic-name>_<epic-id>/vision.md`.

---

## Step 2: Generate vision.md draft in chat

Use the template at `.cursor/skills/aidlc-vision-doc/templates/vision-template.md` as structure.

Fill every section from the context block. Where context is insufficient for a section, use a clearly marked placeholder: `_[TBD — no context provided]_`.

Render the **complete draft in the chat window**. Do NOT write any file yet.

Say: *"Here is the vision.md draft for `<epic-id>`. Review it and say **'approved'**, **'looks good'**, or **'finalized'** to write it to disk — or tell me what to change."*

---

## Step 3: Incorporate feedback

If the user requests changes: revise the draft in chat and present again.
Repeat until explicit approval.

---

## Step 4: Write to disk and advance state (Gate 2 approved)

When the user approves:

1. Create `{EPIC_DIR}/` if it does not exist.
2. Write the approved draft to `{EPIC_DIR}/vision.md`.
3. Update `{EPIC_DIR}/state.json`: set `"status": "inception-completed"`.
4. Append a row to `{EPIC_DIR}/audit.md` (create with standard header if missing):
   - Phase: `inception`
   - Skill/Agent: `aidlc-vision-doc`
   - Action: `vision.md Gate 2 approved and written; status advanced to inception-completed.`
   - Approver: current system username
5. Confirm: "`{EPIC_DIR}/vision.md` written. Status: `inception-completed`. Next: `aidlc-adr`."

---

## Checklist

```
- [ ] state-loader invoked; EPIC_DIR resolved
- [ ] Context confirmed and OUTPUT_PATH set to EPIC_DIR/vision.md
- [ ] Full draft generated in chat (not on disk)
- [ ] User feedback incorporated
- [ ] User approved — "approved" / "looks good" / "finalized"
- [ ] vision.md written to EPIC_DIR/
- [ ] state.json advanced to inception-completed
- [ ] audit.md row appended
```
