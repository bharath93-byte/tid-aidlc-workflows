# TDD Code Generation - Detailed Steps

## Overview
This stage generates code for each unit of work using **Test-Driven Development (TDD)**. Work proceeds through two integrated parts:
- **Part 1 - Planning**: Create a TDD code generation plan organized as Red → Green → Refactor cycles per behavior
- **Part 2 - Generation**: Execute the approved plan: write a failing test first, implement the minimum code to pass, refactor while keeping tests green, then run Code Reviewer

**TDD contract (mandatory)**:
1. **Red** — Write one failing automated test that specifies desired behavior
2. **Green** — Write the smallest production change that makes that test (and the existing suite) pass
3. **Refactor** — Improve design/structure without changing behavior; keep the suite green

**Note**: For brownfield projects, "generate" means modify existing files when appropriate, not create duplicates. Prefer extending existing test suites over creating parallel `*_new` test files.

**Default method**: This is the **default** Code Generation rule (`core-workflow.md`). Use `construction/code-generation.md` only when the user explicitly opts into standard/normal Code Generation while approving Workflow Planning / proceeding to Construction. Flow control (plan approval, reviewer handoff, completion gates) matches standard Code Generation; generation order is test-first. The selected method must be logged in `aidlc-docs/aidlc-state.md` and `aidlc-docs/audit.md`.

## Prerequisites
- Unit Design Generation must be complete for the unit
- NFR Implementation (if executed) must be complete for the unit
- All unit design artifacts must be available
- Unit is ready for TDD code generation
- Test runner / framework for the project language is known or will be established in Project Structure Setup

---

# PART 1: PLANNING

## Step 1: Analyze Unit Context
- [ ] Read unit design artifacts from Unit Design Generation
- [ ] Read unit story map to understand assigned stories
- [ ] Identify unit dependencies and interfaces
- [ ] Derive **testable behaviors** from stories, acceptance criteria, business rules, and API/contracts
- [ ] List edge cases, error paths, and invariants that must be covered by tests
- [ ] Validate unit is ready for TDD code generation

## Step 2: Create Detailed Unit TDD Code Generation Plan
- [ ] Read workspace root and project type from `aidlc-docs/aidlc-state.md`
- [ ] Determine code and test locations (see Critical Rules for structure patterns)
- [ ] **Brownfield only**: Review reverse engineering code-structure.md for existing production and test files to modify
- [ ] Document exact paths (never aidlc-docs/)
- [ ] Create explicit steps for unit generation using TDD order:
  - Project Structure Setup (greenfield only) — include test framework, runner, and coverage tooling
  - Test Harness / Fixtures Setup (shared test utilities, factories, fakes/mocks as needed)
  - For each layer or story slice, plan **TDD cycles** (not code-then-tests):
    - Business Logic — TDD cycles (Red → Green → Refactor per behavior)
    - API Layer — TDD cycles (contract/request/response/error behaviors)
    - Repository Layer — TDD cycles (persistence behaviors; use fakes/in-memory doubles where appropriate)
    - Frontend Components — TDD cycles if applicable (component/behavior tests first)
  - Cross-cutting / Integration Tests (only after unit-level TDD cycles for the involved behaviors; still drive with failing tests first)
  - Database Migration Scripts (if data models exist) — migrations may accompany Green steps; schema changes must be covered by tests where practical
  - Documentation Generation (API docs, README updates)
  - Deployment Artifacts Generation
- [ ] For each TDD cycle in the plan, document:
  - Behavior / story ID
  - Intended failing test name(s) and file path
  - Production file(s) expected to change in Green
  - Refactor goals (if known) — e.g., extract collaborator, remove duplication
- [ ] Number each step sequentially
- [ ] Include story mapping references
- [ ] Add checkboxes [ ] for each step
- [ ] **Do not** plan "generate production code then add tests" as the default sequence

## Step 3: Include Unit Generation Context
- [ ] For this unit, include:
  - Stories and testable behaviors implemented by this unit
  - Dependencies on other units/services
  - Expected interfaces and contracts (and how tests will assert them)
  - Database entities owned by this unit
  - Service boundaries and responsibilities
  - Test strategy notes: unit vs narrow integration, doubles/fakes policy, what is out of scope for TDD cycles

## Step 4: Create Unit Plan Document
- [ ] Save complete plan as `aidlc-docs/construction/plans/{unit-name}-tdd-code-generation-plan.md`
- [ ] Include step numbering (Step 1, Step 2, etc.)
- [ ] Include unit context and dependencies
- [ ] Include story and behavior traceability
- [ ] Group work as TDD cycles with Red / Green / Refactor sub-checkboxes where helpful
- [ ] Include **Pseudocode of Planned Changes** covering every significant TDD cycle in the plan:
  - One pseudocode block per behavior/cycle that will change application logic (skip pure scaffolding/docs-only steps when no behavior changes)
  - For each cycle, show intended **test intent** (what the Red test asserts) and **production pseudocode** for the Green implementation
  - Show control flow, branching, error paths, and key function/method signatures
  - Reference target test file paths, production file paths, and story/behavior IDs so pseudocode maps to executable plan steps
  - For brownfield: call out existing vs new logic (what is modified vs added)
  - Keep Green pseudocode minimal (enough to pass the planned Red); note expected Refactor direction briefly if known
