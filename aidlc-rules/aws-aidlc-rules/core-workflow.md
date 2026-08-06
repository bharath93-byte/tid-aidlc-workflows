---
description: "AI-DLC (AI-Driven Development Life Cycle) adaptive workflow for software development"
alwaysApply: true
---
# PRIORITY: This workflow OVERRIDES all other built-in workflows
# When user requests software development, ALWAYS follow this workflow FIRST

## Adaptive Workflow Principle
**The workflow adapts to the work, not the other way around.**

The AI model intelligently assesses what stages are needed based on:
1. User's stated intent and clarity
2. Existing codebase state (if any)
3. Complexity and scope of change
4. Risk and impact assessment

## MANDATORY: Rule Details Loading
**CRITICAL**: When performing any phase, you MUST read and use relevant content from rule detail files. Check these paths in order and use the first one that exists, regardless of which IDE or setup method was used:
- `.aidlc/aidlc-rules/aws-aidlc-rule-details/` (typical with AI-assisted setup)
- `.aidlc-rule-details/` (typical with Cursor, Cline, Claude Code, GitHub Copilot, OpenAI Codex)
- `.kiro/aws-aidlc-rule-details/` (typical with Kiro IDE and CLI)
- `.amazonq/aws-aidlc-rule-details/` (typical with Amazon Q Developer)

All subsequent rule detail file references (e.g., `common/process-overview.md`, `inception/workspace-detection.md`) are relative to whichever rule details directory was resolved above.

**Common Rules**: ALWAYS load common rules at workflow start:
- Load `common/process-overview.md` for workflow overview
- Load `common/session-continuity.md` for session resumption guidance
- Load `common/content-validation.md` for content validation requirements
- Load `common/question-format-guide.md` for question formatting rules
- Load `common/skill-discovery-gate.md` for per-stage skill selection (Step 0 of every stage)
- Load `common/skill-artifact-adapter.md` when a skill is selected — maps skill output to stage contract artifacts
- Load `common/design-driven-dev-guide.md`, `common/hld-template.md`, `common/lld-template.md`, `common/ears-syntax.md`, `common/story-breakdown-template.md` before Application Design — these define the mandatory Global Spec-First flow (`HLD → LLD(s) → EARS → Story Breakdown → Tests → Code`) that Application Design onward must follow
- Reference these throughout the workflow execution
- Note: a `skills/` directory may also exist alongside `common/`, `inception/`, `construction/`, `operations/` in the resolved rule details directory — see "MANDATORY: Skill Discovery & Selection Gate" below for how it is used

## MANDATORY: Skill Discovery & Selection Gate (Plug-and-Play Skills)
**CRITICAL**: This gate makes the workflow extensible by third parties without editing this file. It applies to EVERY stage in Inception, Construction, and Operations, immediately before that stage's "Load all steps from `<phase>/<stage-file>.md`" instruction is executed — including when resuming mid-workflow or advancing via an approval gate (e.g. "Continue to Next Stage") into a new stage.

**Skill convention**: Framework skills live at `skills/<phase>/<skill-name>/` in the resolved rule details directory (e.g. `skills/inception/domain-modeling/`, `skills/construction/api-standards-review/`), where `<phase>` is `inception`, `construction`, or `operations`. Project skills may also live at `.cursor/skills/<skill-name>/` in the workspace root (flat layout). Each skill folder contains a `SKILL.md` (required) and optionally a `SKILL_CARD.md` (short summary). Anyone can drop a new skill folder in without touching this workflow.

**Execution (per stage, before loading its rule file)**:
1. **Discover skills** — scan both locations and merge results (dedupe by folder path):
   - `skills/<phase>/` under the resolved rule details directory (subfolders containing `SKILL.md`)
   - `.cursor/skills/` under the workspace root (subfolders containing `SKILL.md`; include all — user selects relevance)
