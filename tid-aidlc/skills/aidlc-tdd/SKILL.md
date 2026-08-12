# AIDLC TDD

Drives **one implementation story** from requirements to reviewed, tested code. TDD is not a phase bolted onto delivery here — it **is** the delivery mechanic: the red → green loop, run one seam at a time, is what "Implement" means in this skill. Every step below either sets that loop up correctly (analysis, seam agreement) or checks that it was actually followed (test audit, review).

**Announce at start:** "Running **aidlc-tdd** for `{story}`."

## Core principles

- **Design docs are the alignment, not a fresh grill every time.** If the story has an `ears_ref` / `lld_ref` in `state.json`, that EARS section's bullets *are* the acceptance criteria. Scoped-questioning (Step 2) fills only what design left genuinely open — it does not re-litigate settled decisions.
- **TDD is the implementation mechanic, not a separate phase.** There is no "write code, then bolt on tests" step. Tests are written first, one seam at a time, inside Step 3 itself.
- **Fresh context per role.** Analysis, implementation, test audit, and review each run as isolated Task sub-agents so orchestration context never pollutes any of them.
- **Seams are agreed once, up front, and reused for the whole story.** No test is written at a seam that wasn't confirmed in Step 2.
- **Evidence before advancement.** Each step must produce concrete proof (failing test → passing test, coverage/audit findings, reviewer verdict) before the next one starts.
- **State stays in sync.** The story's entry in `state.json` moves `todo → in-progress → done`, with a matching `audit.md` row (via `aidlc-approve`) at the start and the close of the story.
- **Claim before you work.** Flipping a story to `in-progress` in `state.json` is a claim, not just a status label — it's how concurrent `aidlc-tdd` runs (or a human working in parallel) against the same epic avoid picking up and duplicating each other's story. Claim happens in Step 0, before any sub-agent work starts, not after alignment.

## Inputs

*Before doing anything, invoke the `state-loader` skill* to load the pipeline config and epic state, unless this is a genuinely epic-less ad hoc task (see Step 0).

| Input | Source |
|-------|--------|
| A story already in `EPIC_DIR/state.json`'s `stories` map | Preferred path — its `ears_ref` points at the EARS bullets to satisfy, `lld_ref` at the design |
| A ticket produced by `aidlc-jira-story-breakdown` | The JSON ticket shape (`summary`, `whatToBuild`, `acceptanceCriteria`, `blockedBy`) or a live Jira key via the E-Tools MCP |
| Ad hoc task text | Hotfix path — no epic bookkeeping, alignment mostly skipped (see Step 0) |
| Branch name | Confirm before Step 3; never commit to `main`/`master` without explicit consent |

If none of the above is available: "What do you want to build? Paste the story id, ticket, EARS reference, or task description."

## Step 0 — Load state, claim the story, and locate the requirements

