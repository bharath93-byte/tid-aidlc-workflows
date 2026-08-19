# Dual-Agent TDD Code Generation - Detailed Steps

## Overview
This stage generates code for each unit of work using **Dual-Agent TDD**: Tester owns RED, Builder owns GREEN, with a firewall so the Tester never sees implementation.

Work proceeds through two parts in the **Orchestrator** session (the original AI-DLC workflow chat):
- **Part 1 - Planning**: Create the Dual-Agent plan, public contract (if needed), packets, firewall manifest, and launch prompts
- **Part 2 - Generation**: Launch an unlinked Tester session (batch RED) → confirm RED → launch an unlinked Builder session (GREEN) → confirm GREEN → optional Tester addendum → Code Reviewer

**Load** `common/dual-agent-separation.md` at stage start and enforce it as a hard constraint. Do not weaken the firewall in this file.

**TDD contract (mandatory)** — see `common/dual-agent-separation.md`:
1. **RED (Tester)** — Full black-box suite for this unit from spec + public contract
2. **GREEN (Builder)** — Smallest production change that makes that suite pass; do not edit Tester tests
3. **Addendum (optional)** — Spec-level gaps only; Tester still firewalled

**Opt-in only**: This rule runs only when the user explicitly requests Dual-Agent TDD while approving Workflow Planning / proceeding to Construction. The **default** is single-session TDD (`construction/tdd-code-generation.md`). When this file is used, log `Code Generation Method: Dual-Agent TDD` in `aidlc-docs/aidlc-state.md` and `aidlc-docs/audit.md`.

**Note**: For brownfield projects, "generate" means modify existing files when appropriate, not create duplicates. Prefer extending existing test suites over creating parallel `*_new` test files.

**Orchestrator must not** write tests or production application code (unless the user explicitly asks the Orchestrator to patch after a failed Tester/Builder session).

## Prerequisites
- Unit Design Generation must be complete for the unit
- NFR Implementation (if executed) must be complete for the unit
- All unit design artifacts must be available
- Unit is ready for Dual-Agent TDD
- Test runner / framework for the project language is known or will be established in Project Structure Setup (constraints go in the **Tester packet**, not the Builder packet)
- Public contract available: OpenAPI and/or AsyncAPI, or Orchestrator will write `public-contract.md` from LLD/EARS before Tester launch

---

# PART 1: PLANNING

## Step 0: Skill Discovery & Selection (MANDATORY — do not skip on resume)
- Execute `common/skill-discovery-gate.md` **before any other step in this stage**
- Create `aidlc-docs/code-generation-skill-selection.md`; wait for user to fill `[Answer]:` and confirm
- Update `## Current Stage Skill` in `aidlc-docs/aidlc-state.md`; log resolved choice in `audit.md`
- **Do not** proceed to Step 1 until Step 0 is complete
- If a Dual-Agent skill is selected, follow `SKILL.md` for launch UX (HOW), then `common/skill-artifact-adapter.md` so contract artifacts in this file still exist (WHAT)

## Step 1: Analyze Unit Context
- [ ] Read `common/dual-agent-separation.md`
- [ ] Read unit design artifacts from Unit Design Generation
- [ ] Read unit story map to understand assigned stories
- [ ] Identify unit dependencies and interfaces
- [ ] Read the unit's EARS Coverage (from `unit-of-work.md`) — each EARS ID is a candidate testable behavior
- [ ] Derive **testable behaviors** from stories, acceptance criteria, business rules, API/contracts, and EARS requirements
- [ ] List edge cases, error paths, and invariants that must be covered by Tester tests
- [ ] Locate OpenAPI/AsyncAPI for this unit; if none, plan to write `public-contract.md` from LLD/EARS only
- [ ] Validate unit is ready for Dual-Agent TDD