2. **Always ask** — create `aidlc-docs/{stage-name}-skill-selection.md` using the format in `common/question-format-guide.md`, scoped to the current phase and current stage by name, in one of two shapes:
   - **If one or more skills found**: one option per discovered skill (name + one-line description from `SKILL_CARD.md`, or the first description line of `SKILL.md`, + its folder path), plus a "Use standard AI-DLC rules only (no skill)" option, plus the MANDATORY "Other" option — reused to let the user type a path to their own external skill (e.g. `.cursor/skills/my-skill/SKILL.md`) instead of one from the list.
   - **If none found for this phase/stage**: still ask, don't assume — options are "No skill available for this — proceed with standard AI-DLC rules" plus the MANDATORY "Other" option, reused to let the user point to a skill of their own (anywhere on disk, or an internal skill the discovery scan couldn't see) for this specific phase and stage.
3. Inform the user the question file is ready; **wait** for them to fill `[Answer]:` tags and confirm — do NOT load the stage rule file or generate stage artifacts until the answer is received.
4. Resolve the answer:
   - Standard rules selected → proceed exactly as this workflow already specifies for the stage
   - A listed skill, or a valid "Other" path, selected → execute `SKILL.md` for methodology (HOW), then **mandatory** `common/skill-artifact-adapter.md` to produce the **same** contract artifacts the stage rule defines (WHAT). Do **not** add skill/adapter logic to stage rule files
   - Invalid "Other" path → report the problem and re-ask; do not guess
5. **MANDATORY**: Log the resolved choice (skill name/path, or "standard rules") for this stage in audit.md.

This gate does not replace or skip the stage's existing approval gates (e.g. "Request Changes"/"Continue to Next Stage") — those still run after the skill (or the rules) produce their output.

## MANDATORY: Extensions Loading (Context-Optimized)
**CRITICAL**: At workflow start, scan the `extensions/` directory recursively but load ONLY lightweight opt-in files — NOT full rule files. Full rule files are loaded on-demand after the user opts in.

**Loading process**:
1. List all subdirectories under `extensions/` (e.g., `extensions/security/`, `extensions/compliance/`)
2. In each subdirectory, load ONLY `*.opt-in.md` files — these contain the extension's opt-in prompt. The corresponding rules file is derived by convention: strip the `.opt-in.md` suffix and append `.md` (e.g., `security-baseline.opt-in.md` → `security-baseline.md`)
3. Do NOT load full rule files (e.g., `security-baseline.md`) at this stage

**Deferred Rule Loading**:
- During Requirements Analysis, opt-in prompts from the loaded `*.opt-in.md` files are presented to the user
- When the user opts IN for an extension, load the corresponding rules file (derived by naming convention) at that point
- When the user opts OUT, the full rules file is never loaded — saving context
- Extensions without a matching `*.opt-in.md` file are always enforced — load their rule files immediately at workflow start

**Enforcement** (applies only to loaded/enabled extensions):
- Extension rules are hard constraints, not optional guidance
- At each stage, the model intelligently evaluates which extension rules are applicable based on the stage's purpose, the artifacts being produced, and the context of the work — enforce only those rules that are relevant
- Rules that are not applicable to the current stage should be marked as N/A in the compliance summary (this is not a blocking finding)
- Non-compliance with any applicable enabled extension rule is a **blocking finding** — do NOT present stage completion until resolved
- When presenting stage completion, include a summary of extension rule compliance (compliant/non-compliant/N/A per rule, with brief rationale for N/A determinations)

**Conditional Enforcement**: Extensions may be conditionally enabled/disabled. See `inception/requirements-analysis.md` for the opt-in mechanism. Before enforcing any extension at ANY stage, check its `Enabled` status in `aidlc-docs/aidlc-state.md` under `## Extension Configuration`. Skip disabled extensions and log the skip in audit.md. Default to enforced if no configuration exists. 

## MANDATORY: Content Validation
**CRITICAL**: Before creating ANY file, you MUST validate content according to `common/content-validation.md` rules:
- Validate Mermaid diagram syntax
- Validate ASCII art diagrams (see `common/ascii-diagram-standards.md`)
- Escape special characters properly
- Provide text alternatives for complex visual content
- Test content parsing compatibility

