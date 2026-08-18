---
name: aidlc-gacr
description: >-
  GACR (Guided Adversarial Code Review) — the default PR gate at review-in-progress.
  Runs a developer sub-agent and one or more critic sub-agents in a back-and-forth
  loop, with a human audit/approval gate at every iteration. Critics review against
  the team's distilled guidelines (guidelines/collective-feedback-guidelines.md).
  Roster (critics + developer), each persona's model, and the default iteration
  count are configurable in config/gacr-config.json. Use when the user says "gacr",
  "run GACR", wants an adversarial generate-and-critique review loop, pipeline
  status is review-in-progress, or wants code produced/revised until reviewers approve.
---

# aidlc-gacr — Guided Adversarial Code Review

Default **PR gate** at `review-in-progress`. Orchestrates a **generate → critique → audit →
revise** loop between two kinds of persona sub-agents:

- **1 Developer** — produces and revises the code.
- **1..N Critics** — each an independent persona (default: a Senior Engineer) that reviews
  the change against the team's guidelines and returns findings + a verdict.

The orchestrator (you) mediates the back-and-forth and **pauses for the human to audit and
approve at the end of every iteration**. The loop runs a configurable number of default
iterations and can be extended indefinitely until the user approves. When invoked as the
pipeline PR gate, iteration 1 critiques the **existing** PR/branch diff — the developer
only revises against findings; it does not implement a new task.

**Announce at start:** "Running **aidlc-gacr** — default PR gate at review-in-progress. {N} critic(s), developer, default {K} iterations."

## The roster is config-driven

Everything about who reviews and who codes lives in
[`config/gacr-config.json`](config/gacr-config.json):

- `developer` — one persona; `model` and `persona` file configurable.
- `critics[]` — **one or many**; each maps to exactly one persona (default: the Senior
  Engineer), with its own `model` and its own `guidelines[]` to load. Add a critic by adding
  an object to the array; disable one with `"enabled": false`.
- `loop` — `default_iterations`, `hard_cap_iterations`, approval/continue keywords, and
  `block_if_any_critic_requests_changes`.

Personas are defined under [`personas/`](personas/) following one shared "agent standard"
(persona header → mission → required inputs → operating principles → output contract):

- [`personas/developer.md`](personas/developer.md)
- [`personas/senior-engineer-critic.md`](personas/senior-engineer-critic.md)

`model` accepts `"inherit"` (default) or any slug the Task tool allows (e.g.
`"claude-opus-5-thinking-high"`). Whatever is configured is passed straight to the sub-agent's
`model` parameter.

---

## Step 0 — Load pipeline state, resolve roster, establish the target

*Before doing anything, invoke the `state-loader` skill* to load `pipeline-config.json` and
the epic's `state.json`, unless this is a genuinely epic-less ad hoc review (see the
ungoverned path below).

1. **Epic-status gate (tracked work):**
   - `review-in-progress` → proceed (this is the home state).
   - `implementation-completed` and a PR or `dev/IAM-*` branch-vs-`origin/main` diff exists →
     this meets the `implementation-completed → review-in-progress` trigger. Advance epic
     `status` to `review-in-progress` and append an `audit.md` row via `aidlc-approve`
     (`PHASE: review`, action `Entered review; GACR targeting {PR or branch}.`), then proceed.
   - `shipped` → stop. The epic is already live.
   - Earlier than `implementation-completed` → stop and report the current status and
     `skills_by_state`, unless the user explicitly asked for an ad-hoc/ungoverned review of
     a named diff.
   - No epic at all (genuine hotfix / standalone review with no `aidlc-docs/` entry) →
     ungoverned path: skip `state.json`/`audit.md` bookkeeping for the rest of this run, keep
     the audit inline in chat, and say so explicitly.
2. Read `config/gacr-config.json`. Resolve the `developer` and every critic where
   `enabled == true`. Read each referenced `persona` file and, for each critic, note its
   `guidelines[]` paths (relative to this skill directory).