## Step 2: Create Detailed Unit Dual-Agent TDD Plan
- [ ] Read workspace root and project type from `aidlc-docs/aidlc-state.md`
- [ ] Determine code and test locations (see Critical Rules for structure patterns)
- [ ] **Brownfield only**: Review reverse engineering for existing **test-tree** conventions to include on the Tester allowlist; do not put production source dumps in Tester-visible files
- [ ] Document exact paths (never aidlc-docs/ for application tests or code)
- [ ] Create explicit Orchestrator steps (not same-session Red/Green cycles):
  - Project Structure Setup (greenfield only) — test framework, runner, and coverage tooling **constraints for the Tester packet**
  - Public contract resolution (existing OpenAPI/AsyncAPI or `public-contract.md`)
  - Packet and firewall-manifest creation
  - Tester launch (batch RED)
  - RED evidence gate
  - Builder launch (GREEN)
  - GREEN evidence gate
  - Optional Tester addendum
  - Documentation Generation (API docs, README updates)
  - Deployment Artifacts Generation (Builder or Orchestrator docs only)
- [ ] For each testable behavior, document:
  - Behavior / story ID **and EARS ID(s)**
  - Intended test file path(s) and test intent (what RED asserts) — **test intent only, no Green production pseudocode in Tester-visible artifacts**
  - Production file(s) expected to change in GREEN (Builder packet / plan only)
- [ ] Number each step sequentially
- [ ] Include story mapping references
- [ ] Add checkboxes [ ] for each step
- [ ] **Do not** plan "Orchestrator writes tests and code in this session"

## Step 3: Include Unit Generation Context
- [ ] For this unit, include:
  - Stories and testable behaviors implemented by this unit
  - Dependencies on other units/services
  - Expected interfaces and contracts (and how Tester tests will assert them)
  - Database entities owned by this unit
  - Service boundaries and responsibilities
  - Test strategy notes: black-box/contract vs out of scope; doubles/fakes policy for Tester (public seams only)

## Step 4: Create Unit Plan and Dual-Agent Artifacts
- [ ] Save complete plan as `aidlc-docs/construction/plans/{unit-name}-dual-agent-tdd-plan.md`
- [ ] Include step numbering (Step 1, Step 2, etc.)
- [ ] Include unit context and dependencies
- [ ] Include story and behavior traceability
- [ ] Include **Test intent** covering every significant behavior (what RED asserts) — **do not** put Green production pseudocode in this plan if the Tester session is told to read it; put production pseudocode only in `builder-packet.md`
- [ ] Include **Data Flow Chart with Schema Details** for **public** data shapes (request/response DTOs, events) using Mermaid (validate per `common/content-validation.md`) plus a text alternative. Omit internal-only schemas from Tester-visible files; internal schemas may appear only in `builder-packet.md`
- [ ] Write Dual-Agent artifacts under `aidlc-docs/construction/{unit-name}/dual-agent/` per `common/dual-agent-separation.md`:
  - Create `aidlc-docs/construction/{unit-name}/dual-agent/firewall-manifest.md`
  - Create `aidlc-docs/construction/{unit-name}/dual-agent/public-contract.md` if no OpenAPI/AsyncAPI
  - Create `aidlc-docs/construction/{unit-name}/dual-agent/tester-packet.md`
  - Create `aidlc-docs/construction/{unit-name}/dual-agent/builder-packet.md` (test file list may be a placeholder until RED completes)
  - Create `aidlc-docs/construction/{unit-name}/dual-agent/tester-launch-prompt.md`
  - Create `aidlc-docs/construction/{unit-name}/dual-agent/builder-launch-prompt.md`
- [ ] Ensure the plan is executable step-by-step and is the Orchestrator's source of truth
- [ ] Emphasize that Tester and Builder execute in **unlinked** sessions using the launch prompts

## Step 5: Summarize Unit Plan
- [ ] Provide summary of the Dual-Agent TDD plan to the user
- [ ] Highlight firewall (Tester never sees implementation; two unlinked sessions)
- [ ] Explain batch RED → GREEN sequence and story/behavior coverage
- [ ] Call out packet paths and that the user must paste launch prompts into new sessions
- [ ] Note total number of steps and estimated scope

## Step 6: Log Approval Prompt
- [ ] Before asking for approval, log the prompt with timestamp in `aidlc-docs/audit.md`
- [ ] Include reference to the complete unit Dual-Agent TDD plan and `dual-agent/` packet directory
- [ ] Use ISO 8601 IST timestamp format (`YYYY-MM-DDTHH:mm:ss+05:30`)

## Step 7: Wait for Explicit Approval
- [ ] Do not proceed until the user explicitly approves the unit Dual-Agent TDD plan and packets
- [ ] Approval must cover the plan, firewall manifest, and session sequence
- [ ] If user requests changes, update the plan/packets and repeat approval process