1. Resolve `EPIC_DIR` via `state-loader`.
2. Determine `STORY_ID`:
   - If a story id was given, look it up in `stories`.
   - If none was given but `stories` has entries, list the ones with status `todo` and ask the user which to work (don't guess silently — picking the wrong story is itself duplicated work).
3. **Claim check (avoids duplicate work across concurrent runs):** look at the resolved story's current `status` in `state.json` *before* touching anything else:
   - `done` → tell the user this story is already complete and stop.
   - `in-progress` → do **not** silently proceed as if it were free. Show the most recent `audit.md` row for this `STORY_ID` and ask the user to confirm whether this is a resume of their own interrupted run (proceed via **Resume support** below) or a collision with another agent/session already working it (if the latter, stop).
   - `todo` (or story is untracked ad hoc work) → clear to claim.
4. **Claim:** immediately set the story's `state.json` status to `in-progress` and append an `audit.md` row via `aidlc-approve` (phase `implementation`, action `Claimed {STORY_ID} for implementation.`) — **before** Step 1 dispatches any sub-agents. This is the write that makes the story unavailable to any other `aidlc-tdd` run reading the same `state.json`.
5. Read the EARS section (`ears_ref`) and the parent LLD (`lld_ref`) — this **is** the requirements contract, not a summary of it. If the input is a ticket from `aidlc-jira-story-breakdown` instead, its `whatToBuild` + `acceptanceCriteria` play the same role.
6. If there is no epic at all (a genuine hotfix or standalone task with no `aidlc-docs/` entry), proceed ungoverned: skip `state.json`/`audit.md` bookkeeping (including the claim above) for the rest of this run, and say so explicitly so the user knows this story isn't being tracked or protected from collision.
7. If `STORY_ID` wasn't already set by step 2, set it now (the state.json key, ticket id, or a generated `T-{YYYYMMDD-HHMM}` for untracked ad hoc work).

Print: `[aidlc-tdd] [{STORY_ID}] Step 0 complete — story claimed, requirements located.`

## Step 1 — Codebase & test-landscape analysis

Dispatch two read-only `explore` Task sub-agents in parallel:

**App Code Analyzer:** "Given these requirements: `{requirements}`. Locate every file/layer that will need to change. Study adjacent implementations for patterns — error handling, validation, auth, data access. Find reusable utilities. Flag edge cases visible from code. Return a structured analysis."

**Test Analyzer:** "Given these requirements: `{requirements}`. Map the existing test landscape: frameworks, conventions, fixtures, builders, coverage gaps. Most importantly, propose **candidate seams** — the public interfaces/boundaries where this behavior could be observed and tested without reaching into internals. Return a structured analysis."

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

## Step 3 — Implement via the red → green loop

Dispatch `implementer` as a `generalPurpose` Task sub-agent. Pass: repo root + branch, the confirmed seam list, the requirements, and this discipline verbatim:

**What a good test is.** Tests verify behavior through public interfaces, not implementation details. Code can change entirely; tests shouldn't. A good test reads like a specification — "user can checkout with valid cart" tells you exactly what capability exists — and survives refactors because it doesn't care about internal structure.

**Anti-patterns to never produce:**
- **Implementation-coupled** — mocks internal collaborators, tests private methods, or verifies through a side channel (querying the database instead of using the interface). The tell: the test breaks when you refactor but behavior hasn't changed.
- **Tautological** — the assertion recomputes the expected value the way the code does (`expect(add(a, b)).toBe(a + b)`, a hand-derived snapshot, a constant asserted equal to itself), so it passes by construction. Expected values must come from an independent source of truth — a known-good literal, a worked example, the spec.
- **Horizontal slicing** — writing all tests first, then all implementation. Bulk tests verify *imagined* behavior and go insensitive to real changes. Work in **vertical slices** instead: one test → one implementation → repeat, each test a tracer bullet that responds to what the last cycle taught you.

**Rules of the loop:**
- Red before green. Write the failing test first, then only enough code to pass it. Don't anticipate future tests or add speculative features.
- One slice at a time. One seam, one test, one minimal implementation per cycle.
- Refactoring is not part of the loop — it belongs to Step 5 (code review), not the red → green cycle.
- If a seam not on the agreed list turns out to be necessary, **stop and escalate** to the orchestrator rather than silently expanding scope.

The implementer must not declare Step 3 complete until, locally: format/lint is clean, the build passes, and every test it wrote passes. It must report back a **slice log** (seam → test name → outcome) alongside PASS/FAIL, files touched, and build/test commands + results — this is the evidence that the loop was actually followed cycle-by-cycle, not just "tests pass" at the end.

**On success:** print `[aidlc-tdd] [{STORY_ID}] Step 3 complete — implementer: done.`
**On failure or scope escalation:** stop and bring it to the user.

## Step 4 — Test & anti-pattern audit

This step **audits**, it does not author net-new coverage wholesale — that would reintroduce horizontal slicing. Dispatch `test-auditor` as a `generalPurpose` Task sub-agent after Step 3 passes. Pass the slice log, the confirmed seam list, and the full unit/integration suite. It must:

1. Run the full suite and report counts.
2. Check every test the implementer added against the three anti-patterns above and flag violations.
3. Cross-check the slice log against the confirmed seam list: flag any agreed seam with no test, and any test that reaches an interface outside the agreed seams.
4. It **may** add a single missing test for an already-agreed seam if genuinely absent (still red-before-green) — it **must not** invent new seams or bulk-add tests for untested internals.

**If it fails:** return to `implementer` with the findings. Maximum 3 implementer ↔ test-auditor cycles before escalating to the user.

**On success:** print `[aidlc-tdd] [{STORY_ID}] Step 4 complete — test-auditor: PASS ({N} passed, 0 failed, 0 anti-pattern findings).`

**Optional second-tier/E2E:** if the repo documents a second-tier suite (e.g. `tests/automation/`) and the story is tagged to require it, dispatch `test-auditor` again for that suite. Otherwise: `[aidlc-tdd] [{STORY_ID}] second-tier suite skipped — none documented or required.`

## Step 5 — Code review

Dispatch `code-reviewer` as a `generalPurpose` Task sub-agent after Step 4 passes. Pass all prior context and outputs. Review scope:

- Alignment: does the implementation match the EARS acceptance criteria / LLD (or ticket) exactly — no silent scope drift?
- The three TDD anti-patterns (implementation-coupled, tautological, horizontal slicing) — a second pass, independent of Step 4's own audit.
- Correctness, security, error handling, maintainability.
- Refactoring opportunities the red → green loop deliberately deferred (this is where they belong).

Return: APPROVED, or CHANGES REQUESTED with prioritized findings.

**On CHANGES REQUESTED:** return to `implementer`. Re-run `test-auditor` if behavior or tests changed. Maximum 3 reviewer ↔ implementer cycles before escalating.

**On APPROVED:** print `[aidlc-tdd] [{STORY_ID}] Step 5 complete — code-reviewer: approved.`

## Step 6 — Close out

1. If tracked: set the story's `state.json` status to `done`. If every story in the `stories` map is now `done`, note that the `implementation-in-progress → implementation-completed` transition trigger is met and tell the user (per `state-loader`'s pipeline config) — do not flip the epic-level `status` yourself without saying so.
2. Append an `audit.md` row via `aidlc-approve` (phase `implementation`, action `{STORY_ID} implemented, tested, and reviewed.`).
3. Summarize what was built against the acceptance criteria, list any deferred items or known gaps, and ask the user to confirm before calling the story done.