3. **Guidelines prerequisite:** if any enabled critic's guidelines file is **missing** (default:
   `guidelines/collective-feedback-guidelines.md`), invoke **aidlc-review-guidelines-from-prs** first.
   That skill is standalone but **auto-wires** here when GACR is present and the file is absent
   — it writes corpus/clusters to `references/` and the markdown to `guidelines/`. Do not start
   the critique loop until guidelines exist, unless the user explicitly says to skip.
4. Establish **what is under review**:
   - **Pipeline PR gate** (`review-in-progress`, or just hopped from `implementation-completed`):
     default target is the open PR, or the current `dev/IAM-*` branch vs `origin/main`. Do
     **not** treat this as a task to implement.
   - **Ad-hoc / ungoverned** (no epic, or the user named a target): an explicit task/story
     ("implement X", a Jira story, an EARS/LLD ref), **or** an existing change (uncommitted
     diff, a branch, or named files). If it's ambiguous, ask one question: *"What should GACR
     work on — a task to implement, or an existing diff/branch/files to review?"*
5. Discover build/test/lint commands (README → `pyproject.toml`/poetry → `Makefile` →
   `.github/workflows/`); this repo uses `ruff check --fix . && ruff format .` for Python.
6. Set `ITERATION = 1` and `MAX = loop.default_iterations`.

Print: `[gacr] Step 0 — roster: developer(model=…), critics=[…]; target: …; default iterations=K.`

---

## Step 1 — Generate / Revise (Developer sub-agent)

**Pipeline PR gate, iteration 1:** skip this step. Critics review the existing PR/branch
diff in Step 2; the developer is dispatched only from iteration 2 onward, to revise against
findings. Print: `[gacr] Iteration 1 — developer skipped (PR-gate: existing diff).`

Otherwise, dispatch the **developer** as a Task sub-agent using its configured
`subagent_type` and `model`. The prompt MUST contain, verbatim where possible:

- The **full persona** from the developer's persona file.
- The task/acceptance criteria (ad-hoc iteration 1) **or** the previous iteration's
  aggregated critic findings table (iteration ≥ 2, including PR-gate revisions).
- Repo root + branch, and the discovered lint/test commands.
- The developer output contract (change summary, response-to-findings table, verification,
  files touched).

Isolate context: give summaries of prior rounds, not full transcripts. Capture the
developer's returned report.

Print: `[gacr] Iteration {ITERATION} — developer done ({files touched}).`

---

## Step 2 — Critique (Critic sub-agents, one per enabled critic)

For **each** enabled critic, dispatch a Task sub-agent (its configured `subagent_type` and
`model`). The prompt MUST contain:

- The **full persona** from that critic's persona file.
- An explicit instruction to **read its `guidelines[]` files first** (default:
  `guidelines/collective-feedback-guidelines.md`) and review against them.
- The developer's change this iteration (diff/files) + the task. On **PR-gate
  iteration 1**, pass the existing PR / `dev/IAM-*` vs `origin/main` diff — there is no
  developer revision yet.
- On iteration ≥ 2, the findings that critic raised last round, so it verifies fixes and
  doesn't re-raise resolved items.
- The critic output contract (verdict + findings table with severity, guideline reference,
  `file:line`, problem → fix).

If there are multiple critics, dispatch them **in parallel** (independent reviews). Collect
each critic's verdict and findings.

**Aggregate verdict:** with `loop.block_if_any_critic_requests_changes == true` (default),
the round is `REQUEST_CHANGES` if *any* critic requests changes; otherwise `APPROVE`.

Print: `[gacr] Iteration {ITERATION} — critics: {critic: verdict, …} → aggregate: {APPROVE|REQUEST_CHANGES}.`

---

## Step 3 — Audit gate (human approval, every iteration)

This gate is mandatory and runs **every** iteration — this is the "audit approval at each
iteration".

1. Present a concise **iteration audit**:
   - Developer: what changed + verification (lint/tests) results.
   - Each critic: verdict + findings table (grouped by severity).
   - Aggregate verdict and the count of open BLOCKER/MAJOR findings.
2. Record the iteration to the audit trail:
   - If running inside a tracked epic, append a row via **`aidlc-approve`** (`PHASE: review`,
     skill `aidlc-gacr`, action `Iteration {ITERATION}: {aggregate verdict}, {open blockers} open`).
     Approver stays `pending` until the user closes this iteration's gate.
   - Otherwise keep the audit inline in chat (ungoverned path — no epic to write to).
