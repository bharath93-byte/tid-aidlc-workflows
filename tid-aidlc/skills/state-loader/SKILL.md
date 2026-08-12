# state-loader

Micro skill. Loads the AI-DLC pipeline rules and the current epic's state into context before any other skill runs. It is read-only — it never writes files.

---

## Step 1: Load the Pipeline Config

Read the file at:

```
.cursor/skills/state-loader/pipeline-config.json
```

Extract and hold in working memory:

- `states` — full map of every valid pipeline state and its description
- `transitions[<state>]` — allowed next states and rollback states from the current position
- `skills_by_state[<state>]` — primary and optional skills for the current state
- `story_statuses` — valid values for story status fields

This is the immutable framework rulebook. Do not modify it.

---

## Step 2: Identify the Target Epic

Resolve the epic silently using this priority order. Only ask the user if every signal fails.

1. **Already in context** — if the epic name, Jira key, or folder name is already known from the current conversation, open files, or recently viewed files, use it directly. No search, no confirmation needed.
2. **Infer from topic** — if the user's message unambiguously points to one epic (e.g. mentions a feature, signal, or component unique to one epic), use that epic. No search, no confirmation needed.
3. **Ask (last resort only)** — only if the epic is genuinely unknown from context, ask exactly once: *"Which epic are we working on? Give me the folder name under `aidlc-docs/` or the Jira key."* Do not proceed until the user answers.

> **Rule:** Never ask when the answer is already knowable from context. Ask only when the epic is genuinely ambiguous or unknown.

**Resolve `EPIC_DIR`.** The directory may use either naming form (see `governance.epic_dir_patterns` in the config):

- `aidlc-docs/<epic-name>/`
- `aidlc-docs/<epic-name>_<epic-id>/`

Use whichever exists. If both exist, prefer the one that contains a `state.json`. This is a single directory-existence check — do not read file contents while resolving.

---

## Step 3: Load the Epic State

Read `EPIC_DIR/state.json`.

**If the file does not exist:** the epic is in the implicit `not-started` state (no error). Set `status = "not-started"` with empty `stories`, then continue to Step 4 — the banner will correctly surface `aidlc-epic-scaffold` as the next skill.

**If it exists,** extract and validate against `state_json_schema.required` in the config:

- `epic-id`
- `epic-name`
- `status` — the current pipeline position
- `stories` — the current story map (may be empty `{}`)

If any required field is missing or malformed, warn the user, show what was found, and ask them to fix `state.json` before proceeding.

**Trust `state.json` as the single source of truth.** Do not scan disk artifacts to re-derive the status (respects both correctness and token cost).

---

## Step 4: Resolve the Active Rules

Look up the loaded `status` in `pipeline-config.json`.

**If `status` is not a key in `states`** (typo or unknown value), stop: warn the user, print the list of valid state keys, and ask them to correct `state.json`. Do not guess.

Otherwise extract:

- `states[status].description` → what this state means
- `transitions[status].next` → where the pipeline can go next
- `transitions[status].rollback` (if present) → valid rollback states
- `skills_by_state[status].primary` → skills that SHOULD be run now
- `skills_by_state[status].optional` → skills that MAY be run now
- `skills_by_state[status].note` → any special guidance for this state

---

## Step 5: Output the Status Banner

Print this banner in chat before doing anything else. This gives the AI and user shared context.

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📦 Epic       : <epic-name> (<epic-id>)
📍 State      : <status> — <state description>
➡️  Can go to  : <next states, comma-separated, or "terminal">
🛠️  Run now    : <primary skills, comma-separated, or "none">
📖 Optionally : <optional skills, comma-separated, or "none">
📝 Stories    : <count of stories in map, or "none yet">
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

If `stories` is non-empty, also list each story in a compact table:

| Story ID | Title | Status | EARS Ref |
|----------|-------|--------|----------|
| ...      | ...   | ...    | ...      |

---

## Step 6: Hand Off

Once the banner is printed, the calling skill (or the user's current task) takes over. The pipeline-config and state are now in context for the rest of the session.

**Do not proceed with any design, code, or file changes as part of this skill.** State-loader is context-only.

**Writer contract (for the calling skill, not this one):** when a phase completes and its transition trigger is met, the calling skill advances `status` in `state.json` to a value listed in `transitions[current].next` (or `.rollback`), and appends a matching row to `EPIC_DIR/audit.md`. state-loader itself never writes.

---

## Usage Convention

Every AI-DLC skill MUST begin with this instruction at the top of its execution:

> *Before doing anything, invoke the `state-loader` skill to load the pipeline config and epic state into context.*

Skills may skip state-loader only for purely informational or read-only queries where no epic context is needed.
