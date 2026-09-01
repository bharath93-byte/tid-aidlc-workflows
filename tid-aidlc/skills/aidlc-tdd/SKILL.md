# AIDLC TDD

Drives **one implementation story** from requirements to tested code. TDD is not a phase bolted onto delivery here — it **is** the delivery mechanic: the red → green loop, run one seam at a time, is what "Implement" means in this skill (hypothesis-driven execution). Every step below either sets that loop up correctly (analysis, seam agreement) or checks that it was actually followed (test audit). When chained from **`aidlc-init`**, init runs this skill in a per-story loop (Phase E). When the epic's last story closes, run Steps **5.5 → 5.6 → 5.7 → 5.8** (vision measurement, construction illustrative example, manual test cases, **construction GACR**) before `implementation-completed`. **aidlc-init** Phase F is PR-open only and does not re-run GACR.

**Announce at start:** "Running **aidlc-tdd** for `{story}`."

## Core principles

- **Design docs are the alignment, not a fresh grill every time.** If the story has an `ears_ref` / `lld_ref` in `state.json`, that EARS section's bullets *are* the acceptance criteria. `{EPIC_DIR}/illustrative-example.md` (when present) is **scenario context** for the primary happy path — not a second spec and not extra AC. Scoped-questioning (Step 2) fills only what design left genuinely open — it does not re-litigate settled decisions.
- **Construction must load `coding-guidelines` before any production or test code is written.** Read `.cursor/skills/coding-guidelines/SKILL.md` (source: `tid-aidlc/skills/coding-guidelines/SKILL.md`) as a hard constraint. YAGNI: implement only what this story's `lld_ref` / `ears_ref` specify (Lightweight: EARS + ADR). The illustrative example does not widen that set.
- **TDD is the implementation mechanic, not a separate phase.** There is no "write code, then bolt on tests" step. Tests are written first, one seam at a time, inside Step 3 itself.
- **Execution is hypothesis-driven (RPT loop).** Each red → green cycle is a falsifiable hypothesis: the failing test states the predicted behavior; the minimal implementation is the intervention; the green result plus the slice log are the evidence. Seams keep the hypothesis observable at a public boundary. Do not skip red, batch into horizontal slices, or advance without that evidence.
- **Measurement closes the vision loop.** When the epic reaches `implementation-completed`, map every `vision.md` Success Criteria row to concrete metrics/tests and record the mapping in `audit.md` (Step 5.5). Story-level AC proves the slice; vision-level criteria prove the epic delivered what it set out to measure.
- **Fresh context per role.** Analysis, implementation, and test audit each run as isolated Task sub-agents so orchestration context never pollutes any of them.
- **Seams are agreed once, up front, and reused for the whole story.** No test is written at a seam that wasn't confirmed in Step 2.
- **Evidence before advancement.** Each step must produce concrete proof (failing test → passing test, coverage/audit findings) before the next one starts.
- **State stays in sync.** The story's entry in `state.json` moves `todo → in-progress → done` (or `on-hold` when paused), with a matching `audit.md` row (via `aidlc-approve`) at the start and the close of the story.
- **Claim before you work.** Flipping a story to `in-progress` in `state.json` is a claim, not just a status label — it's how concurrent `aidlc-tdd` runs (or a human working in parallel) against the same epic avoid picking up and duplicating each other's story. Claim happens in Step 0, before any sub-agent work starts, not after alignment.
- **Work the frontier.** A `todo` story is claimable only when every id in its `blockedBy` array is `status=done` (empty `blockedBy` is immediately claimable). Do not start a gated story early.

## Inputs

*Before doing anything, invoke the `state-loader` skill* to load the pipeline config and epic state, unless this is a genuinely epic-less ad hoc task (see Step 0).

| Input | Source |
|-------|--------|
| A story already in `EPIC_DIR/state.json`'s `stories` map | Preferred — and required for tracked epic work. `ears_ref` points at the EARS bullets to satisfy, `lld_ref` at the design, `blockedBy` at the stories that must be `done` first |
| `{EPIC_DIR}/illustrative-example.md` | Scenario walkthrough of one primary path. Required when present on a governed epic (Gate 1 already ran). Not a second spec — do not expand scope beyond this story's EARS/LLD. Skip if absent (coherence-check-only, ungoverned hotfix) |
| Breakdown JSON (map empty) | Fallback only when `stories` is still `{}` — do not use this to bypass `aidlc-jira-story-breakdown` on a governed epic |
| Ad hoc task text | Hotfix path — no epic bookkeeping, alignment mostly skipped (see Step 0) |
| Jira key (`IAM-<number>`) | Required for branch/commit naming — resolve from the ticket, `state.json` epic key, or ask the user | FOR NOW ONLY HAVE tmp/test-(`IAM-<number>`) because we are testing. CRITICAL. NEVER NAME BRANCH NAME AS dev/(`IAM-<number>`) 

