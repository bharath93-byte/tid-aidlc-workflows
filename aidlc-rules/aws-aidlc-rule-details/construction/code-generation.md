# Code Generation - Detailed Steps

## Overview
This stage generates code for each unit of work through two integrated parts:
- **Part 1 - Planning**: Create detailed code generation plan with explicit steps
- **Part 2 - Generation**: Execute approved plan to generate code, tests, and artifacts

**Opt-in only**: This is **standard/normal Code Generation**. It runs only when the user explicitly requests it while approving Workflow Planning / proceeding to Construction. The **default** is TDD Code Generation (`construction/tdd-code-generation.md`). When this file is used, ensure `Code Generation Method: Standard` is logged in `aidlc-docs/aidlc-state.md` and `aidlc-docs/audit.md`.

**Note**: For brownfield projects, "generate" means modify existing files when appropriate, not create duplicates.

## Prerequisites
- Unit Design Generation must be complete for the unit
- NFR Implementation (if executed) must be complete for the unit
- All unit design artifacts must be available
- Unit is ready for code generation

---

# PART 1: PLANNING

## Step 0: Skill Discovery & Selection (MANDATORY — do not skip on resume)
- Execute `common/skill-discovery-gate.md` **before any other step in this stage**
- Create `aidlc-docs/code-generation-skill-selection.md`; wait for user to fill `[Answer]:` and confirm
- Update `## Current Stage Skill` in `aidlc-docs/aidlc-state.md`; log resolved choice in `audit.md`
- **Do not** proceed to Step 1 until Step 0 is complete

## Step 1: Analyze Unit Context
- [ ] Read unit design artifacts from Unit Design Generation
- [ ] Read unit story map to understand assigned stories
- [ ] Identify unit dependencies and interfaces
- [ ] Validate unit is ready for code generation

## Step 2: Create Detailed Unit Code Generation Plan
- [ ] Read workspace root and project type from `aidlc-docs/aidlc-state.md`
- [ ] Determine code location (see Critical Rules for structure patterns)
- [ ] **Brownfield only**: Review reverse engineering code-structure.md for existing files to modify
- [ ] Document exact paths (never aidlc-docs/)
- [ ] Create explicit steps for unit generation:
  - Project Structure Setup (greenfield only)
  - Business Logic Generation
  - Business Logic Unit Testing
  - Business Logic Summary
  - API Layer Generation
  - API Layer Unit Testing
  - API Layer Summary
  - Repository Layer Generation
  - Repository Layer Unit Testing
  - Repository Layer Summary
  - Frontend Components Generation (if applicable)
  - Frontend Components Unit Testing (if applicable)
  - Frontend Components Summary (if applicable)
  - Database Migration Scripts (if data models exist)
  - Documentation Generation (API docs, README updates)
  - Deployment Artifacts Generation
- [ ] Number each step sequentially
- [ ] Include story mapping references
- [ ] Add checkboxes [ ] for each step

## Step 3: Include Unit Generation Context
- [ ] For this unit, include:
  - Stories implemented by this unit
  - Dependencies on other units/services
  - Expected interfaces and contracts
  - Database entities owned by this unit
  - Service boundaries and responsibilities

## Step 4: Create Unit Plan Document
- [ ] Save complete plan as `aidlc-docs/construction/plans/{unit-name}-code-generation-plan.md`
- [ ] Include step numbering (Step 1, Step 2, etc.)
- [ ] Include unit context and dependencies
- [ ] Include story traceability
- [ ] Ensure plan is executable step-by-step
- [ ] Emphasize that this plan is the single source of truth for Code Generation

## Step 5: Summarize Unit Plan
- [ ] Provide summary of the unit code generation plan to the user
- [ ] Highlight unit generation approach
- [ ] Explain step sequence and story coverage
- [ ] Note total number of steps and estimated scope

## Step 6: Log Approval Prompt
- [ ] Before asking for approval, log the prompt with timestamp in `aidlc-docs/audit.md`
- [ ] Include reference to the complete unit code generation plan
- [ ] Use ISO 8601 IST timestamp format (`YYYY-MM-DDTHH:mm:ss+05:30`)

## Step 7: Wait for Explicit Approval
- [ ] Do not proceed until the user explicitly approves the unit code generation plan
- [ ] Approval must cover the entire plan and generation sequence
- [ ] If user requests changes, update the plan and repeat approval process

## Step 8: Record Approval Response
- [ ] Log the user's approval response with timestamp in `aidlc-docs/audit.md`
- [ ] Include the exact user response text
- [ ] Mark the approval status clearly

