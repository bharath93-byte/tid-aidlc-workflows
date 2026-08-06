# Session Continuity Templates

## Welcome Back Prompt Template
When a user returns to continue work on an existing AI-DLC project, present this prompt:

```markdown
**Welcome back! I can see you have an existing AI-DLC project in progress.**

Based on your aidlc-state.md, here's your current status:
- **Project**: [project-name]
- **Current Phase**: [INCEPTION/CONSTRUCTION/OPERATIONS]
- **Current Stage**: [Stage Name]
- **Last Completed**: [Last completed step]
- **Next Step**: [Next step to work on]

**What would you like to work on today?**

A) Continue where you left off ([Next step description])

B) Review a previous stage ([Show available stages])

[Answer]: 
```

## MANDATORY: Session Continuity Instructions
1. **Always read aidlc-state.md first** when detecting existing project
2. **Skill gate on resume (MANDATORY)**: On resume, "start unit again", or advancing into a new stage via an approval gate, check `## Current Stage Skill` in `aidlc-docs/aidlc-state.md` and whether `aidlc-docs/{current-stage-name}-skill-selection.md` exists with a valid `[Answer]:`. If missing or `pending`, run `common/skill-discovery-gate.md` (Step 0) **before** loading stage artifacts or generating outputs — even if other stage artifacts already exist
3. **Parse current status** from the workflow file to populate the prompt
4. **MANDATORY: Load Previous Stage Artifacts** - Before resuming any stage, automatically read all relevant artifacts from previous stages:
   - **Reverse Engineering**: Read architecture.md, code-structure.md, api-documentation.md
   - **Requirements Analysis**: Read requirements.md, requirement-verification-questions.md
   - **Application Design**: Read application-design artifacts (components.md, component-methods.md, services.md, hld.md, lld/*.md, requirements/ears/*.md)
   - **Design (Units)**: Read unit-of-work.md, unit-of-work-dependency.md, unit-of-work-story-map.md, personas.md (if present)
   - **Per-Unit Design**: Per-unit artifacts live under `aidlc-docs/construction/{unit-name}/` in
     `functional-design/`, `nfr-requirements/`, `nfr-design/`, and `infrastructure-design/`
     subdirectories. On resume, determine the in-progress unit from `aidlc-state.md` and load that
     unit's design artifacts, plus the design artifacts of any units it depends on (per
     `unit-of-work-dependency.md`). The exact files in each subdirectory are enumerated by the
     corresponding construction stage rules.
   - **Code Stages**: Read all code files, plans, AND all previous artifacts
5. **Smart Context Loading by Stage**:
   - **Early Stages (Workspace Detection, Reverse Engineering)**: Load workspace analysis
   - **Requirements/Stories**: Load reverse engineering + requirements artifacts
   - **Design Stages**: Load requirements + stories + architecture + design artifacts
   - **Code Stages**: Load ALL artifacts + existing code files
6. **Adapt options** based on architectural choice and current phase
7. **Show specific next steps** rather than generic descriptions
8. **Log the continuity prompt** in audit.md with timestamp
9. **Context Summary**: After loading artifacts, provide brief summary of what was loaded for user awareness
10. **Asking questions**: ALWAYS ask clarification or user feedback questions by placing them in .md files. DO NOT place the multiple-choice questions in-line in the chat session.

## Error Handling
If artifacts are missing or corrupted during session resumption, see [error-handling.md](error-handling.md) for guidance on recovery procedures. 