## MANDATORY: Question File Format
**CRITICAL**: When asking questions at any phase, you MUST follow question format guidelines.

**See `common/question-format-guide.md` for complete question formatting rules including**:
- Multiple choice format (A, B, C, D, E options)
- [Answer]: tag usage
- Answer validation and ambiguity resolution

## MANDATORY: Custom Welcome Message
**CRITICAL**: When starting ANY software development request, you MUST display the welcome message.

**How to Display Welcome Message**:
1. Load the welcome message from `common/welcome-message.md` (in the resolved rule details directory)
2. Display the complete message to the user
3. This should only be done ONCE at the start of a new workflow
4. Do NOT load this file in subsequent interactions to save context space

# Adaptive Software Development Workflow

---

# INCEPTION PHASE

**Purpose**: Planning, requirements gathering, and architectural decisions

**Focus**: Determine WHAT to build and WHY

**Stages in INCEPTION PHASE**:
- Workspace Detection (ALWAYS)
- Reverse Engineering (CONDITIONAL - Brownfield only)
- Requirements Analysis (ALWAYS - Adaptive depth)
- Workflow Planning (ALWAYS)
- Application Design (CONDITIONAL)
- Units Generation (CONDITIONAL)
- Artifact Generation (CONDITIONAL)

---

## Workspace Detection (ALWAYS EXECUTE)

1. **MANDATORY**: Log initial user request in audit.md with complete raw input
2. Load all steps from `inception/workspace-detection.md`
3. Execute workspace detection:
   - Check for existing aidlc-state.md (resume if found)
   - Scan workspace for existing code
   - Determine if brownfield or greenfield
   - Check for existing reverse engineering artifacts
4. Determine next phase: Reverse Engineering (if brownfield and no artifacts) OR Requirements Analysis
5. **MANDATORY**: Log findings in audit.md
6. Present completion message to user (see workspace-detection.md for message formats)
7. Automatically proceed to next phase

## Reverse Engineering (CONDITIONAL - Brownfield Only)

**Execute IF**:
- Existing codebase detected
- No previous reverse engineering artifacts found

**Skip IF**:
- Greenfield project
- Previous reverse engineering artifacts exist

**Execution**:
1. **MANDATORY**: Log start of reverse engineering in audit.md
2. Load all steps from `inception/reverse-engineering.md`
3. Execute reverse engineering:
   - Analyze all packages and components
   - Generate a business overview of the whole system covering the business transactions
   - Generate architecture documentation
   - Generate code structure documentation
   - Generate API documentation
   - Generate component inventory
   - Generate Interaction Diagrams depicting how business transactions are implemented across components
   - Generate technology stack documentation
   - Generate dependencies documentation

4. **Wait for Explicit Approval**: Present detailed completion message (see reverse-engineering.md for message format) - DO NOT PROCEED until user confirms
5. **MANDATORY**: Log user's response in audit.md with complete raw input

## Requirements Analysis (ALWAYS EXECUTE - Adaptive Depth)

**Always executes** but depth varies based on request clarity and complexity:
- **Minimal**: Simple, clear request - just document intent analysis
- **Standard**: Normal complexity - gather functional and non-functional requirements
- **Comprehensive**: Complex, high-risk - detailed requirements with traceability

**Execution**:
1. **MANDATORY**: Log any user input during this phase in audit.md
2. Load all steps from `inception/requirements-analysis.md`
3. Execute requirements analysis:
   - Load reverse engineering artifacts (if brownfield)
   - Analyze user request (intent analysis)
   - Determine requirements depth needed
   - Assess current requirements
   - Ask clarifying questions (if needed)
   - Document requirements comprehensively
4. Execute at appropriate depth (minimal/standard/comprehensive)
5. **Wait for Explicit Approval**: Follow approval format from requirements-analysis.md detailed steps - DO NOT PROCEED until user confirms
6. **MANDATORY**: Log user's response in audit.md with complete raw input

