---
name: aidlc-design-driven-dev
description: Guide for design-driven development with prescribed folder structure. Large/new features use the full workflow (HLD → LLD → EARS); minor bugs or small stories use the Lightweight tier (skip HLD and LLD, EARS only); pure bug fixes skip doc creation but verify intent coherence.
---

# Design-Driven Development

This skill guides a structured design-driven development workflow. The goal is to get alignment on what you're building *before* writing code, which dramatically reduces rework and misunderstandings.

## Step 0: Load pipeline state (state-loader)

Before starting any design work, if it hasn't already run in this session, invoke the **state-loader** skill to load `pipeline-config.json` and the `state.json` **of the currently-resolved epic** — the file inside this epic's own context directory (`aidlc-docs/<epic-name>_<epic-id>/`), not just any epic's file. If the epic context directory cannot be resolved from context, **ask the user which epic** (folder name or Jira key) before proceeding. Use its resolved `EPIC_DIR` as your `DOCS_DIR` (this supersedes re-deriving the path in *DOCS_DIR Discovery* below). This guarantees you resume at the correct pipeline position when a user or another developer continues the work, and that `status`/`audit.md` stay in lockstep as phases are approved.

## ADR Prerequisite Check

After state-loader resolves `EPIC_DIR` / `DOCS_DIR`, verify before any design work:

1. **`status` must be `adr-completed` or `design-in-progress`.** If `status` is `inception-completed` or earlier, stop and tell the user to run `aidlc-adr` (or re-run `aidlc-init`) before starting design.
2. **`DOCS_DIR/system-prompts/adr_decisions.xml` must exist.** If missing, stop and tell the user to complete `aidlc-adr` and ADR system-prompt compression (`generate-system-prompts` ADR mode).
3. **Migration:** If `status` is `inception-completed` (legacy epics), route to `aidlc-adr` — do not proceed to HLD.

## Critical Rule: Stop, Iterate, and Audit

**STOP after completing each phase.** Present the document to the user for review. Incorporate their numbered feedback. Only proceed to the next phase when explicitly approved.

This is the most important part of the workflow. Don't rush through design to get to code.

**MANDATORY AUDIT LOGGING:** 
Every time the user explicitly approves a phase (HLD, LLD, or EARS), you MUST update the `audit.md` file located at `DOCS_DIR/audit.md` *before* starting the next phase. 
*   If the file does not exist, create it with the standard markdown table headers (`| Timestamp | Phase | Skill/Agent | Action | Approver |`).
*   Append a new row using the current UTC timestamp and the current developer's system username.
*   Example row: `| 2026-07-29T12:45Z | design | design-driven-dev | <Specific action described below> | <username> |`

## DOCS_DIR Discovery & State Check

Before starting any design work, you must determine the correct epic context to locate the documentation directory.

1. **Identify the Epic:** If the user hasn't specified which epic they are working on, ask them (e.g., "Which epic are we designing for? Please provide the key like IAM-123 or the name").
2. **Locate the Directory:** Search the `aidlc-docs/` directory for a folder matching the provided epic key or name. The canonical format is `aidlc-docs/<epic-name>_<epic-id>/`.
3. **Read `state.json`:** Once the folder is found, read the `state.json` file inside it to strictly confirm the `"epic-id"` and `"epic-name"`. 
4. **Set DOCS_DIR:** Set your working `DOCS_DIR` strictly to `aidlc-docs/<epic-name>_<epic-id>` based on the values in `state.json`. All generated docs (HLD, LLD, EARS, and updated `audit.md`) MUST be saved inside this specific directory.
5. **Ingest Vision Document:** You MUST read `DOCS_DIR/vision.md`. This establishes the business goals, architectural North Star, and scope. The technical designs you create MUST **perfectly** align with this document.
6. **Ingest XML System Prompts:** You MUST read the structured XML files located in `DOCS_DIR/system-prompts/` — at minimum `context.xml` and `adr_decisions.xml`. These files contain critical data constraints, integration boundaries, hard user decisions, and locked architecture decisions from ADR. Treat these XML constraints as the absolute factual baseline for your entire DDD flow. **Cite ADR IDs** (e.g., ADR-001) in HLD/LLD/EARS where a design choice implements or depends on an ADR decision.

## Folder Structure

```
DOCS_DIR/
├── high-level-design.md           # Single HLD for entire project
└── designs/
    └── <feature-name>/           # only if the epic is big enough for multiple features, else keep below under one level
        ├── LLD.md                 # Low-level design for feature
        ├── -EARS.md
        ├── -EARS.md
        └── ...
```

**Example:**
```
DOCS_DIR/
├── high-level-design.md
└── designs/
    ├── authentication/
    │   ├── LLD.md
    │   ├── login-EARS.md
    │   ├── logout-EARS.md
    │   └── password-reset-EARS.md
    └── payments/
        ├── LLD.md
        ├── checkout-EARS.md
        └── refunds-EARS.md
```

## Workflow Overview

1. **High-Level Design (HLD)** - Project vision and architecture → `DOCS_DIR/high-level-design.md`
2. **Low-Level Design (LLD)** - Feature-specific technical design → `DOCS_DIR/designs/<feature>/LLD.md`
3. **EARS Specifications** - Sub-feature requirements → `DOCS_DIR/designs/<feature>/<subfeature>-EARS.md`

See [hld-template.md](./references/hld-template.md) for HLD structure guidance.

## Complexity Tiers: Which Phases to Run