If none of the above is available: "What do you want to build? Paste the story id, ticket, EARS reference, or task description."

## Repo naming conventions

Follow the IAM repo's documented conventions (see `.github/copilot-instructions.md`). Never work on `main`/`master` without explicit user consent.

### Branches

All developer work branches use:

```
dev/IAM-<number>[-<optional-suffix>]
```

| Part | Rule |
|------|------|
| `dev/` | Required prefix for implementation branches |
| `IAM-<number>` | Jira ticket key (e.g. `IAM-6042`) — must match `IAM-<digits>` |
| `-<optional-suffix>` | Short kebab-case slug when disambiguation helps (e.g. `-fix-bug`, `-1`, `-counter-store`) |

**Examples:** `dev/IAM-6042`, `dev/IAM-6042-fix-bug`, `dev/IAM-323-1`, `dev/IAM-1234-short-desc`

**Deriving the branch name:**
1. Resolve `JIRA_KEY` (`IAM-<number>`) from the story ticket, epic key in `state.json`, or ask the user.
2. Optionally append a suffix derived from the story title (lowercase, hyphen-separated, ≤4 words).
3. If the user is already on a correctly named branch, confirm and reuse it — do not create a duplicate.

**Creating the branch** (after Step 2, before Step 3):

```bash
git fetch origin main
git checkout -b dev/IAM-<number>[-<suffix>] origin/main
```

If a branch for this ticket already exists locally or on origin, ask whether to check it out (resume) or create a new suffixed branch.

### Commits

Commit messages use:

```
[IAM-<number>] - "<description>"
```

| Part | Rule |
|------|------|
| `[IAM-<number>]` | Jira key in square brackets — use the sub-task key when one exists |
| `"<description>"` | Imperative, concise summary of what changed (quoted) |

**Examples:** `[IAM-6042] - "add sliding-window counter increment"`, `[IAM-5891] - "test: add dealer list devices sortBy coverage"`

Only commit when the user explicitly asks (per repo git rules). When they do, use this format.

## Step 0 — Load state, claim the story, and locate the requirements

1. Resolve `EPIC_DIR` via `state-loader`.
2. **Epic-status gate (tracked work):**
   - `prioritization-completed` or `implementation-in-progress` → proceed.
   - `design-completed` (typically empty `stories`) → stop. Tell the user to run `aidlc-jira-story-breakdown` (or re-run `aidlc-init` Phase D) first so the stories map is populated.
   - Earlier than `design-completed` → stop. Design is not locked yet.
   - Later than `implementation-in-progress` (`implementation-completed` / `review-*` / `shipped`) → stop unless the user is explicitly resuming a leftover story; report the current status and `skills_by_state`.
   - No epic at all (genuine hotfix / standalone task with no `aidlc-docs/` entry) → skip to step 8 (ungoverned path).