## Workflow Planning (ALWAYS EXECUTE)

1. **MANDATORY**: Log any user input during this phase in audit.md
2. Load all steps from `inception/workflow-planning.md`
3. **MANDATORY**: Load content validation rules from `common/content-validation.md`
4. Load all prior context:
   - Reverse engineering artifacts (if brownfield)
   - Intent analysis
   - Requirements (if executed)
   - User stories (if executed)
5. Execute workflow planning:
   - Determine which phases to execute
   - Determine depth level for each phase
   - Create multi-package change sequence (if brownfield)
   - Generate workflow visualization (VALIDATE Mermaid syntax before writing)
6. **MANDATORY**: Validate all content before file creation per content-validation.md rules
7. **Wait for Explicit Approval**: Present recommendations using language from workflow-planning.md Step 9, emphasizing user control to override recommendations - DO NOT PROCEED until user confirms
8. **MANDATORY**: Log user's response in audit.md with complete raw input

## Application Design (CONDITIONAL)

**Execute IF**:
- New components or services needed
- Component methods and business rules need definition
- Service layer design required
- Component dependencies need clarification

**Skip IF**:
- Changes within existing component boundaries
- No new components or methods
- Pure implementation changes

**Execution**:
1. **MANDATORY**: Log any user input during this phase in audit.md
2. Load all steps from `inception/application-design.md`, `common/hld-template.md`, `common/lld-template.md`, and `common/ears-syntax.md`
3. Load reverse engineering artifacts (if brownfield)
4. Execute at appropriate depth (minimal/standard/comprehensive) — depth affects how many components get their own LLD file and how many EARS statements are generated, not whether HLD/LLD/EARS are produced (mandatory at every depth level)
5. **MANDATORY — Global Spec-First order**: within this stage, produce artifacts strictly in this order: (a) `hld.md`, (b) one `lld.md` per major component (Step 10.1), (c) EARS requirements derived from each `lld.md` (Step 10.2). Do not generate EARS before the LLD it's derived from exists.
6. **Wait for Explicit Approval**: Present detailed completion message (see application-design.md for message format) - DO NOT PROCEED until user confirms
7. **MANDATORY**: Log user's response in audit.md with complete raw input

## Units Generation (CONDITIONAL)

**Execute IF**:
- System needs decomposition into multiple units of work
- Multiple services or modules required
- Complex system requiring structured breakdown

**Skip IF**:
- Single simple unit
- No decomposition needed
- Straightforward single-component implementation

**This stage is the "Story Breakdown" step of the Global Spec-First flow** (`HLD → LLD → EARS → Story Breakdown → Tests → Code`) — see `common/design-driven-dev-guide.md`.

**Execution**:
1. **MANDATORY**: Log any user input during this phase in audit.md
2. Load all steps from `inception/units-generation.md` and `common/story-breakdown-template.md`
3. Load reverse engineering artifacts (if brownfield)
4. Execute at appropriate depth (minimal/standard/comprehensive)
5. **MANDATORY**: Enforce PR size guardrails from `units-generation.md` when splitting units (each unit sized for easy PR review)
6. **MANDATORY**: Assign every in-scope EARS requirement (from `aidlc-docs/inception/requirements/ears/`) to exactly one unit's EARS Coverage
7. **Wait for Explicit Approval**: Present detailed completion message (see units-generation.md for message format) - DO NOT PROCEED until user confirms
8. **MANDATORY**: Log user's response in audit.md with complete raw input

## Artifact Generation (CONDITIONAL)

**Execute IF**:
- Requirements Analysis was executed
- Formal stakeholder-facing artifacts are needed (PRD, consolidated requirements traceability report)
- Stakeholder documentation is required

**Skip IF**:
- Simple task with no need for formal documentation
- Artifact types already exist and are up to date

**Note on scope**: HLD, LLDs, and EARS already exist as of Application Design — they are the single source of truth and are **not regenerated here**. This stage produces the stakeholder-facing PRD and a traceability rollup only.