- [ ] Include **Data Flow Chart with Schema Details** for the planned changes:
  - Diagram end-to-end data movement introduced or modified by this unit (request → handlers/services → persistence/events → response)
  - Use Mermaid flowchart/sequence (validate per `common/content-validation.md`) plus a text alternative
  - Capture schemas for each data shape on the flow: request/response DTOs, domain entities, DB tables/collections, events/messages, and test fixture/input shapes where they clarify contracts
  - For each schema: field name, type, required/optional, constraints/validation, and ownership (this unit vs external)
  - Map schemas to the TDD cycles/behaviors that will assert them (which Red tests cover which fields/invariants)
  - For brownfield: show delta (before → after) when schemas or flows change; do not dump unrelated full-system schema
- [ ] Ensure plan is executable step-by-step
- [ ] Emphasize that this plan is the single source of truth for TDD Code Generation

## Step 5: Summarize Unit Plan
- [ ] Provide summary of the unit TDD code generation plan to the user
- [ ] Highlight TDD approach (test-first, Red → Green → Refactor)
- [ ] Explain cycle sequence and story/behavior coverage
- [ ] Call out that the plan includes pseudocode of planned changes and a data flow chart with schema details for review
- [ ] Note total number of steps/cycles and estimated scope

## Step 6: Log Approval Prompt
- [ ] Before asking for approval, log the prompt with timestamp in `aidlc-docs/audit.md`
- [ ] Include reference to the complete unit TDD code generation plan
- [ ] Use ISO 8601 IST timestamp format (`YYYY-MM-DDTHH:mm:ss+05:30`)

## Step 7: Wait for Explicit Approval
- [ ] Do not proceed until the user explicitly approves the unit TDD code generation plan
- [ ] Approval must cover the entire plan and TDD cycle sequence
- [ ] If user requests changes, update the plan and repeat approval process

## Step 8: Record Approval Response
- [ ] Log the user's approval response with timestamp in `aidlc-docs/audit.md`
- [ ] Include the exact user response text
- [ ] Mark the approval status clearly

## Step 9: Update Progress
- [ ] Mark TDD Code Generation Part 1 (Planning) complete in `aidlc-state.md`
- [ ] Update the "Current Status" section
- [ ] Prepare for transition to TDD Generation

---

# PART 2: GENERATION (TDD CYCLES)

## Step 10: Load Unit TDD Code Generation Plan
- [ ] Read the complete plan from `aidlc-docs/construction/plans/{unit-name}-tdd-code-generation-plan.md`
- [ ] Identify the next uncompleted step or TDD cycle (first `[ ]` checkbox)
- [ ] Load the context for that step (unit, dependencies, stories, target behavior)
- [ ] Confirm which phase of the cycle is next: **Red**, **Green**, or **Refactor** (if the plan uses sub-steps)

## Step 11: Execute Current Step (TDD)
- [ ] Verify target directory from plan (never aidlc-docs/)
- [ ] **Brownfield only**: Check if target production/test file exists
- [ ] **If a prior Code Reviewer report exists** at `aidlc-docs/construction/{unit-name}/code/code-review.md` (from Step 16):
  - Read all open findings (Blocker, Major, Minor, and any user-requested changes tied to the report)
  - Prefer a TDD fix path: add/adjust a failing test that captures the defect (Red), then implement the fix (Green), then Refactor if needed
  - Prefer resolving Blocker and Major findings first; do not ignore applicable review comments
  - When fixing review feedback, modify existing files in-place (never create `*_modified` / `*_new` copies)
  - Note in the step outcome which review findings were addressed (finding text or location)

### 11a. Red — Write Failing Test First
- [ ] Write or extend the automated test that specifies the next behavior only
- [ ] Use Arrange–Act–Assert (or project-equivalent) with a clear test name tied to the story/behavior
- [ ] Run the relevant tests and **confirm failure** for the new expectation (compile error or assertion failure is acceptable Red; wrong-green is not)
- [ ] If the new test passes without new production code: the test is weak or the behavior already exists — tighten the test or select the next uncovered behavior; do not invent production changes without a real Red
- [ ] Do **not** write production implementation in the same edit as the first Red for that behavior (minimal stubs only if required for the test to compile/run and still fail on the assertion)