3. Determine `STORY_ID`:
   - If a story id was given (including when **aidlc-init** Phase E passed `STORY_ID`), look it up in `stories`. Do not re-ask which story.
   - If none was given but `stories` has entries, list only the **frontier** — `todo` stories whose `blockedBy` ids are all `status=done` (empty `blockedBy` counts as frontier) — and ask the user which to work (don't guess silently — picking the wrong story is itself duplicated work). Do not offer stories still gated by unfinished blockers.
4. **Claim check (avoids duplicate work across concurrent runs):** look at the resolved story's current `status` in `state.json` *before* touching anything else:
   - `done` → tell the user this story is already complete and stop.
   - `in-progress` → do **not** silently proceed as if it were free. Show the most recent `audit.md` row for this `STORY_ID` and ask the user to confirm whether this is a resume of their own interrupted run (proceed via **Resume support** below) or a collision with another agent/session already working it (if the latter, stop).
   - `on-hold` → story is paused; do not auto-claim. Summarize the last `audit.md` row and ask whether to resume (set `in-progress` and continue) or leave on hold and pick another story.
   - `blocked` → tell the user this story is blocked and stop unless they explicitly override.
   - `todo` whose `blockedBy` ids are **not** all `status=done` → **not claimable**. List the remaining unfinished blockers and stop. Do not silently override.
   - `todo` on the frontier (or story is untracked ad hoc work) → clear to claim.
5. **Claim:** immediately set the story's `state.json` status to `in-progress` and append an `audit.md` row via `aidlc-approve` (phase `implementation`, action `Claimed {STORY_ID} for implementation.`) — **before** Step 1 dispatches any sub-agents. This is the write that makes the story unavailable to any other `aidlc-tdd` run reading the same `state.json`.
6. **Epic hop:** if the epic `status` is still `prioritization-completed`, this first successful claim meets the `prioritization-completed → implementation-in-progress` trigger. Advance epic `status` to `implementation-in-progress` and append a matching `audit.md` row via `aidlc-approve` (phase `implementation`, action `Entered implementation; claimed {STORY_ID}.`).
7. Read the EARS section (`ears_ref`) and the parent LLD (`lld_ref`) — this **is** the requirements contract, not a summary of it. If `lld_ref` is `""` (Lightweight / EARS-only), skip the LLD. Then, if `{EPIC_DIR}/illustrative-example.md` exists, Read it as **scenario context** (same epic file for every story; do not generate a new example). Pass EARS/LLD first, then the example last, labeled scenario-only. If the file is absent, proceed without it — do not block. Only if the stories map is empty and this is the ungoverned/hotfix path may a pasted ticket's `whatToBuild` + `acceptanceCriteria` stand in.
8. If there is no epic at all (a genuine hotfix or standalone task with no `aidlc-docs/` entry), proceed ungoverned: skip `state.json`/`audit.md` bookkeeping (including the claim and epic hop above) for the rest of this run, and say so explicitly so the user knows this story isn't being tracked or protected from collision.
9. If `STORY_ID` wasn't already set by step 3, set it now (the state.json key, ticket id, or a generated `T-{YYYYMMDD-HHMM}` for untracked ad hoc work).

Print: `[aidlc-tdd] [{STORY_ID}] Step 0 complete — story claimed, requirements located.`

## Step 1 — Codebase & test-landscape analysis

Dispatch two read-only `explore` Task sub-agents in parallel:

**App Code Analyzer:** "Given these requirements: `{requirements}` (EARS/LLD are the contract; `illustrative-example.md` if included is scenario-only — do not expand scope). Locate every file/layer that will need to change. Study adjacent implementations for patterns — error handling, validation, auth, data access. Find reusable utilities. Flag edge cases visible from code. Align file maps with the designed flow and payloads. Return a structured analysis."

**Test Analyzer:** "Given these requirements: `{requirements}` (EARS/LLD are the contract; `illustrative-example.md` if included is scenario-only — do not expand scope). Map the existing test landscape: frameworks, conventions, fixtures, builders, coverage gaps. Most importantly, propose **candidate seams** — the public interfaces/boundaries where this behavior could be observed and tested without reaching into internals. Prefer seams on the illustrative-example happy path when present. Return a structured analysis."

Synthesize both into a short summary in chat. Do not write this to disk by default — it's working context for Step 2, not a persisted artifact (persist only if the user asks for a reference doc, under `EPIC_DIR/implementation/{STORY_ID}-analysis.md`).

Print: `[aidlc-tdd] [{STORY_ID}] Step 1 complete — codebase analysis done.`

## Step 2 — Confirm seams and close remaining gaps

This is the mandatory alignment gate, and where the seam rule lives:

> A **seam** is the public boundary you test at: the interface where you observe behavior without reaching inside. Tests live at seams, never against internals. **No test is written at an unconfirmed seam** — you can't test everything, so agreeing the seams up front is how testing effort lands on the critical paths and complex logic instead of every edge case.

1. Present the acceptance criteria (from `ears_ref` / ticket) alongside the candidate seams Step 1 found.
2. Apply `tp-ai-kit-scoped-questioning`'s mechanics **inline** (one topic at a time, 2–3 options with a recommended default, grounded in the Step 1 analysis) for whatever is still ambiguous — do not ask about anything the EARS/LLD already settled.
3. Explicitly ask: *"What's the public interface, and which seams should we test?"* — and get the user's confirmation on the final seam list before Step 3 starts.
4. **Skip this step's questioning** only if the user says "skip alignment" or "hotfix" — proceed to Step 3 with the seams the analysis proposed, flagged as unconfirmed.

**Gate:** the user confirms the seam list and any open questions are resolved. On confirmation, if this story is tracked (status is already `in-progress` from Step 0's claim): append an `audit.md` row via `aidlc-approve` (phase `implementation`, action `Seams confirmed for {STORY_ID}: {seam list}`).

Print: `[aidlc-tdd] [{STORY_ID}] Step 2 complete — seams confirmed.`

## Step 2.5 — Create or confirm branch

Run this gate after seams are confirmed and before any implementation sub-agent is dispatched.

1. Resolve `JIRA_KEY` (`IAM-<number>`) — from the ticket, epic key, or by asking the user. Do not proceed without it unless this is an ungoverned hotfix (Step 0).
2. Derive the branch name per **Repo naming conventions** above: `dev/IAM-<number>[-<suffix>]`.
3. Check current branch (`git branch --show-current`):
   - Already on the correct `dev/IAM-*` branch → confirm with the user and proceed.
   - On `main`/`master` or an unrelated branch → create or checkout the derived branch from `origin/main`.
   - A `dev/IAM-*` branch for the same ticket already exists → ask: resume that branch, or create a new suffixed branch?
4. Never commit to `main`/`master` without explicit user consent.

Print: `[aidlc-tdd] [{STORY_ID}] Step 2.5 complete — branch: {branch-name}.`

## Step 3 — Implement via the red → green loop

Dispatch `implementer` as a `generalPurpose` Task sub-agent. Pass: repo root + branch, the confirmed seam list, the requirements (EARS/LLD first), path to `{EPIC_DIR}/illustrative-example.md` when present with the line **"implement and test only `ears_ref`/`lld_ref`; use the example to match the primary scenario, not to expand scope"**, an instruction to **Read `.cursor/skills/coding-guidelines/SKILL.md` first** as a hard constraint, and this discipline verbatim:

**What a good test is.** Tests verify behavior through public interfaces, not implementation details. Code can change entirely; tests shouldn't. A good test reads like a specification — "user can checkout with valid cart" tells you exactly what capability exists — and survives refactors because it doesn't care about internal structure.

**Anti-patterns to never produce:**
- **Implementation-coupled** — mocks internal collaborators, tests private methods, or verifies through a side channel (querying the database instead of using the interface). The tell: the test breaks when you refactor but behavior hasn't changed.
- **Tautological** — the assertion recomputes the expected value the way the code does (`expect(add(a, b)).toBe(a + b)`, a hand-derived snapshot, a constant asserted equal to itself), so it passes by construction. Expected values must come from an independent source of truth — a known-good literal, a worked example, the spec.
- **Single-variant of a parameterized type** — production takes a discriminator (`signal`, `kind`, `resource_type`) but tests only exercise one sibling (`azp` only). A hardcoded prefix like `f"rl#client#{value}#{endpoint}"` then green-passes. Write the second variant *and* an equal-value collision case (`azp` vs `sub` with the same id → distinct keys) in red, then implement by interpolating the parameter (`rl#{signal}#…`).
- **Horizontal slicing** — writing all tests first, then all implementation. Bulk tests verify *imagined* behavior and go insensitive to real changes. Work in **vertical slices** instead: one test → one implementation → repeat, each test a tracer bullet that responds to what the last cycle taught you.

**Rules of the loop (hypothesis → evidence):**
- Red before green. The failing test *is* the hypothesis ("this behavior should hold"); only then write enough code to pass it. Don't anticipate future tests or add speculative features.
- One slice at a time. One seam, one test, one minimal implementation per cycle — each cycle is one falsifiable experiment, not a batch.
- Evidence is the green result plus the slice log entry. "Tests pass at the end" without a per-cycle log is not enough to claim the loop was followed.
- Refactoring is not part of the loop — it is not part of the red → green cycle. Construction close-out review is **`aidlc-gacr`** at Step 5.8 (after all stories), not TDD Step 5 per-story close-out.
- If a seam not on the agreed list turns out to be necessary, **stop and escalate** to the orchestrator rather than silently expanding scope.

The implementer must not declare Step 3 complete until, locally: format/lint is clean, the build passes, and every test it wrote passes. It must report back a **slice log** (seam → test name → outcome) alongside PASS/FAIL, files touched, and build/test commands + results — this is the evidence that the loop was actually followed cycle-by-cycle, not just "tests pass" at the end.

**On success:** print `[aidlc-tdd] [{STORY_ID}] Step 3 complete — implementer: done.`
**On failure or scope escalation:** stop and bring it to the user.

## Step 4 — Test & anti-pattern audit

This step **audits**, it does not author net-new coverage wholesale — that would reintroduce horizontal slicing. Dispatch `test-auditor` as a `generalPurpose` Task sub-agent after Step 3 passes. Pass the slice log, the confirmed seam list, the full unit/integration suite, path to `{EPIC_DIR}/illustrative-example.md` when present (scenario-not-spec), and an instruction to Read `.cursor/skills/coding-guidelines/SKILL.md`. It must:

1. Run the full suite and report counts.
2. Check every test the implementer added against the anti-patterns above (implementation-coupled, tautological, single-variant of a parameterized type, horizontal slicing) **and** coding-guidelines anti-patterns (magic numbers, swallowed errors, deep nesting, unused utilities) and flag violations.
3. Cross-check the slice log against the confirmed seam list: flag any agreed seam with no test, and any test that reaches an interface outside the agreed seams.
4. It **may** add a single missing test for an already-agreed seam if genuinely absent (still red-before-green) — it **must not** invent new seams or bulk-add tests for untested internals.

**If it fails:** return to `implementer` with the findings. Maximum 3 implementer ↔ test-auditor cycles before escalating to the user.

**On success:** print `[aidlc-tdd] [{STORY_ID}] Step 4 complete — test-auditor: PASS ({N} passed, 0 failed, 0 anti-pattern findings).`

**Optional second-tier/E2E:** if the repo documents a second-tier suite (e.g. `tests/automation/`) and the story is tagged to require it, dispatch `test-auditor` again for that suite. Otherwise: `[aidlc-tdd] [{STORY_ID}] second-tier suite skipped — none documented or required.`

## Step 5 — Close out

1. If tracked: set the story's `state.json` status to `done`. If every story in the `stories` map is now `done`, note that the `implementation-in-progress → implementation-completed` transition is **not** met until Steps **5.5 → 5.6 → 5.7 → 5.8** are approved. **Run those steps before treating the epic as implementation-complete.** Do not flip the epic-level `status` to `implementation-completed` yourself; **aidlc-init** Phase E writes that hop after Step 5.8 (standalone: tell the user they may advance, or re-run `aidlc-init` for Phase F PR-open).
2. Append an `audit.md` row via `aidlc-approve` (phase `implementation`, action `{STORY_ID} implemented and tested.`).
3. Summarize what was built against the acceptance criteria, list any deferred items or known gaps, and ask the user to confirm before calling the story done.
4. If the user asks to commit, use the commit message format from **Repo naming conventions**: `[IAM-<number>] - "<description>"`.

Print (standalone):
```
[aidlc-tdd] [{STORY_ID}] STORY COMPLETE — implementation and tests finished.
Branch: dev/IAM-<number>[-<suffix>]
Commit format: [IAM-<number>] - "<description>"
Next: start the next frontier story with aidlc-tdd; after the last story, Steps 5.5–5.8 (measurement, construction example, manual TCs, construction GACR), then re-run aidlc-init for Phase F (PR-open only).
```

Print (when invoked by **aidlc-init** with `STORY_ID`):
```
[aidlc-tdd] [{STORY_ID}] STORY COMPLETE — implementation and tests finished.
Next: returning to aidlc-init (next frontier story, or Steps 5.5–5.8 after last story).
```

If this was the last open story, continue immediately to Step 5.5.

## Step 5.5 — Vision success-criteria measurement (epic gate)

**When:** only when every story in `stories` is `done` and the epic is about to run construction close-out (Steps 5.6–5.8) before `implementation-completed`. Skip for ungoverned hotfixes (no epic / no `vision.md`).

This is a **lightweight measurement checkpoint**, not a new test authoring phase. It answers: *did we instrument / cover what vision said success looks like?*

1. Read `EPIC_DIR/vision.md` § **Success Criteria** (Criterion | Measurement | Target).
2. For each criterion, produce a concrete mapping row:

   | Vision criterion | Concrete metric / test | Evidence location | Status |
   |------------------|------------------------|-------------------|--------|
   | *(from vision.md)* | Named test(s), suite command, or observable metric (e.g. Datadog query, Allure suite, pytest node id) | Path, command, or dashboard link | `covered` / `partial` / `gap` |

3. Prefer evidence already produced by Steps 3–4 (slice log, agreed seams, suite results). Do **not** invent new seams or bulk-add tests here. If a criterion has no mapped evidence, mark `gap` and call it out — the user decides whether to defer, open a follow-up story, or accept the gap before advancing.
4. Present the table in chat for a quick human confirm (same approval phrases as elsewhere: approved / looks good / finalized).
5. On confirmation, append one `audit.md` row via `aidlc-approve`:
   - phase: `implementation`
   - action: `Success-criteria measurement mapped for implementation-completed: {N} covered, {M} partial, {K} gap. {one-line summary of gaps or "no gaps"}.`
   - Optionally persist the full table under `EPIC_DIR/implementation/success-criteria-measurement.md` if the user wants a durable artifact; the audit row is the required record.
6. Only after this row exists: continue to **Step 5.6**. **Do not** flip epic `status` to `implementation-completed` — `aidlc-init` Phase E does that hop after Steps 5.6–5.8. Standalone: continue 5.6 → 5.7 → 5.8, then remind the user they may advance (or re-run `aidlc-init` for the PR-open pause).

Print: `[aidlc-tdd] Step 5.5 complete — vision success criteria mapped to metrics/tests; audit.md updated.`

## Step 5.6 — Construction illustrative example with corner cases (epic gate)

**When:** every story in `stories` is `done` and Step 5.5's audit row exists. Epic-level, not per-story (and not per-LLD). Skip for ungoverned hotfixes (no epic).

**Artifact:** `{EPIC_DIR}/illustrative-example-construction.md`. Same happy-path spine as `{EPIC_DIR}/illustrative-example.md` (already used in the TDD loop), **plus a required Corner Cases section** grounded in implemented code:

- Each LLD Edge Case and relevant EARS negative/exception
- Fail-open / fail-closed as the ADR/LLD states
- Empty/malformed input, missing dependency, mixed config/rollout if the design has them
- Pointers to real files, routes, tests, or log/metric names — not design-only fiction

Use [illustrative-example-construction-template.md](../aidlc-design-driven-dev/references/illustrative-example-construction-template.md).

**Approval:** present the doc, stop, wait for approved / looks good / finalized. On confirmation, append via **`aidlc-approve`** (`phase: implementation`, action `Construction illustrative example with corner cases generated and approved.`). Do not proceed to 5.7 until that row exists.

Print: `[aidlc-tdd] Step 5.6 complete — illustrative-example-construction.md approved.`

## Step 5.7 — Manual regression test cases (epic gate)

**When:** Step 5.6 approved. Still **before** `implementation-completed`. Skip for ungoverned hotfixes.

Chain **`aidlc-manual-test-cases`** with `EPIC_DIR` already in context (do not re-ask epic). That skill writes `{EPIC_DIR}/manual-test-cases.json` and `.xlsx` and **stops for approval**. Do not proceed to 5.8 until `audit.md` has action `Manual regression test cases generated and approved.`

Print: `[aidlc-tdd] Step 5.7 complete — manual test cases approved.`

## Step 5.8 — Construction GACR (epic gate)

**When:** Step 5.7 approved. All stories `done`. Still `implementation-in-progress`. Skip for ungoverned hotfixes (GACR may still run ad-hoc if the user asks).

Chain **`aidlc-gacr`** in **construction mode**: target the current `dev/IAM-*` (or implementation branch) vs `origin/main`. A PR is **not** required. Construction GACR **must not** hop `status` to `review-in-progress`.

Do not treat this epic as implementation-complete until `audit.md` has a user-approved construction GACR close-out row (`Construction GACR approved.` and/or `GACR complete for {target}: approved after {N} iteration(s).`).

Print: `[aidlc-tdd] Step 5.8 complete — construction GACR approved.`

**Standalone after 5.8:** tell the user they may advance `status → implementation-completed`, or re-run `aidlc-init` for Phase F (PR-open only). **Do not** hop epic status yourself unless you are **aidlc-init** Phase E.

## Sub-agent dispatch rules

Every `implementer` and `test-auditor` dispatch **must** be a `generalPurpose` Task sub-agent for context isolation; analysis in Step 1 uses `explore`. Each prompt must include: repo root + branch (`dev/IAM-<number>[-<suffix>]`), full requirements text, the confirmed seam list, paths to `ears_ref`/`lld_ref` when present, path to `{EPIC_DIR}/illustrative-example.md` when present (with "implement and test only `ears_ref`/`lld_ref`; use the example to match the primary scenario, not to expand scope"), path to `.cursor/skills/coding-guidelines/SKILL.md`, prior step outputs as summaries (not full dumps), and an instruction to return PASS/FAIL, artifacts touched, and blockers.

## Command discovery

Build/test/lint/format commands are discovered at runtime, in order: `README` (Getting Started/Development/Testing sections) → `package.json` scripts → `Makefile` → `pyproject.toml`/`poetry.lock`/`tox.ini` (and this repo's `ruff check --fix . && ruff format .` convention for Python) → `build.gradle`/`pom.xml` → `.github/workflows/`. Pass whatever is discovered to every sub-agent prompt. If nothing is discoverable, ask the user before proceeding.

## Resume support

Reached from Step 0's claim check once the user has confirmed this is their own interrupted run, not another agent's story:
1. `EPIC_DIR/state.json` — status is already `in-progress`; resume from the step implied by what's on disk (seams already confirmed → Step 2.5 or 3; branch already checked out → Step 3; implementation already reported → Step 4, etc.) rather than restarting.
2. `EPIC_DIR/audit.md` — the most recent row for this story indicates the last completed gate. If all stories are `done` but there is no success-criteria measurement row yet, resume at Step 5.5. If 5.5 exists but the construction-example row is missing, resume at 5.6. If 5.6 exists but the manual-TC row is missing, resume at 5.7. If 5.7 exists but the construction GACR complete row is missing, resume at 5.8.
3. Current git branch — if already on `dev/IAM-*`, skip Step 2.5 branch creation and confirm with the user.

Present a short resume summary before continuing. Do not re-run the Step 0 claim write (it's already claimed) — just proceed from the resumed step.

## Integration with other skills

| Skill | Relationship |
|-------|-------------|
| `state-loader` / `aidlc-init` | Supplies `EPIC_DIR`, epic status, and the `stories` map. **aidlc-init Phase E** loops this skill once per frontier story (passes `STORY_ID`), then requires Steps 5.5–5.8 before writing `implementation-completed`. Phase F is PR-open only. |
| `coding-guidelines` | In-loop construction constraint. Load before any production or test code. Not a GACR replacement. |
| `aidlc-design-driven-dev` | Upstream — produces the HLD/LLD/EARS and `illustrative-example.md` this skill implements against |
| `aidlc-jira-story-breakdown` | Upstream — governed prioritization phase; populates the `stories` map (`ears_ref`, `lld_ref`, `blockedBy`) and advances `status` to `prioritization-completed`. This skill consumes that map; it does not invent stories. |
| `aidlc-manual-test-cases` | Chained at Step 5.7 after Gate 2. Writes `manual-test-cases.json` / `.xlsx` and waits for approval. |
| `aidlc-gacr` | Chained at Step 5.8 in **construction mode** (no hop to `review-in-progress`). Phase F does not re-run GACR if the construction complete row exists. |
| `aidlc-vision-doc` / `vision.md` | Source of epic Success Criteria mapped in Step 5.5 |
| `aidlc-approve` | Used for every `audit.md` row this skill writes (Steps 0, 2, 5, 5.5, 5.6, and 5.8; 5.7 is written by `aidlc-manual-test-cases`) |

## When NOT to use this skill

- User only wants planning or design — send them to `aidlc-design-driven-dev` first, then come back once EARS is approved.
- Epic is at `design-completed` with an empty `stories` map — run `aidlc-jira-story-breakdown` first (or re-run `aidlc-init`, which chains it as Phase D) so RPT prioritization writes the map.
- Epic is at `implementation-completed` or `review-in-progress` — Phase F is PR-open only. Do **not** re-run construction GACR if the construction complete row exists. Re-run **`aidlc-init`** (or **`aidlc-gacr`** only if that row is missing).
- Genuine hotfix with no time for seam alignment — say "skip alignment" and proceed with the ad hoc path in Step 0/2.
- Repo is not a git repository — clarify workspace and pause.
- Requirements are completely unknown — gather them first (vision, ADR, EARS, or a ticket), then invoke this skill.