**Execution**:
1. **MANDATORY**: Log any user input during this phase in audit.md
2. Load reference artifacts (all that exist):
   - `aidlc-docs/inception/requirements/` — requirements (EARS files + index)
   - `aidlc-docs/inception/application-design/` — application design, `hld.md`, `lld/`, `unit-of-work.md` (personas + story breakdown, if generated)
   - `aidlc-docs/inception/plans/` — units
   - `aidlc-docs/inception/reverse-engineering/` — reverse engineering (brownfield only)
3. Generate **PRD** (`aidlc-docs/inception/artifacts/prd.md`):
   - Load template from `common/prd-template.md` (in resolved rule details directory)
   - Use all loaded reference artifacts as input context; cite EARS IDs (not free-text restatements) in the User Stories / Acceptance Criteria / NFR sections
   - Populate every section of the template with content derived from the reference artifacts
4. Generate **Requirements Traceability Report** (`aidlc-docs/inception/artifacts/requirements-traceability.md`): compile a rollup table (EARS file | ID range | Category | Priority | Status counts | Assigned Unit(s)) — link to EARS files rather than duplicating them
5. Reference the existing **HLD/LLDs** (`aidlc-docs/inception/application-design/hld.md`, `lld/`) — do not regenerate with `technical-design-document-template.md`; if they don't exist (Application Design was skipped), note the gap rather than fabricating them
6. **Wait for Explicit Approval**: Present completion message listing the generated artifacts and their paths - DO NOT PROCEED until user confirms
7. **MANDATORY**: Log user's response in audit.md with complete raw input

---

# 🟢 CONSTRUCTION PHASE

**Purpose**: Detailed design, NFR implementation, and code generation

**Focus**: Determine HOW to build it

**Stages in CONSTRUCTION PHASE**:
- Per-Unit Loop (executes for each unit):
  - Functional Design (CONDITIONAL, per-unit)
  - NFR Requirements (CONDITIONAL, per-unit)
  - NFR Design (CONDITIONAL, per-unit)
  - Infrastructure Design (CONDITIONAL, per-unit)
  - Code Generation (ALWAYS, per-unit) — **default: TDD** (`construction/tdd-code-generation.md`)
- Build and Test (ALWAYS - after all units complete)

**Note**: Each unit is completed fully (design + code) before moving to the next unit.

**Code Generation Method** (selected before Construction code generation runs):
- **Default**: TDD Code Generation — load `construction/tdd-code-generation.md`
- **Standard (opt-in)**: Normal Code Generation — load `construction/code-generation.md` only when the user explicitly requests it while approving the Workflow Planning / proceeding to Construction
- **MANDATORY**: Log the selected generation method in `aidlc-docs/aidlc-state.md` and `aidlc-docs/audit.md` (see Code Generation stage)

---

## Per-Unit Loop (Executes for Each Unit)

**For each unit of work, execute the following stages in sequence:**

### Functional Design (CONDITIONAL, per-unit)

**Execute IF**:
- New data models or schemas
- Complex business logic
- Business rules need detailed design

**Skip IF**:
- Simple logic changes
- No new business logic

**Execution**:
1. **MANDATORY**: Log any user input during this stage in audit.md
2. Load all steps from `construction/functional-design.md`
3. Execute functional design for this unit
4. **MANDATORY**: Present standardized 2-option completion message as defined in functional-design.md - DO NOT use emergent 3-option behavior
5. **Wait for Explicit Approval**: User must choose between "Request Changes" or "Continue to Next Stage" - DO NOT PROCEED until user confirms
6. **MANDATORY**: Log user's response in audit.md with complete raw input

### NFR Requirements (CONDITIONAL, per-unit)

**Execute IF**:
- Performance requirements exist
- Security considerations needed
- Scalability concerns present
- Tech stack selection required

**Skip IF**:
- No NFR requirements
- Tech stack already determined