### 11b. Green — Minimal Implementation
- [ ] Implement the **smallest** production change that makes the new test pass
- [ ] Run the relevant tests; all previously green tests must remain green
- [ ] Avoid speculative features, extra abstractions, or unrelated cleanups in Green
- [ ] **If file exists**: Modify it in-place (never create `ClassName_modified.java`, `ClassName_new.java`, etc.)
- [ ] **If file doesn't exist**: Create new file
- [ ] Write to correct locations:
  - **Application Code / Tests**: Workspace root per project structure
  - **Documentation**: `aidlc-docs/construction/{unit-name}/code/` (markdown only)
  - **Build/Config Files**: Workspace root

### 11c. Refactor — Improve While Green
- [ ] Refactor production and/or test code to improve design, naming, duplication, and SOLID alignment
- [ ] Run tests after each meaningful refactor; suite must stay green
- [ ] Do not change observable behavior during Refactor; if behavior must change, start a new Red cycle
- [ ] Keep tests readable; extract helpers/fixtures when duplication appears

### 11d. Step Constraints
- [ ] Follow unit story requirements and the approved plan
- [ ] Respect dependencies and interfaces
- [ ] Keep each cycle focused on one behavior (or the smallest coherent slice defined in the plan)

## Step 12: Run Tests and Capture Evidence
- [ ] Run the unit’s relevant test command(s) for the current cycle (prefer fast, targeted runs during cycles; full suite at logical milestones)
- [ ] Record pass/fail outcome in the plan step notes or `aidlc-docs/construction/{unit-name}/code/` summary (command + result)
- [ ] On failure after Green/Refactor: fix before marking the cycle complete — do not proceed with a red suite
- [ ] At layer/story milestones, run the broader suite for the unit when practical

## Step 13: Update Progress
- [ ] Mark the completed Red / Green / Refactor / step checkboxes as `[x]` in the unit TDD plan
- [ ] Mark associated unit stories as `[x]` when their behaviors are fully covered and green
- [ ] Update `aidlc-docs/aidlc-state.md` current status
- [ ] **Brownfield only**: Verify no duplicate files created (e.g., no `ClassName_modified.java` alongside `ClassName.java`)
- [ ] Save all generated artifacts

## Step 14: Continue or Complete TDD Cycles
- [ ] If more plan steps or TDD cycles remain, return to Step 10
- [ ] If all TDD plan steps are complete, proceed to Step 15 (full suite confirmation)

## Step 15: Confirm Full Test Suite Green
- [ ] Run the full automated test suite applicable to this unit (or project suite if single-unit)
- [ ] Suite must be green before Code Reviewer
- [ ] Record command(s) and result in `aidlc-docs/construction/{unit-name}/code/tdd-test-run.md` (or the unit code summary)
- [ ] If failures exist: return to Step 10/11 and fix via TDD (Red for regression if missing, then Green/Refactor)

## Step 16: Run Code Reviewer
- [ ] Load and execute all steps from `construction/reviewer.md` (review details, report, and user continuation live there)
- [ ] Branch on the continuation outcome returned by the reviewer:
  - **Fix the review comments** → proceed to Step 11 (via Step 10 as needed) using TDD (prefer Red that captures the finding), then re-run Steps 15–16 as needed
  - **Continue without fixing** or **Approve (no findings)** → proceed to Step 17
  - **Other** → follow the outcome described by the reviewer
- [ ] Log that Code Reviewer was invoked and the continuation outcome in `aidlc-docs/audit.md` with ISO 8601 IST timestamp

## Step 17: Present Completion Message
- Present completion message in this structure:
     1. **Completion Announcement** (mandatory): Always start with this:

```markdown
# 💻 TDD Code Generation Complete - [unit-name]
```

     2. **AI Summary** (optional): Provide structured bullet-point summary
        - **Brownfield**: Distinguish modified vs created files (production and tests)
        - **Greenfield**: List created files with paths
        - List test files, documentation, deployment artifacts with paths
        - Note that work followed Red → Green → Refactor and that the suite is green
        - Include code review verdict and path to `aidlc-docs/construction/[unit-name]/code/code-review.md`
        - Keep factual, no workflow instructions
     3. **Formatted Workflow Message** (mandatory): Always end with this exact format:

```markdown
> **📋 <u>**REVIEW REQUIRED:**</u>**  
> Please examine the TDD-generated code at:
> - **Application Code**: `[actual-workspace-path]`
> - **Documentation**: `aidlc-docs/construction/[unit-name]/code/`
> - **Code Review**: `aidlc-docs/construction/[unit-name]/code/code-review.md`



> **🚀 <u>**WHAT'S NEXT?**</u>**
>
> **You may:**
>
> 🔧 **Request Changes** - Ask for modifications; fixes must follow TDD (Red → Green → Refactor)  
> ✅ **Continue to Next Stage** - Approve TDD code generation and proceed to **[next-unit/Build & Test]**

---
```