## Step 8: Record Approval Response
- [ ] Log the user's approval response with timestamp in `aidlc-docs/audit.md`
- [ ] Include the exact user response text
- [ ] Mark the approval status clearly

## Step 9: Update Progress
- [ ] Mark Dual-Agent TDD Part 1 (Planning) complete in `aidlc-state.md`
- [ ] Update the "Current Status" section
- [ ] Prepare for Tester launch

---

# PART 2: GENERATION (UNLINKED SESSIONS)

## Step 10: Launch Tester Session (Batch RED)
- [ ] Present `aidlc-docs/construction/{unit-name}/dual-agent/tester-launch-prompt.md` to the user
- [ ] Instruct the user to open a **new unlinked agent session**, paste the prompt, and not attach production source or the Builder packet
- [ ] Log the Tester launch prompt in `aidlc-docs/audit.md` with ISO 8601 IST timestamp
- [ ] **Wait** until the user confirms the Tester session is done
- [ ] Log the user's confirmation (complete raw input) in `aidlc-docs/audit.md`

## Step 11: Confirm RED
- [ ] Identify test files written or modified under the firewall manifest **Test write paths**
- [ ] Run the unit's relevant test command(s)
- [ ] Create `aidlc-docs/construction/{unit-name}/dual-agent/red-evidence.md` (command, exit code, counts, timestamp, gate result)
- [ ] **RED gate**: new Tester tests must fail (compile error or assertion failure). If they pass without new production code: **do not start Builder** — treat as firewall/test-quality failure; return to Tester (tighten tests or select uncovered behavior)
- [ ] Update `builder-packet.md` and `builder-launch-prompt.md` with the actual Tester test file list
- [ ] Mark RED plan steps `[x]`

## Step 12: Launch Builder Session (GREEN)
- [ ] Present `aidlc-docs/construction/{unit-name}/dual-agent/builder-launch-prompt.md` to the user
- [ ] Instruct the user to open a **new unlinked agent session**, paste the prompt, and not edit Tester assertions
- [ ] Log the Builder launch prompt in `aidlc-docs/audit.md` with ISO 8601 IST timestamp
- [ ] **Wait** until the user confirms the Builder session is done
- [ ] Log the user's confirmation (complete raw input) in `aidlc-docs/audit.md`

## Step 13: Confirm GREEN
- [ ] Run the full automated test suite applicable to this unit (or project suite if single-unit)
- [ ] Create `aidlc-docs/construction/{unit-name}/dual-agent/green-evidence.md`
- [ ] Also record command(s) and result in `aidlc-docs/construction/{unit-name}/code/tdd-test-run.md` (or the unit code summary)
- [ ] On failure: return to Step 12 with failure output in an updated Builder prompt — **do not** patch production in the Orchestrator session unless the user explicitly asks
- [ ] Verify Builder did not modify Tester assertions (diff test files vs post-RED snapshot). If tests were weakened or rewritten: **Blocker** — restore Tester tests and return to Builder
- [ ] Annotate any missing `@spec` on production code if Builder omitted them (Orchestrator may add `@spec` comments only — not logic)
- [ ] Flip each EARS ID's status marker from `[ ]` to `[x]` in `aidlc-docs/inception/requirements/ears/` only once its `@spec`-annotated tests are green
- [ ] Mark GREEN plan steps `[x]`
- [ ] **Brownfield only**: Verify no duplicate files created (e.g., no `ClassName_modified.java`)

## Step 14: Optional Tester Addendum
- [ ] Compare EARS coverage and public contract to the Tester suite
- [ ] If no spec-level gaps, skip to Step 15 and mark addendum `[x]` as skipped
- [ ] If gaps exist: write a spec-level gap list (no source excerpts) into the Tester packet or a dedicated addendum section
- [ ] Repeat Steps 10–13 for the addendum only (Tester adds tests → RED evidence → Builder greens → GREEN evidence)
- [ ] Maximum 2 addendum rounds unless the user requests more; then escalate remaining gaps as deferred EARS `[D]` or follow-on unit

## Step 15: Confirm Full Test Suite Green
- [ ] Suite must be green before Code Reviewer
- [ ] If failures exist: return to Step 12 (Builder) or Step 14 (missing spec tests) — do not proceed with a red suite