**Execution**:
1. **MANDATORY**: Log any user input during this stage in audit.md
2. Load all steps from `construction/nfr-requirements.md`
3. Execute NFR assessment for this unit
4. **MANDATORY**: Present standardized 2-option completion message as defined in nfr-requirements.md - DO NOT use emergent behavior
5. **Wait for Explicit Approval**: User must choose between "Request Changes" or "Continue to Next Stage" - DO NOT PROCEED until user confirms
6. **MANDATORY**: Log user's response in audit.md with complete raw input

### NFR Design (CONDITIONAL, per-unit)

**Execute IF**:
- NFR Requirements was executed
- NFR patterns need to be incorporated

**Skip IF**:
- No NFR requirements
- NFR Requirements was skipped

**Execution**:
1. **MANDATORY**: Log any user input during this stage in audit.md
2. Load all steps from `construction/nfr-design.md`
3. Execute NFR design for this unit
4. **MANDATORY**: Present standardized 2-option completion message as defined in nfr-design.md - DO NOT use emergent behavior
5. **Wait for Explicit Approval**: User must choose between "Request Changes" or "Continue to Next Stage" - DO NOT PROCEED until user confirms
6. **MANDATORY**: Log user's response in audit.md with complete raw input

### Infrastructure Design (CONDITIONAL, per-unit)

**Execute IF**:
- Infrastructure services need mapping
- Deployment architecture required
- Cloud resources need specification

**Skip IF**:
- No infrastructure changes
- Infrastructure already defined

**Execution**:
1. **MANDATORY**: Log any user input during this stage in audit.md
2. Load all steps from `construction/infrastructure-design.md`
3. Execute infrastructure design for this unit
4. **MANDATORY — LLD Refinement**: Update the owning component's `aidlc-docs/inception/application-design/lld/{component}.md` Infrastructure Mapping section (Step 6.1 of `infrastructure-design.md`) with this unit's choices — edit in place, do not create a second design document
5. **MANDATORY**: Present standardized 2-option completion message as defined in infrastructure-design.md - DO NOT use emergent behavior
6. **Wait for Explicit Approval**: User must choose between "Request Changes" or "Continue to Next Stage" - DO NOT PROCEED until user confirms
7. **MANDATORY**: Log user's response in audit.md with complete raw input

### Code Generation (ALWAYS EXECUTE, per-unit)

**Always executes for each unit**

**Default generation method: TDD** (`construction/tdd-code-generation.md`).  
**Standard** Code Generation (`construction/code-generation.md`) runs only when the user explicitly opts in while approving Workflow Planning / proceeding to Construction. If the user does not specify standard/normal code generation, use TDD.

**Code Generation has two parts within one stage**:
1. **Part 1 - Planning**: Create detailed code generation plan with explicit steps (TDD cycles by default)
2. **Part 2 - Generation**: Execute approved plan to generate code, tests, and artifacts

**Execution**:
1. **MANDATORY**: Log any user input during this stage in audit.md
2. **Resolve generation method** (before loading rule details):
   - Read `Code Generation Method` from `aidlc-docs/aidlc-state.md` if already set during Workflow Planning
   - If unset: default to **TDD**; use **Standard** only if the user has explicitly requested normal/standard code generation
   - **MANDATORY — Log generation method** in `aidlc-docs/aidlc-state.md`:

```markdown
## Code Generation Method
- **Method**: TDD | Standard
- **Rule file**: construction/tdd-code-generation.md | construction/code-generation.md
- **Selected at**: [ISO timestamp]
- **Selected by**: default | explicit user request
- **User request (raw, if any)**: "[complete raw user text or N/A]"
```

   - **MANDATORY — Log generation method** in `aidlc-docs/audit.md` with ISO 8601 IST timestamp, method, rule file, and whether it was default or explicit user request (include complete raw user input when they requested Standard)
3. Load all steps from the selected rule file:
   - **TDD (default)**: `construction/tdd-code-generation.md`
   - **Standard (opt-in)**: `construction/code-generation.md`
