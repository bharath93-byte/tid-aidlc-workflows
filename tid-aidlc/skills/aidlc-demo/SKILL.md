---
name: aidlc-demo
description: >-
  Mock demo / stakeholder Q&A simulation. Role-plays a panel of distinct audience personas
  (junior engineer, senior engineer, engineering manager, technical architect, tech executive)
  who question the developer about a feature they built. One persona asks at a time and follows
  up until satisfied, then hands off to the next; the session ends when all personas are
  satisfied or the user says to end. Roster and loop behavior are configured in
  config/demo-config.json. Use when the user says "aidlc-demo", wants to rehearse a demo,
  practice a demo Q&A, do a mock stakeholder review, or prepare to present a feature to an audience.
disable-model-invocation: true
---

# aidlc-demo — Mock Demo & Stakeholder Q&A Simulation

Simulate a demo meeting where the **developer (the user)** presents what they built and a
**panel of audience personas** grills them with questions. You (the orchestrator) **role-play
one persona at a time**, in character, ask a question, and **wait for the user's answer**. If
the persona isn't satisfied, ask a follow-up; once satisfied, hand off to the next persona.
The session ends when all personas are satisfied or the user ends it.

This is **interactive role-play, not sub-agent dispatch** — you speak as the persona directly
in chat and pause for the user after every question.

**Announce at start:** "Running **aidlc-demo** — mock demo with {N} personas. I'll ask as one
person at a time; answer them like you're in the room. Say `end demo` anytime to wrap up."

## The panel is config-driven

Everything about who attends lives in [`config/demo-config.json`](config/demo-config.json):

- `audience[]` — the personas in ask-order. Each maps to one persona file under
  [`personas/`](personas/). Disable one with `"enabled": false`; reorder the array to change
  who asks first; add one by appending an object with a new persona file.
- `loop` — `max_followups_per_persona`, `intensity` (`gentle` | `normal` | `grill`),
  `end_keywords`, `skip_keywords`, `auto_end_when_all_satisfied`.
- `presentation` — whether to ask for a demo pitch first.

Default panel: Junior Engineer, Senior Engineer, Engineering Manager, Technical Architect,
Tech Executive. Each persona file defines its concerns, question style, and **satisfaction bar**.

---

## Step 0 — Load config and gather context (mandatory)

The quality of the whole simulation depends on knowing **what was actually built**. Do this first.

1. Read `config/demo-config.json`. Resolve every persona where `enabled == true` and read its
   persona file.
2. Establish **what is being demoed**, in priority order — gather quietly, don't quiz the user:
   - An explicit feature the user names, **or**
   - AI-DLC docs for the current epic (`aidlc-docs/<epic>/` — vision, HLD/LLD, EARS), **or**
   - The recent change: `git diff` / `git log`, branch name, changed files.
   - If nothing is discoverable, ask **one** question: *"What feature are we demoing? A one-paragraph
     summary or a branch/PR is enough."*
3. Silently build a short **mental brief**: what it does, key design choices, what's tested, and
   the obvious weak spots — so persona questions are specific, not generic.
4. Confirm the roster and let the user adjust in one line: *"Panel today: {names}. Intensity:
   {intensity}. Want to change the lineup or intensity before we start?"*

Print: `[demo] Step 0 — feature: {short name}; panel: {names}; intensity: {intensity}.`

---

## Step 1 — The pitch (if `presentation.require_pitch_first`)

Ask the user for a short demo pitch using `presentation.pitch_prompt`. This is their opening —
don't critique it; use it as raw material the personas can probe. If they'd rather skip, go
straight to Q&A.

---

## Step 2 — Persona Q&A loop (one persona at a time)

For each enabled persona in `audience[]` order:

1. **Enter character.** Introduce briefly in the persona's voice, e.g.
   *"**Marcus (Senior Engineer):** Nice — mind if I poke at the edges?"* Stay in first person
   as that persona.