## Step 9: Update Progress
- [ ] Mark Code Generation Part 1 (Planning) complete in `aidlc-state.md`
- [ ] Update the "Current Status" section
- [ ] Prepare for transition to Code Generation

---

# PART 2: GENERATION

## Step 10: Load Unit Code Generation Plan
- [ ] Read the complete plan from `aidlc-docs/construction/plans/{unit-name}-code-generation-plan.md`
- [ ] Identify the next uncompleted step (first [ ] checkbox)
- [ ] Load the context for that step (unit, dependencies, stories)

## Step 11: Execute Current Step
- [ ] Verify target directory from plan (never aidlc-docs/)
- [ ] **Brownfield only**: Check if target file exists
- [ ] **If a prior Code Reviewer report exists** at `aidlc-docs/construction/{unit-name}/code/code-review.md` (from Step 14):
  - Read all open findings (Blocker, Major, Minor, and any user-requested changes tied to the report)
  - Apply fixes for findings that affect the current plan step's files/scope before or as part of generating that step
  - Prefer resolving Blocker and Major findings first; do not ignore applicable review comments
  - When fixing review feedback, modify existing files in-place (never create `*_modified` / `*_new` copies)
  - Note in the step outcome which review findings were addressed (finding text or location)
- [ ] Generate exactly what the current step describes (and any applicable review fixes):
  - **If file exists**: Modify it in-place (never create `ClassName_modified.java`, `ClassName_new.java`, etc.)
  - **If file doesn't exist**: Create new file
- [ ] Write to correct locations:
  - **Application Code**: Workspace root per project structure
  - **Documentation**: `aidlc-docs/construction/{unit-name}/code/` (markdown only)
  - **Build/Config Files**: Workspace root
- [ ] Follow unit story requirements
- [ ] Respect dependencies and interfaces

## Step 12: Update Progress
- [ ] Mark the completed step as [x] in the unit code generation plan
- [ ] Mark associated unit stories as [x] when their generation is finished
- [ ] Update `aidlc-docs/aidlc-state.md` current status
- [ ] **Brownfield only**: Verify no duplicate files created (e.g., no `ClassName_modified.java` alongside `ClassName.java`)
- [ ] Save all generated artifacts

## Step 13: Verify PR Size Budget
- [ ] If any steps in the unit code generation plan remain incomplete (`[ ]`), skip this step and proceed to Step 15
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
- [ ] Record counted vs excluded totals in `aidlc-docs/construction/{unit-name}/code/` (or the unit code summary)
- [ ] If counted files > 10 or counted lines > 300 and no approved exception exists in `unit-of-work.md`:
  - Do **not** present completion as success
  - Split remaining work into a follow-on unit/PR, or stop and ask the user for an explicit exception with rationale
- [ ] If within limits (or exception approved), proceed to Step 14

## Step 14: Run Code Reviewer
- [ ] If any steps in the unit code generation plan remain incomplete (`[ ]`), skip this step and proceed to Step 15
- [ ] If all unit code generation plan steps are complete and Step 13 PR size check passed (or exception approved):
  - Load and execute all steps from `construction/reviewer.md` (review details, report, and user continuation live there)
  - Branch on the continuation outcome returned by the reviewer:
    - **Fix the review comments** → proceed to Step 11 (via Step 10 as needed), then re-run Steps 13–14
    - **Continue without fixing** or **Approve (no findings)** → proceed to Step 15
    - **Other** → follow the outcome described by the reviewer
- [ ] Log that Code Reviewer was invoked and the continuation outcome in `aidlc-docs/audit.md` with ISO 8601 IST timestamp

## Step 15: Continue or Complete Generation
- [ ] If more generation plan steps remain, return to Step 10
- [ ] If Step 13 failed PR size budget without exception, do not present completion — split work or obtain exception first
- [ ] If Step 14 continuation outcome is **Fix the review comments**, return to Step 10/11 (do not present completion yet)
- [ ] If all generation plan steps are complete, Step 13 passed, and Step 14 continuation outcome is **Continue without fixing** or **Approve (no findings)**, proceed to present completion message

## Step 16: Present Completion Message
- Present completion message in this structure:
     1. **Completion Announcement** (mandatory): Always start with this:

```markdown
# 💻 Code Generation Complete - [unit-name]
```

     2. **AI Summary** (optional): Provide structured bullet-point summary
        - **Brownfield**: Distinguish modified vs created files (e.g., "• Modified: `src/services/user-service.ts`", "• Created: `src/services/auth-service.ts`")
        - **Greenfield**: List created files with paths (e.g., "• Created: `src/services/user-service.ts`")
        - List tests, documentation, deployment artifacts with paths
        - Include code review verdict and path to `aidlc-docs/construction/[unit-name]/code/code-review.md`
        - Keep factual, no workflow instructions
     3. **Formatted Workflow Message** (mandatory): Always end with this exact format:

```markdown
> **📋 <u>**REVIEW REQUIRED:**</u>**  
> Please examine the generated code at:
> - **Application Code**: `[actual-workspace-path]`
> - **Documentation**: `aidlc-docs/construction/[unit-name]/code/`
> - **Code Review**: `aidlc-docs/construction/[unit-name]/code/code-review.md`



> **🚀 <u>**WHAT'S NEXT?**</u>**
>
> **You may:**
>
> 🔧 **Request Changes** - Ask for modifications to the generated code based on your review  
> ✅ **Continue to Next Stage** - Approve code generation and proceed to **[next-unit/Build & Test]**

---
```

## Step 17: Wait for Explicit Approval
- Do not proceed until the user explicitly approves the generated code
- Approval must be clear and unambiguous
- If user requests changes, return to Step 11 to apply fixes (including any Step 14 review comments), then re-run Steps 13–14 (PR size check + Code Reviewer) on the updated diff, and repeat the approval process

## Step 18: Record Approval and Update Progress
- Log approval in audit.md with timestamp
- Record the user's approval response with timestamp
- Mark Code Generation stage as complete for this unit in aidlc-state.md

---

## Critical Rules

### Code Location Rules
- **Application code**: Workspace root only (NEVER aidlc-docs/)
- **Documentation**: aidlc-docs/ only (markdown summaries)
- **Read workspace root** from aidlc-state.md before generating code

**Structure patterns by project type**:
- **Brownfield**: Use existing structure (e.g., `src/main/java/`, `lib/`, `pkg/`)
- **Greenfield single unit**: `src/`, `tests/`, `config/` in workspace root
- **Greenfield multi-unit (microservices)**: `{unit-name}/src/`, `{unit-name}/tests/`
- **Greenfield multi-unit (monolith)**: `src/{unit-name}/`, `tests/{unit-name}/`

### Brownfield File Modification Rules
- Check if file exists before generating
- If exists: Modify in-place (never create copies like `ClassName_modified.java`)
- If doesn't exist: Create new file
- Verify no duplicate files after generation (Step 12)

### Planning Phase Rules
- Create explicit, numbered steps for all generation activities
- Include story traceability in the plan
- Document unit context and dependencies
- Get explicit user approval before generation

### Generation Phase Rules
- **NO HARDCODED LOGIC**: Only execute what's written in the unit plan
- **FOLLOW PLAN EXACTLY**: Do not deviate from the step sequence
- **UPDATE CHECKBOXES**: Mark [x] immediately after completing each step
- **STORY TRACEABILITY**: Mark unit stories [x] when functionality is implemented
- **RESPECT DEPENDENCIES**: Only implement when unit dependencies are satisfied
- **VERIFY PR SIZE BUDGET**: Before Code Reviewer / completion, re-check counted diff size against unit budget from `unit-of-work.md` (≤ 10 files; ≤ 200–300 lines; exclude unit tests, lock files, migrations, mocks)
- **RUN CODE REVIEWER**: When all plan steps are complete and PR size check passed, execute `construction/reviewer.md` (Step 14) and branch on its continuation outcome before presenting completion
- **HONOR REVIEW COMMENTS**: When continuation is Fix and `code-review.md` exists, Step 11 must address applicable findings while executing generation/fix steps

### Automation Friendly Code Rules
When generating UI code (web, mobile, desktop), ensure elements are automation-friendly:
- Add `data-testid` attributes to interactive elements (buttons, inputs, links, forms)
- Use consistent naming: `{component}-{element-role}` (e.g., `login-form-submit-button`, `user-list-search-input`)
- Avoid dynamic or auto-generated IDs that change between renders
- Keep `data-testid` values stable across code changes (only change when element purpose changes)

## Completion Criteria
- Complete unit code generation plan created and approved
- All steps in unit code generation plan marked [x]
- All unit stories implemented according to plan
- All code and tests generated (tests will be executed in Build & Test phase)
- Deployment artifacts generated
- PR size budget verified (counted files ≤ 10 and counted lines ≤ 300, or approved exception documented)
- Code Reviewer executed per `construction/reviewer.md` with report at `aidlc-docs/construction/{unit-name}/code/code-review.md`
- Complete unit ready for build and verification