Before Phase 1, assess the size of the change and pick a tier. State the chosen tier to the user in one line and let them override it. **When unsure, default to Full — over-designing is safer than under-designing.** Only the phases for the chosen tier run; every phase that runs still STOPS for explicit approval and is logged to `audit.md`.

**Full tier — run HLD → LLD(s) → EARS.** Use for:
- New features, large epics, or multi-feature / multi-component work
- Major refactors or significant behavior changes

**Lightweight tier — skip HLD and LLD; run EARS only, then proceed.** Use for:
- Minor bugs or small stories (e.g. a two-or-three-files change)
- Localized changes that introduce no new architecture and touch a single existing component

**Coherence check only (no new docs) for:**
- Pure bug fixes, quick changes (<30 minutes), or debugging sessions where existing EARS already cover the behavior — verify intent coherence and update in place instead of creating new docs.

## Phase 1: High-Level Design

**File:** `DOCS_DIR/high-level-design.md`

> **Skip this phase for the Lightweight tier** (minor bug / small story). Go straight to Phase 3 (EARS).

Check if an HLD exists first. For new projects or major features, create an HLD covering:
- Problem statement and goals
- Target users and personas
- System architecture overview
- Key design decisions and trade-offs (reference ADR IDs from `adr_decisions.xml`)
- Non-goals (what's explicitly out of scope)

**Required: Link to LLDs**
```
## Related Designs

- [Authentication LLD](./designs/authentication/LLD.md)
- [Payments LLD](./designs/payments/LLD.md)
```

See [hld-template.md](./references/hld-template.md) for full structure with examples.

**Stop and get user approval.** Upon approval, append a row to `DOCS_DIR/audit.md` with Action: `High-Level Design (HLD) generated and approved.` before proceeding.

## Phase 2: Low-Level Design

**File:** `DOCS_DIR/designs/<feature>/LLD.md`

> **Skip this phase for the Lightweight tier** (minor bug / small story). Go straight to Phase 3 (EARS).

Create one LLD per major feature. Each LLD should include:

* Component overview and context
* Design patterns (e.g., Factory, Strategy, State machines) explicitly call out applied patterns
* Data models, state management, and interfaces
* API contracts (if applicable)
* Error handling, edge cases, and logging strategies
* Performance considerations (e.g., caching, database indexing, latency)
* Code complexity and modularity constraints (ensuring maintainability and reusability)
* Dependencies and third-party integrations

**Required: Link to HLD and EARS**

```
## Related Documents

- [High-Level Design](../high-level-design.md)
- [Login EARS](./login-EARS.md)
- [Logout EARS](./logout-EARS.md)

```

See [lld-template.md](./references/lld-template.md) for structure guidance, including when to use narrative vs. structured format.

**Stop and get user approval.** Upon approval, append a row to `DOCS_DIR/audit.md` with Action: `Low-Level Design (LLD) for <feature> generated and approved.` before proceeding.

## Phase 3: EARS Specifications

**File:** `DOCS_DIR/designs/<feature>/<subfeature>-EARS.md`

Generate requirements using EARS (Easy Approach to Requirements Syntax). Create one EARS file per sub-feature.

**Required: Link to parent LLD** (Full tier). For the **Lightweight tier** (no HLD/LLD), link back to `vision.md` and cite the relevant ADR IDs from `adr_decisions.xml` instead.

```
## Related Documents

- [Authentication LLD](./LLD.md)

```

See [ears-syntax.md](./references/ears-syntax.md) for full EARS syntax, semantic ID format, and scope disambiguation guidance.

**Stop and get user approval.** Upon approval, append a row to `DOCS_DIR/audit.md` with Action: `EARS specifications for <subfeature> generated and approved.` before proceeding.

## Cross-Document Linking Rules

### HLD → LLD

HLD **must** link to all LLDs:

```
## Related Designs

- [Authentication LLD](./designs/authentication/LLD.md)
- [Payments LLD](./designs/payments/LLD.md)

```

### LLD → HLD

LLD **must** link back to HLD:

```
## Related Documents

- [High-Level Design](../high-level-design.md)

```

### LLD → EARS

LLD **must** link to all its EARS files:

```
## Requirements

- [Login Form EARS](./login-EARS.md)
- [Password Reset EARS](./password-reset-EARS.md)

```

### EARS → LLD

EARS **must** link back to parent LLD:

```
## Related Documents

- [Authentication LLD](./LLD.md)

```

## Maintaining Intent Coherence

### The Arrow of Intent

There's a chain of documents that translates intent from HLD to modular EARS:

```
HLD → LLDs → EARS

```

Each level translates the previous into more specific terms:

* **HLD** says *what* and *why*
* **LLDs** say *how* at a feature level
* **EARS** says *exactly what must be true* in testable terms

### The Principle: Coherence Over History

The arrow of intent must stay coherent. When one level changes, downstream levels must be reviewed and updated to match.

**Mutation, not accumulation.** Update docs in place. Delete what's wrong. The documentation should always reflect *current* intent.

### The Practice: Cascade Changes Downward

When requirements or understanding change:

1. **Identify the entry point** - Where in the chain does this change originate?
2. **Update at that level** - Mutate the doc directly
3. **Cascade downward** - Review and update each subsequent level:
    * HLD change → review LLDs → review EARS 
    * LLD change → review EARS 
    * EARS change → Get approval and update audit.md as said above
4. **Delete what's obsolete** - Delete specs that no longer apply

**ADR rollback:** If a design change reopens an architecture decision locked in ADR, rollback `status` to `adr-completed` (per `pipeline-config.json` transitions) and revise `adr.md` + `adr_decisions.xml` before continuing HLD/LLD/EARS work.