## Step 16: Verify PR Size Budget
- [ ] Read the unit's approved PR size budget from `aidlc-docs/inception/application-design/unit-of-work.md` (≤ 10 counted files; target ≤ 200 / hard max 300 counted lines; `< 15 minutes` review)
- [ ] Measure actual scope vs merge-base with `origin/main` (plus uncommitted changes):

```bash
git fetch origin main
BASE=$(git merge-base HEAD origin/main)
git diff --stat "$BASE"...HEAD
git status --short
git diff --stat
git diff --cached --stat
```

- [ ] Count **only production/application source** files and their additions+deletions toward the budget
- [ ] **Exclude** from both file and line counts: unit tests, auto-generated lock files, migrations, and mocks
- [ ] Record counted vs excluded totals in `aidlc-docs/construction/{unit-name}/code/` (or `tdd-test-run.md` / unit code summary)
- [ ] If counted files > 10 or counted lines > 300 and no approved exception exists in `unit-of-work.md`:
  - Do **not** present completion as success
  - Split remaining work into a follow-on unit/PR, or stop and ask the user for an explicit exception with rationale
- [ ] If within limits (or exception approved), proceed to Step 17

## Step 17: Run Code Reviewer
- [ ] Load and execute all steps from `construction/reviewer.md` only after Step 16 PR size check passed (or exception approved)
- [ ] Dual-Agent extras for the reviewer (also in `reviewer.md`): Builder must not have weakened Tester tests; tests should remain black-box vs the public contract
- [ ] Branch on the continuation outcome returned by the reviewer:
  - **Fix the review comments** → production fixes go to Builder (Step 12); missing spec tests go to Tester addendum (Step 14); then re-run Steps 15–17 as needed
  - **Continue without fixing** or **Approve (no findings)** → proceed to Step 18
  - **Other** → follow the outcome described by the reviewer
- [ ] Log that Code Reviewer was invoked and the continuation outcome in `aidlc-docs/audit.md` with ISO 8601 IST timestamp

## Step 18: Present Completion Message
- Present completion message in this structure:
     1. **Completion Announcement** (mandatory): Always start with this:

```markdown
# Dual-Agent TDD Code Generation Complete - [unit-name]
```

     2. **AI Summary** (optional): Provide structured bullet-point summary
        - **Brownfield**: Distinguish modified vs created files (production and tests)
        - **Greenfield**: List created files with paths
        - List test files, documentation, deployment artifacts with paths
        - Note that Tester wrote tests (RED) and Builder implemented (GREEN) in unlinked sessions
        - Include paths to `dual-agent/red-evidence.md`, `dual-agent/green-evidence.md`, and `code/code-review.md`
        - Keep factual, no workflow instructions
     3. **Formatted Workflow Message** (mandatory): Always end with this exact format:

```markdown
> **📋 <u>**REVIEW REQUIRED:**</u>**
> Please examine the Dual-Agent TDD output at:
> - **Application Code**: `[actual-workspace-path]`
> - **Tests**: `[actual-test-path]`
> - **Packets / evidence**: `aidlc-docs/construction/[unit-name]/dual-agent/`
> - **Documentation**: `aidlc-docs/construction/[unit-name]/code/`
> - **Code Review**: `aidlc-docs/construction/[unit-name]/code/code-review.md`

> **🚀 <u>**WHAT'S NEXT?**</u>**
>
> **You may:**
>
> 🔧 **Request Changes** - Ask for modifications; production fixes via Builder session, missing spec tests via Tester addendum
> ✅ **Continue to Next Stage** - Approve Dual-Agent TDD and proceed to **[next-unit/Build & Test]**

---
```

## Step 19: Wait for Explicit Approval
- Do not proceed until the user explicitly approves the generated code
- Approval must be clear and unambiguous
- If user requests changes, return to Step 12 (Builder) and/or Step 14 (Tester addendum), re-run Step 15 (full suite), then re-run Steps 16–17 (PR size check + Code Reviewer), and repeat the approval process

## Step 20: Record Approval and Update Progress
- Log approval in audit.md with timestamp
- Record the user's approval response with timestamp
- Mark Dual-Agent TDD Code Generation stage as complete for this unit in aidlc-state.md

---

## Critical Rules