3. Ask the user to **audit and choose**:
   - Reply with an **approval keyword** (`approved`, `looks good`, `lgtm`, …) → go to Step 4.
   - Reply with a **continue keyword** (or give extra direction) → run another iteration.
   - Give targeted feedback → it's merged into the next developer prompt alongside the critic
     findings.

**Never auto-approve.** Only the user closes the loop.

---

## Loop control

After Step 3, decide whether to iterate again:

1. **User approved** → Step 4 (done).
2. **Aggregate is APPROVE but user hasn't said "approved"** → tell the user the critics are
   satisfied and ask for their audit approval (they may still request changes).
3. **`ITERATION < MAX`** → `ITERATION += 1`, return to Step 1 with the aggregated findings +
   any user feedback.
4. **`ITERATION == MAX`** → do **not** stop silently. Report that the default iteration budget
   is reached and ask: *"Extend for more rounds, or stop here?"* If the user extends, raise
   `MAX` (up to `loop.hard_cap_iterations`) and continue. The loop only ends on user approval
   or an explicit user stop.

---

## Step 4 — Close out

1. Summarize the whole run: iterations taken, final aggregate verdict, and any remaining
   MINOR/NIT items the user chose to accept.
2. List all files touched across iterations and the final lint/test status.
3. If inside a tracked epic, append a final `audit.md` row via **`aidlc-approve`**
   (`PHASE: review`, action `GACR complete for {target}: approved after {ITERATION} iteration(s).`,
   approver = the user). Do **not** advance `status` to `shipped` — that hop is "PR merged."
   Tell the user GACR is approved; merge the PR to reach `shipped`.
4. Do **not** commit, push, or merge unless the user explicitly asks (repo git rules).

Print:
```
[gacr] COMPLETE — {target}
Iterations: {ITERATION}   Critics: {list}   Final verdict: APPROVED (by user)
Files: {…}   Lint/tests: {…}
Next: merge the PR to reach shipped. GACR does not write shipped.
```

---

## Sub-agent dispatch rules

- Every developer and critic dispatch is a Task sub-agent for context isolation, using the
  `subagent_type` and `model` from `config/gacr-config.json`.
- Always inline the **full persona text** into the sub-agent prompt — the sub-agent does not
  share this orchestrator's context.
- Pass prior-round information as **summaries** (the findings table, a change summary), never
  full transcripts.
- Require each sub-agent to return its persona's output contract exactly, so Step 2/3 parsing
  is deterministic.

## Extending the roster

- **Add a critic** (e.g. a Security reviewer or a Test-quality reviewer): add an object to
  `critics[]` with a new `persona` file under `personas/` and, optionally, its own
  `guidelines[]`. No change to this SKILL.md is needed — the loop iterates over whatever is
  enabled.
- **Swap models per persona:** edit the `model` field for that entry.
- **Change how long it runs by default:** edit `loop.default_iterations`.

## Integration with other skills

| Skill | Relationship |
|-------|-------------|
| `state-loader` / `aidlc-init` | Supplies `EPIC_DIR` and epic status. This skill is the `review-in-progress` primary; `aidlc-init` does not chain it. |
| `aidlc-tdd` | Upstream — implements stories; after all stories are `done` and a PR is open, this skill is the PR gate. |
| `aidlc-approve` | Used for every `audit.md` row this skill writes (the `implementation-completed → review-in-progress` hop, each iteration, and close-out). `PHASE: review`. |
| `aidlc-review-guidelines-from-prs` | Upstream — derives review/coding guidelines from merged-PR review comments into `guidelines/collective-feedback-guidelines.md` when missing. GACR Step 0 invokes it automatically; that skill auto-wires outputs into this skill's `references/` and `guidelines/` when the file is absent. |

## When NOT to use this skill

- A single quick review with no revision loop — just review directly.
- Epic is earlier than `implementation-completed` and the user did not explicitly ask for an ad-hoc review of a named diff — finish TDD first.
- Epic is `shipped` — nothing left to review.
- No code target and no task to implement — clarify first.
- Repo is not a git repository — clarify the workspace.
