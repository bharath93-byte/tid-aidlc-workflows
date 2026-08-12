---
name: aidlc-init
description: Orchestrator entry point for the AI-DLC pipeline. From one command it bootstraps the epic and chains state-loader -> aidlc-epic-scaffold (context) -> aidlc-vision-doc (vision) -> aidlc-adr (ADR + adr_decisions.xml) -> aidlc-design-driven-dev (HLD -> LLD -> EARS), pausing only at human approval gates. Fully resumable. Use when the user says "aidlc-init" or wants to start/resume an epic end-to-end.
---

# aidlc-init

Single entry point for the AI-DLC pipeline. From one command this drives the full chain and is **resumable** — re-running always picks up from the current `state.json` status rather than restarting.

```
aidlc-init
  └─ Step 0: state-loader              (load pipeline-config + epic state)
  └─ Step 1: bootstrap / resume        (create state.json @ not-started, or detect existing)
  └─ Step 2: route by status           (state-machine driver)
  └─ Phase A:   aidlc-epic-scaffold    → status: context-ready
  └─ Phase A½: aidlc-vision-doc        → status: inception-completed
  └─ Phase B:   aidlc-adr              → status: adr-completed (includes adr_decisions.xml)
  └─ Phase C:   aidlc-design-driven-dev → status: design-completed
```

## What this produces

By the end (`status = design-completed`): the XML system prompts (`context.xml` + `adr_decisions.xml`), `vision.md`, `adr.md`, `high-level-design.md`, every feature `LLD.md`, every `*-EARS.md`, and a complete `audit.md` trail — each artifact approved by you at its gate.

> **Approval gates are human.** This orchestrator *sequences* the skills and **pauses at every approval gate**. It never auto-approves. Nothing lands on disk without your explicit "approved". "Boom" means the whole sequence is driven for you — not that review is skipped.

---

## Step 0 — Load pipeline state (always first)

Invoke the **state-loader** skill. It loads `.cursor/skills/state-loader/pipeline-config.json` and, if an epic is already known from context, that epic's `state.json`. This is what makes the flow resumable across sessions and across developers.

---

## Step 1 — Establish the epic (bootstrap or resume)

Branch on what state-loader found:

**A. Existing epic (`state.json` present)** → this is a RESUME. Record `EPIC_DIR` and `status`. Go to Step 2.

**B. Fresh start (no `state.json`)** → BOOTSTRAP:

1. **Get identity (one question):** ask for the Jira epic key (e.g. `IAM-123`) or a short manual identifier (e.g. `rate-limiting-user-userid`).
2. **Derive names:** `epic-name` = lowercase-hyphenated; `epic-id` = the Jira key, or the same as `epic-name` for the manual path. Set the **canonical** `EPIC_DIR = aidlc-docs/<epic-name>/`.
3. **Create `EPIC_DIR/state.json`:**
```json
{ "epic-id": "<epic-id>", "epic-name": "<epic-name>", "status": "not-started", "stories": {} }
```
4. **Create `EPIC_DIR/audit.md`** with the standard header and a bootstrap row — phase `init`, skill `aidlc-init`, action `Epic bootstrapped; state.json initialized at not-started.`, approver = current system username.
5. **`EPIC_DIR` is canonical.** Every downstream skill MUST read/write here. Do not allow a chained skill to spawn a second directory (e.g. `<epic-name>_<epic-id>/`) for the same epic.

---

## Step 2 — Route by status (state-machine driver)

Read the current `status` and route. Consult `transitions` in `pipeline-config.json` so every hop stays legal.

| Current status | Action |
|---|---|
| `not-started` | Run **Phase A** (scaffold), then **Phase A½** (vision), then **Phase B** (ADR), then **Phase C** (design). |
| `context-ready` | Skip Phase A. Run **Phase A½** (vision), then **Phase B**, then **Phase C**. |
| `inception-completed` | Skip Phases A and A½. Run **Phase B** (ADR), then **Phase C**. |
| `adr-completed` | Skip Phases A, A½, and B. Run **Phase C** (design). |
| `design-in-progress` | Resume **Phase C** where it left off. |
| `design-completed` | Goal already reached — go to **Step 5** (report, stop). |
| `implementation-*` / `review-*` / `shipped` | Beyond aidlc-init's scope. Report the current status and the relevant skills from `skills_by_state`, then stop. |

---

## Phase A — Context (chain `aidlc-epic-scaffold`)

Run only when `status = not-started`.

1. Invoke **aidlc-epic-scaffold**, passing the already-known epic identity and the canonical `EPIC_DIR` so it does **not** re-ask for input and does **not** create a differently-named directory.
2. Let it run its completeness check, review gate, and XML generation. On success it advances `status → context-ready` and writes its audit rows.
3. Do not proceed until scaffold reports context ready and `status = context-ready`.

---

## Phase A½ — Vision (chain `aidlc-vision-doc`)

Run when `status` is `context-ready` (or immediately after Phase A in a fresh run).

1. Invoke **aidlc-vision-doc**, passing `EPIC_DIR` and using conversation context from Phase A (no separate context-loader needed).
2. Output path must be `EPIC_DIR/vision.md`.
3. On Gate 2 approval, it advances `status → inception-completed` and writes its audit row.
4. Do not proceed until `vision.md` exists and `status = inception-completed`.

---

## Phase B — ADR (chain `aidlc-adr`)

Run when `status` is `inception-completed`.

1. Invoke **aidlc-adr**. It reads `EPIC_DIR/vision.md`, runs Gate 1 and Gate 2, writes `EPIC_DIR/adr.md`, compresses to `adr_decisions.xml`, and advances `status → adr-completed`.
2. Phase B includes the ADR system-prompt step (Step 8b inside `aidlc-adr` via `generate-system-prompts` ADR mode). Do not enter Phase C until `EPIC_DIR/system-prompts/adr_decisions.xml` exists.
3. Do not proceed until ADR reports complete and `status = adr-completed`.

---

## Phase C — Design (chain `aidlc-design-driven-dev`)

Run when `status` is `adr-completed` or `design-in-progress`.

1. If `status = adr-completed`, advance `status → design-in-progress` in `state.json` and append an audit row (phase `design`, skill `aidlc-init`, action `Entered design phase.`). This keeps resume accurate if the session ends mid-design.
2. Invoke **aidlc-design-driven-dev**. It reads `vision.md`, `context.xml`, and `adr_decisions.xml`, then drives **HLD → LLD(s) → EARS**, STOPPING for your approval at each phase and logging every approval to `audit.md`.
3. When the full HLD → all LLDs → all EARS chain is approved, advance `status → design-completed` and append an audit row (action `Design phase complete: HLD, LLDs, EARS approved.`).

---

## Step 5 — Report & hand off

Print the state-loader banner one final time (now at `design-completed`), summarize the artifacts created, and tell the user the design pipeline is complete. Point them to the next-phase skills listed under `skills_by_state["design-completed"]` in the config.

---

## Resumability contract

- **Anyone can re-run `aidlc-init` at any time.** Step 0 + Step 2 guarantee it resumes from the true `status` instead of restarting or duplicating work.
- `state.json` is the **single source of truth** for pipeline position; `audit.md` is the human ledger. Keep them in lockstep on every status change.
- Status may only move to a value listed in `transitions[current].next` (or `.rollback`). Never invent a status.
