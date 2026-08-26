---
name: aidlc-init
description: Orchestrator entry point for the AI-DLC pipeline. From one command it bootstraps the epic and chains state-loader -> aidlc-epic-scaffold (context) -> aidlc-vision-doc (vision) -> aidlc-adr (ADR + adr_decisions.xml) -> aidlc-design-driven-dev (HLD -> LLD -> EARS) -> aidlc-jira-story-breakdown (prioritization) -> aidlc-tdd (per-story implementation loop) -> aidlc-gacr (PR gate), pausing only at human approval gates and the PR-open pause. Fully resumable. Use when the user says "aidlc-init" or wants to start/resume an epic end-to-end.
---

# aidlc-init

Single entry point for the AI-DLC pipeline. From one command this drives the full chain and is **resumable** — re-running always picks up from the current `state.json` status rather than restarting.

```
aidlc-init
  └─ Step 0: state-loader              (load pipeline-config + epic state)
  └─ Step 1: bootstrap / resume        (create state.json @ not-started, or detect existing)
  └─ Step 2: route by status           (state-machine driver)
  └─ Phase A:   aidlc-epic-scaffold         → status: context-ready
  └─ Phase A½: aidlc-vision-doc            → status: inception-completed
  └─ Phase B:   aidlc-adr                  → status: adr-completed (includes adr_decisions.xml)
  └─ Phase C:   aidlc-design-driven-dev    → status: design-completed
  └─ Phase D:   aidlc-jira-story-breakdown → status: prioritization-completed
  └─ Phase E:   aidlc-tdd (story loop)     → status: implementation-completed
  └─ Phase F:   aidlc-gacr (PR gate)       → review approved; shipped = PR merged (not this skill)
```

**Workers vs orchestrator.** `aidlc-jira-story-breakdown`, `aidlc-tdd`, and `aidlc-gacr` remain standalone skills and may be run directly. This orchestrator *sequences* them. It does not reimplement their gates. `aidlc-tdd` stays the **per-story** worker; init runs it in a loop. `aidlc-gacr` stays the **PR gate**; init invokes it once after implementation is complete and a PR (or `dev/IAM-*` vs `origin/main` diff) exists.

## What this produces

By the end of a full run (GACR user-approved, `status = review-in-progress`): the XML system prompts (`context.xml` + `adr_decisions.xml`), `vision.md`, `adr.md`, `high-level-design.md` and every feature `LLD.md` (Full tier only — skipped for the Lightweight tier), every `*-EARS.md`, a populated `stories` map, implemented and tested stories, GACR review evidence in `audit.md`, and a complete `audit.md` trail — each artifact and iteration approved by you at its gate. **`shipped` is not written here** — that hop is "PR merged."

> **Approval gates are human.** This orchestrator *sequences* the skills and **pauses at every approval gate** (and at the Phase F PR-open pause). It never auto-approves, never auto-pushes, and never auto-merges. Nothing lands on disk without your explicit "approved". "Boom" means the whole sequence is driven for you — not that review is skipped.

---

## Step 0 — Load pipeline state (always first)

Invoke the **state-loader** skill. It loads `.cursor/skills/state-loader/pipeline-config.json` and, if an epic is already known from context, that epic's `state.json`. This is what makes the flow resumable across sessions and across developers.

---

## Step 1 — Establish the epic (bootstrap or resume)

Branch on what state-loader found:

**A. Existing epic (`state.json` present)** → this is a RESUME. Record `EPIC_DIR` and `status`. Go to Step 2.

**B. Fresh start (no `state.json`)** → BOOTSTRAP:

1. **Get identity (one question):** ask for the Jira epic key (e.g. `IAM-123`) or a short manual identifier (e.g. `rate-limiting-user-userid`).
2. **Derive names:** `epic-name` = lowercase-hyphenated; `epic-id` = the Jira key, or the same as `epic-name` for the manual path. Set the **canonical** `EPIC_DIR = aidlc-docs/<epic-name>_<epic-id>/` (e.g. `IAM-123: Rate Limiting` → `aidlc-docs/rate-limiting_IAM-123/`).
3. **Create `EPIC_DIR/state.json`:**
```json
{ "epic-id": "<epic-id>", "epic-name": "<epic-name>", "status": "not-started", "stories": {} }
```
4. **Create `EPIC_DIR/audit.md`** with the standard header and a bootstrap row — phase `init`, skill `aidlc-init`, action `Epic bootstrapped; state.json initialized at not-started.`, approver = current system username.
5. **`EPIC_DIR` is canonical.** Every downstream skill MUST read/write here. Do not allow a chained skill to spawn a second directory (e.g. `aidlc-docs/<epic-name>/`) for the same epic.

---

## Step 2 — Route by status (state-machine driver)

Read the current `status` and route. Consult `transitions` in `pipeline-config.json` so every hop stays legal.

| Current status | Action |
|---|---|
| `not-started` | Run **Phase A** → **A½** → **B** → **C** → **D** → **E** → **F**. |
| `context-ready` | Skip Phase A. Run **A½** → **B** → **C** → **D** → **E** → **F**. |
| `inception-completed` | Skip A and A½. Run **B** → **C** → **D** → **E** → **F**. |
| `adr-completed` | Skip A–B. Run **C** → **D** → **E** → **F**. |
| `design-in-progress` | Resume **Phase C**, then **D** → **E** → **F**. |
| `design-completed` | Skip A–C. Run **Phase D** → **E** → **F**. |
| `prioritization-completed` | Skip A–D. Run **Phase E** → **F**. |
| `implementation-in-progress` | Resume **Phase E** (story loop), then **F**. |
| `implementation-completed` | Skip A–E. Run **Phase F** (PR pause, then GACR). |
| `review-in-progress` | Resume **Phase F**. If `audit.md` already has a user-approved GACR complete row, skip to **Step 5**. |
| `shipped` | Terminal — go to **Step 5**. |

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
2. Invoke **aidlc-design-driven-dev**. It reads `vision.md`, `context.xml`, and `adr_decisions.xml`, then first assesses a **complexity tier**: large / multi-feature work runs the full **HLD → LLD(s) → EARS**; a minor bug or small story runs the **Lightweight tier** (skips HLD and LLD, produces **EARS only**). Each phase that runs STOPS for your approval and is logged to `audit.md`.
3. When the design phases for the chosen tier are approved (full HLD → all LLDs → all EARS, or **EARS-only** for the Lightweight tier), advance `status → design-completed` and append an audit row (action `Design phase complete: <phases run> approved.`).

---

## Phase D — Prioritization (chain `aidlc-jira-story-breakdown`)

Run when `status = design-completed`.

1. Invoke **aidlc-jira-story-breakdown**, passing `EPIC_DIR`. It breaks approved HLD/LLD/EARS into tracer-bullet vertical slices, pauses for your approval of the numbered breakdown, writes the `stories` map (`ears_ref`, `lld_ref`, `blockedBy`), and advances `status → prioritization-completed`.
2. Do not proceed until `status = prioritization-completed` and `stories` is non-empty.
3. Do **not** rewrite the map if `status` is already `implementation-in-progress` or later — Phase D is skipped on those resumes.

---

## Phase E — Implementation (loop `aidlc-tdd`)

Run when `status` is `prioritization-completed` or `implementation-in-progress`.

`aidlc-tdd` is the per-story worker. This phase is a **story loop**, not a single invocation. Init never implements code itself.