4. **PART 1 - Planning**: Create code generation plan with checkboxes, get user approval; read the unit's EARS Coverage from `unit-of-work.md`
5. **PART 2 - Generation**: Execute approved plan to generate code for this unit; **MANDATORY**: annotate code and tests with `@spec {EARS-ID}` comments (see `common/ears-syntax.md`), and flip each EARS ID's status marker from `[ ]` to `[x]` in `aidlc-docs/inception/requirements/ears/` only once its `@spec`-annotated tests are green
6. **MANDATORY**: Present standardized 2-option completion message as defined in the selected rule file - DO NOT use emergent behavior
7. **Wait for Explicit Approval**: User must choose between "Request Changes" or "Continue to Next Stage" - DO NOT PROCEED until user confirms
8. **MANDATORY**: Log user's response in audit.md with complete raw input

---

## Build and Test (ALWAYS EXECUTE)

1. **MANDATORY**: Log any user input during this phase in audit.md
2. Load all steps from `construction/build-and-test.md`
3. Generate comprehensive build and test instructions:
   - Build instructions for all units
   - Unit test execution instructions
   - Integration test instructions (test interactions between units)
   - Performance test instructions (if applicable)
   - Additional test instructions as needed (contract tests, security tests, e2e tests)
   - **EARS traceability rollup**: verify status markers across `aidlc-docs/inception/requirements/ears/` match actual test results; correct any marker Code Generation flipped incorrectly
4. Create instruction files in build-and-test/ subdirectory: build-instructions.md, unit-test-instructions.md, integration-test-instructions.md, performance-test-instructions.md, build-and-test-summary.md (with EARS coverage rollup)
5. **Wait for Explicit Approval**: Ask: "**Build and test instructions complete. Ready to proceed to Operations stage?**" - DO NOT PROCEED until user confirms
6. **MANDATORY**: Log user's response in audit.md with complete raw input

---

# 🟡 OPERATIONS PHASE

**Purpose**: Placeholder for future deployment and monitoring workflows

**Focus**: How to DEPLOY and RUN it (future expansion)

**Stages in OPERATIONS PHASE**:
- Operations (PLACEHOLDER)

---

## Operations (PLACEHOLDER)

**Status**: This stage is currently a placeholder for future expansion.

The Operations stage will eventually include:
- Deployment planning and execution
- Monitoring and observability setup
- Incident response procedures
- Maintenance and support workflows
- Production readiness checklists

**Current State**: All build and test activities are handled in the CONSTRUCTION phase.

## Key Principles

- **Adaptive Execution**: Only execute stages that add value
- **Transparent Planning**: Always show execution plan before starting
- **User Control**: User can request stage inclusion/exclusion
- **Progress Tracking**: Update aidlc-state.md with executed and skipped stages
- **Complete Audit Trail**: Log ALL user inputs and AI responses in audit.md with timestamps
  - **CRITICAL**: Capture user's COMPLETE RAW INPUT exactly as provided
  - **CRITICAL**: Never summarize or paraphrase user input in audit log
  - **CRITICAL**: Log every interaction, not just approvals
- **Quality Focus**: Complex changes get full treatment, simple changes stay efficient
- **Content Validation**: Always validate content before file creation per content-validation.md rules
- **NO EMERGENT BEHAVIOR**: Construction phases MUST use standardized 2-option completion messages as defined in their respective rule files. DO NOT create 3-option menus or other emergent navigation patterns.

## MANDATORY: Plan-Level Checkbox Enforcement

### MANDATORY RULES FOR PLAN EXECUTION
1. **NEVER complete any work without updating plan checkboxes**
2. **IMMEDIATELY after completing ANY step described in a plan file, mark that step [x]**
3. **This must happen in the SAME interaction where the work is completed**
4. **NO EXCEPTIONS**: Every plan step completion MUST be tracked with checkbox updates

### Two-Level Checkbox Tracking System
- **Plan-Level**: Track detailed execution progress within each stage
- **Stage-Level**: Track overall workflow progress in aidlc-state.md
- **Update immediately**: All progress updates in SAME interaction where work is completed