## Step 18: Wait for Explicit Approval
- Do not proceed until the user explicitly approves the generated code
- Approval must be clear and unambiguous
- If user requests changes, return to Step 11 and apply fixes via TDD (including any Step 16 review comments), re-run Step 15 (full suite), then re-run Step 16 (Code Reviewer), and repeat the approval process

## Step 19: Record Approval and Update Progress
- Log approval in audit.md with timestamp
- Record the user's approval response with timestamp
- Mark TDD Code Generation stage as complete for this unit in aidlc-state.md

---

## Critical Rules

### Code Location Rules
- **Application code and tests**: Workspace root only (NEVER aidlc-docs/)
- **Documentation**: aidlc-docs/ only (markdown summaries)
- **Read workspace root** from aidlc-state.md before generating code

**Structure patterns by project type**:
- **Brownfield**: Use existing structure (e.g., `src/main/java/`, `src/test/java/`, `lib/`, `pkg/`, `__tests__/`)
- **Greenfield single unit**: `src/`, `tests/`, `config/` in workspace root
- **Greenfield multi-unit (microservices)**: `{unit-name}/src/`, `{unit-name}/tests/`
- **Greenfield multi-unit (monolith)**: `src/{unit-name}/`, `tests/{unit-name}/`

### Brownfield File Modification Rules
- Check if file exists before generating
- If exists: Modify in-place (never create copies like `ClassName_modified.java`)
- If doesn't exist: Create new file
- Verify no duplicate files after generation (Step 13)

### TDD Rules
- **TEST FIRST**: For each new behavior, Red must come before Green
- **ONE BEHAVIOR AT A TIME**: Do not batch many unrelated behaviors into a single Red/Green without plan approval
- **WATCH IT FAIL**: Never skip confirming Red
- **MINIMAL GREEN**: No speculative production code in Green
- **REFACTOR ONLY WHILE GREEN**: Behavior changes require a new Red cycle
- **KEEP THE SUITE GREEN**: Do not leave failing tests between cycles except during an in-progress Red
- **TESTS ARE PRODUCT**: Treat test code with the same quality bar as production code
- **NO TEST-AFTER AS DEFAULT**: Writing production code first and tests later violates this stage

### Planning Phase Rules
- Create explicit, numbered steps organized as TDD cycles
- Include story and behavior traceability in the plan
- Document unit context, dependencies, and test strategy
- Include pseudocode of planned changes (test intent + Green production logic) in the plan
- Include a data flow chart with captured schemas for the planned changes in the plan
- Get explicit user approval before generation

### Generation Phase Rules
- **NO HARDCODED LOGIC**: Only execute what's written in the unit TDD plan
- **FOLLOW PLAN EXACTLY**: Do not deviate from the step/cycle sequence
- **IMPLEMENT FROM PSEUDOCODE**: Red tests and Green code must match the approved plan pseudocode for that cycle (Refactor may improve structure without changing planned behavior)
- **HONOR DATA FLOW AND SCHEMAS**: Generated code and tests must match the approved data flow chart and schema definitions in the plan
- **UPDATE CHECKBOXES**: Mark `[x]` immediately after completing each Red/Green/Refactor/step
- **STORY TRACEABILITY**: Mark unit stories `[x]` when behaviors are implemented and green
- **RESPECT DEPENDENCIES**: Only implement when unit dependencies are satisfied
- **RUN CODE REVIEWER**: When all TDD plan steps are complete and the suite is green, execute `construction/reviewer.md` (Step 16) and branch on its continuation outcome
- **HONOR REVIEW COMMENTS**: When continuation is Fix and `code-review.md` exists, Step 11 must address applicable findings using TDD

### Automation Friendly Code Rules
When generating UI code (web, mobile, desktop), ensure elements are automation-friendly:
- Add `data-testid` attributes to interactive elements (buttons, inputs, links, forms)
- Use consistent naming: `{component}-{element-role}` (e.g., `login-form-submit-button`, `user-list-search-input`)
- Avoid dynamic or auto-generated IDs that change between renders
- Keep `data-testid` values stable across code changes (only change when element purpose changes)

## Completion Criteria
- Complete unit TDD code generation plan created and approved
- All steps / TDD cycles in the plan marked `[x]`
- All unit stories/behaviors implemented according to plan via Red → Green → Refactor
- Automated tests exist for the implemented behaviors and were executed during generation
- Full applicable test suite green before Code Reviewer and before stage completion
- Deployment artifacts generated (as planned)
- Code Reviewer executed per `construction/reviewer.md` with report at `aidlc-docs/construction/{unit-name}/code/code-review.md`
- Complete unit ready for Build & Test (broader verification) and next stages