1. Re-read `EPIC_DIR/state.json` `stories` at the start of every iteration.
2. If **every** story is `status=done`, go to step 6 (no TDD invocation). If Step 5.5's audit row is missing, invoke TDD Step 5.5 only, then hop.
3. **Frontier:** `todo` stories whose `blockedBy` ids are all `status=done` (empty `blockedBy` is immediately claimable). Do not start a gated story early.
4. If there is no frontier but unfinished stories remain (`blocked`, `on-hold`, or gated `todo`): stop, report the blockers, and go to **Step 5** (partial). Do not enter Phase F.
5. **Pick `STORY_ID`:**
   - One frontier story → pass that id to `aidlc-tdd`.
   - Several frontier stories → list them and ask once which to claim (do not guess). After the user picks, subsequent single-frontier iterations may continue without re-asking.
   - A story is already `in-progress` → treat as resume of this session only after the user confirms it is theirs (TDD's claim check). If it is another agent/session, skip it and pick a different frontier `todo`.
   - User says pause / stop → leave remaining stories as `todo`, keep epic `status` at `implementation-in-progress`, and go to **Step 5** (partial). Do not enter Phase F.
6. Invoke **aidlc-tdd**, passing `EPIC_DIR` and `STORY_ID` so it does **not** re-ask which story. Let it run claim → seams → branch → red/green → test audit → close-out. All of TDD's human gates still apply.
7. After TDD reports `STORY COMPLETE`, loop to step 1.
8. When every story is `status=done`:
   - TDD must have run **Step 5.5** (vision Success Criteria → metrics/tests in `audit.md`). If that audit row is missing, invoke TDD's Step 5.5 before hopping.
   - Advance epic `status → implementation-completed` and append an audit row (phase `implementation`, skill `aidlc-init`, action `Implementation complete; all stories done; success-criteria measurement recorded.`).
9. **Concurrency:** this loop serializes stories in *this* session. Other `aidlc-tdd` runs against the same epic still use TDD's claim. Never claim a story that is already `in-progress` or `done`.

---

## Phase F — Review (PR pause, then chain `aidlc-gacr`)

Run when `status` is `implementation-completed` or `review-in-progress`.

`aidlc-gacr` is the PR-gate worker. Init does not critique the diff itself.

1. **Already approved?** If `status = review-in-progress` and `audit.md` has a user-approved GACR complete row, skip to **Step 5**.
2. **PR-open pause** (mandatory when `status = implementation-completed`). The `implementation-completed → review-in-progress` trigger is "PR opened."
   - Ask the user to confirm the review target: an existing PR URL, or the current `dev/IAM-*` branch vs `origin/main`.
   - **Do not** `git push`, `gh pr create`, or merge unless the user explicitly asks in this turn.
   - If they ask to open the PR, do that, then continue. If they paste a URL or confirm the branch diff, continue. If they decline, stay at `implementation-completed`, write no hop, and go to **Step 5** (paused before review).
3. Invoke **aidlc-gacr**, passing `EPIC_DIR` and the confirmed target. On the hop from `implementation-completed`, GACR advances `status → review-in-progress` and writes its audit row. Iteration 1 critiques the existing PR/branch diff; later iterations revise against findings. Every iteration pauses for your audit.
4. Do not proceed to **Step 5** as "review done" until GACR reports user-approved complete.
5. **Never** advance `status` to `shipped`. That hop is "PR merged." Tell the user to merge after GACR is approved.

---

## Step 5 — Report & hand off

Print the state-loader banner for the **current** `status`. Summarize artifacts produced this run. Then:

| Status | What to tell the user |
|---|---|
| `review-in-progress` (GACR approved) | Review pipeline complete. Merge the PR to reach `shipped`. GACR / init do not write `shipped`. |
| `implementation-completed` (user declined PR) | Implementation complete. Re-run `aidlc-init` (or `aidlc-gacr`) when a PR exists. |
| `implementation-in-progress` (user paused the story loop) | Remaining frontier stories are still `todo`. Re-run `aidlc-init` or `aidlc-tdd` to continue. |
| `shipped` | Terminal. No further skill execution. |

Do not invent a next skill beyond what `skills_by_state` lists for the current status.

---

## Resumability contract

- **Anyone can re-run `aidlc-init` at any time.** Step 0 + Step 2 guarantee it resumes from the true `status` instead of restarting or duplicating work.
- `state.json` is the **single source of truth** for pipeline position; `audit.md` is the human ledger. Keep them in lockstep on every status change.
- Status may only move to a value listed in `transitions[current].next` (or `.rollback`). Never invent a status.
- Phases D–F are skipped when `status` is already past them. Phase E resumes mid-loop from `stories` + TDD's claim check. Phase F resumes mid-review from GACR's iteration audit rows.