## Prompts Logging Requirements
- **MANDATORY**: Log EVERY user input (prompts, questions, responses) with timestamp in audit.md
- **MANDATORY**: Capture user's COMPLETE RAW INPUT exactly as provided (never summarize)
- **MANDATORY**: Log every approval prompt with timestamp before asking the user
- **MANDATORY**: Record every user response with timestamp after receiving it
- **CRITICAL**: ALWAYS append changes to EDIT audit.md file, NEVER use tools and commands that completely overwrite its contents
- **CRITICAL**: NEVER use file writing tools and commands that overwrite the entire contents of audit.md, as this causes duplication
- Use ISO 8601 format for timestamps in **IST** (`YYYY-MM-DDTHH:mm:ss+05:30`)
- Include **User** (actor) as the user name only — never include email (resolve from `git config user.name` or OS username)
- Include stage context for each entry

### Audit Log Format:
```markdown
## [Stage Name or Interaction Type]
**Timestamp**: [ISO 8601 IST, e.g. 2026-08-05T16:32:00+05:30]
**User**: [User name only — do not include email]
**User Input**: "[Complete raw user input - never summarized]"
**AI Response**: "[AI's response or action taken]"
**Context**: [Stage, action, or decision made]

---
```

### Correct Tool Usage for audit.md

✅ CORRECT:

1. Read the audit.md file
2. Append/Edit the file to make changes

❌ WRONG:

1. Read the audit.md file
2. Completely overwrite the audit.md with the contents of what you read, plus the new changes you want to add to it

## Directory Structure

```text
<WORKSPACE-ROOT>/                   # ⚠️ APPLICATION CODE HERE
├── [project-specific structure]    # Varies by project (see code-generation.md)
│
├── aidlc-docs/                     # 📄 DOCUMENTATION ONLY
│   ├── inception/                  # 🔵 INCEPTION PHASE
│   │   ├── plans/
│   │   ├── reverse-engineering/    # Brownfield only
│   │   ├── requirements/
│   │   │   ├── requirement-verification-questions.md
│   │   │   ├── requirements.md     # Prose context + index into ears/
│   │   │   └── ears/               # Canonical EARS requirements (derived from LLDs)
│   │   │       └── {feature}-{subfeature}-ears.md
│   │   ├── application-design/
│   │   │   ├── components.md, component-methods.md, services.md, component-dependency.md
│   │   │   ├── hld.md              # Canonical High-Level Design
│   │   │   ├── lld/                # One Low-Level Design per component (refined by Construction)
│   │   │   │   └── {component}.md
│   │   │   ├── personas.md         # Optional — generated in Units Generation, not a separate stage
│   │   │   └── unit-of-work.md, unit-of-work-dependency.md, unit-of-work-story-map.md  # Story Breakdown: EARS Coverage + Gherkin/user-story framing per unit
│   │   └── artifacts/              # prd.md, requirements-traceability.md (rollup only)
│   ├── construction/               # 🟢 CONSTRUCTION PHASE
│   │   ├── plans/
│   │   ├── {unit-name}/
│   │   │   ├── functional-design/  # Refines owning component's lld.md
│   │   │   ├── nfr-requirements/   # Refines owning component's lld.md
│   │   │   ├── nfr-design/         # Refines owning component's lld.md
│   │   │   ├── infrastructure-design/  # Refines owning component's lld.md
│   │   │   └── code/               # Markdown summaries only; code is @spec-annotated to EARS IDs
│   │   └── build-and-test/         # includes EARS coverage rollup in build-and-test-summary.md
│   ├── operations/                 # 🟡 OPERATIONS PHASE (placeholder)
│   ├── aidlc-state.md
│   └── audit.md
```

**CRITICAL RULE**:
- Application code: Workspace root (NEVER in aidlc-docs/)
- Documentation: aidlc-docs/ only
- Project structure: See code-generation.md for patterns by project type