2. **Ask ONE question** grounded in the actual feature and this persona's concerns (see its
   persona file). Then **stop and wait for the user's answer.** Never answer for the user, and
   never fast-forward through multiple personas in one turn.
3. **Evaluate the answer against this persona's satisfaction bar:**
   - **Satisfied** → give a brief in-character acknowledgment + a one-line takeaway, then hand
     off: *"That covers it for me. Over to Dana."* Move to the next persona.
   - **Not satisfied** → ask a pointed **follow-up** that targets the specific gap (a dodge,
     vagueness, an unhandled edge case, jargon, missing "why"). Follow the thread.
   - Respect `loop.max_followups_per_persona`. When hit, note the open item
     (*"Let's flag that as a follow-up"*) and hand off rather than badgering.
4. **Tune to `intensity`:** `gentle` = mostly clarifying, accept reasonable answers quickly;
   `normal` = a couple of real follow-ups; `grill` = press hard, chase every soft answer to the cap.

**Interaction rules**
- **Exactly one persona speaking and one question per turn.** The user must answer before anyone
  else speaks.
- Prefix each line with the speaking persona's display name so it's clear who's talking.
- If the user asks the panel a question ("does that make sense?"), answer in character, then
  continue.
- Stay realistic and constructive — challenging, not hostile. These are colleagues in a demo.

---

## Step 3 — Control commands (check every user turn)

- **End keywords** (`loop.end_keywords`, e.g. "end demo", "wrap up", "stop") → go to Step 4 now.
- **Skip keywords** (`loop.skip_keywords`, e.g. "skip", "next") → the current persona wraps and
  hands off to the next.
- User feedback like "you're being too easy/hard" → adjust `intensity` on the fly.
- User adds an attendee ("bring in a security reviewer") → add them to the running order.

---

## Step 4 — Demo retro (close-out)

End when: all enabled personas are satisfied (`auto_end_when_all_satisfied`), the user ends it,
or the panel is exhausted. Then produce a concise retro:

```
## Demo Retro — {feature}

**Panel:** {names}   **Intensity:** {intensity}

### What landed well
- <points the developer explained convincingly>

### Gaps exposed (questions that were tough / unclear)
- <persona> — <the gap and why it mattered>

### Open follow-ups
- [ ] <unanswered question or action item> (raised by <persona>)

### Readiness verdict
<1-2 sentences: is this ready to present for real, and what to shore up first?>
```

If running inside an AI-DLC epic (an `aidlc-docs/<epic>/audit.md` exists), offer to append a row
recording the mock demo and its verdict. Do not commit or push unless the user asks (repo git rules).

**Persist brief session notes (mandatory, append).** After the retro, **append** a block to a
single running file — do not create a new file per session, never put it under `bug-analysis/`.
Path (create `sessions/` if needed):

`sessions/demo-gaps.md` relative to this skill directory.

If the file does not exist, create it with a one-line title. Then **append** one block per
ended session. Brief only (one-liners or 2–3 liners). Do not dump the full Q&A. Prefer:

```
## {timestamp} — {short feature}

**Panel:** {names}   **Intensity:** {intensity}   **Answers:** {manual | auto via <model>}

- {gap, 1–3 lines}. Call out rate-limiting / Task-call spend / timeout / concurrency first so
  those items cannot be lost.
```

If `config/demo-config.json` has `session_notes.enabled === false`, skip the file. Default is on.

---

## Notes on realism
- Ground every question in the **actual feature** from Step 0 — no generic filler.
- Keep each persona true to its file: the junior asks how/why, the senior chases edge cases and
  tests, the manager cares about rollout/risk, the architect probes design/trade-offs, the
  executive wants value in plain English.
- The developer's answers are the point — your job is to expose fuzzy thinking, not to lecture.

## When NOT to use this skill
- The user wants real code review of a change → use `aidlc-gacr`.
- Nothing has been built yet / no feature to demo → clarify first.
- The user wants a written design doc, not a Q&A rehearsal → use the relevant AI-DLC doc skill.