Print:
```
[aidlc-tdd] [{STORY_ID}] STORY COMPLETE — implementation, tests, and review finished.
Branch: {branch-name}
Next: push branch / open a PR, or start the next story with aidlc-tdd.
```

## Sub-agent dispatch rules

Every `implementer`, `test-auditor`, and `code-reviewer` dispatch **must** be a `generalPurpose` Task sub-agent for context isolation; analysis in Step 1 uses `explore`. Each prompt must include: repo root + branch, full requirements text, the confirmed seam list, paths to `ears_ref`/`lld_ref` when present, prior step outputs as summaries (not full dumps), and an instruction to return PASS/FAIL, artifacts touched, and blockers.

## Command discovery

Build/test/lint/format commands are discovered at runtime, in order: `README` (Getting Started/Development/Testing sections) → `package.json` scripts → `Makefile` → `pyproject.toml`/`poetry.lock`/`tox.ini` (and this repo's `ruff check --fix . && ruff format .` convention for Python) → `build.gradle`/`pom.xml` → `.github/workflows/`. Pass whatever is discovered to every sub-agent prompt. If nothing is discoverable, ask the user before proceeding.

## Resume support

Reached from Step 0's claim check once the user has confirmed this is their own interrupted run, not another agent's story:
1. `EPIC_DIR/state.json` — status is already `in-progress`; resume from the step implied by what's on disk (seams already confirmed → Step 3; implementation already reported → Step 4, etc.) rather than restarting.
2. `EPIC_DIR/audit.md` — the most recent row for this story indicates the last completed gate.

Present a short resume summary before continuing. Do not re-run the Step 0 claim write (it's already claimed) — just proceed from the resumed step.

## Integration with other skills

| Skill | Relationship |
|-------|-------------|
| `state-loader` / `aidlc-init` | Supplies `EPIC_DIR`, epic status, and the `stories` map this skill reads and updates |
| `aidlc-design-driven-dev` | Upstream — produces the HLD/LLD/EARS this skill implements against |
| `aidlc-jira-story-breakdown` | Alternate story source — its ticket JSON (or a live Jira issue) can stand in for an `ears_ref` |
| `aidlc-approve` | Used for every `audit.md` row this skill writes (Steps 2 and 6) |

## When NOT to use this skill

- User only wants planning or design — send them to `aidlc-design-driven-dev` first, then come back once EARS is approved.
- Genuine hotfix with no time for seam alignment — say "skip alignment" and proceed with the ad hoc path in Step 0/2.
- Repo is not a git repository — clarify workspace and pause.
- Requirements are completely unknown — gather them first (vision, ADR, EARS, or a ticket), then invoke this skill.