### Code Location Rules
- **Application code and tests**: Workspace root only (NEVER aidlc-docs/)
- **Documentation / packets / evidence**: aidlc-docs/ only (markdown)
- **Read workspace root** from aidlc-state.md before generation

**Structure patterns by project type**:
- **Brownfield**: Use existing structure (e.g., `src/main/java/`, `src/test/java/`, `lib/`, `pkg/`, `__tests__/`)
- **Greenfield single unit**: `src/`, `tests/`, `config/` in workspace root
- **Greenfield multi-unit (microservices)**: `{unit-name}/src/`, `{unit-name}/tests/`
- **Greenfield multi-unit (monolith)**: `src/{unit-name}/`, `tests/{unit-name}/`

### Brownfield File Modification Rules
- Check if file exists before generating
- If exists: Modify it in-place (never create copies like `ClassName_modified.java`)
- If doesn't exist: Create new file
- Verify no duplicate files after GREEN

### Dual-Agent TDD Rules
- **FIREWALL**: Tester session must not read production source (see `common/dual-agent-separation.md`)
- **UNLINKED SESSIONS**: Tester and Builder are new sessions, not Orchestrator sub-agents
- **TEST FIRST**: RED (Tester) before GREEN (Builder)
- **WATCH IT FAIL**: Never skip `red-evidence.md`
- **MINIMAL GREEN**: No speculative production code in Builder
- **BUILDER DOES NOT EDIT TESTS**: Assertion changes are a Blocker
- **ORCHESTRATOR DOES NOT IMPLEMENT**: No tests or production code in the workflow session
- **TESTS ARE PRODUCT**: Treat Tester tests with the same quality bar as production code
- **NO TEST-AFTER**: Builder writing tests, or Orchestrator generating tests after code, violates this stage

### Planning Phase Rules
- Create explicit, numbered Orchestrator steps (packet → Tester → RED → Builder → GREEN)
- Include story and behavior traceability
- Keep Green production pseudocode out of Tester-visible files
- Include a public data flow chart with schemas in Tester-visible plan/packet
- Get explicit user approval before launching Tester

### Generation Phase Rules
- **NO HARDCODED LOGIC**: Only execute what's written in the unit Dual-Agent plan
- **FOLLOW PLAN EXACTLY**: Do not skip RED evidence or merge Tester+Builder into one session
- **UPDATE CHECKBOXES**: Mark `[x]` immediately after completing each step
- **STORY TRACEABILITY**: Mark unit stories `[x]` when behaviors are implemented and green
- **RESPECT DEPENDENCIES**: Only implement when unit dependencies are satisfied
- **VERIFY PR SIZE BUDGET**: Before Code Reviewer / completion, re-check counted diff size against unit budget from `unit-of-work.md`
- **RUN CODE REVIEWER**: When plan steps are complete, the suite is green, and PR size check passed, execute `construction/reviewer.md`
- **HONOR REVIEW COMMENTS**: Production findings → Builder; missing spec tests → Tester addendum

### Automation Friendly Code Rules
When generating UI code (web, mobile, desktop), ensure elements are automation-friendly:
- Add `data-testid` attributes to interactive elements (buttons, inputs, links, forms)
- Use consistent naming: `{component}-{element-role}` (e.g., `login-form-submit-button`, `user-list-search-input`)
- Avoid dynamic or auto-generated IDs that change between renders
- Keep `data-testid` values stable across code changes (only change when element purpose changes)

## Completion Criteria
- Complete unit Dual-Agent TDD plan created and approved
- All steps in the plan marked `[x]`
- Tester packet, Builder packet, firewall manifest, and launch prompts exist
- `red-evidence.md` shows failing new tests before Builder
- `green-evidence.md` shows the suite green after Builder
- Builder did not rewrite Tester assertions
- All unit stories/behaviors covered via Dual-Agent RED → GREEN
- PR size budget verified (counted files ≤ 10 and counted lines ≤ 300, or approved exception documented)
- Code Reviewer executed per `construction/reviewer.md` with report at `aidlc-docs/construction/{unit-name}/code/code-review.md`
- Every EARS ID in this unit's coverage is `@spec`-annotated in code/tests, and its status marker in `aidlc-docs/inception/requirements/ears/` reflects actual pass/fail state
- Complete unit ready for Build & Test (broader verification) and next stages
