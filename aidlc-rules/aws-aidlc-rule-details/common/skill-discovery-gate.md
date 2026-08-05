# Skill Discovery & Selection Gate

**MANDATORY**: Execute at **Step 0** of every Inception, Construction, and Operations stage — including on resume, "start unit again", or advancing via an approval gate (e.g. "Continue to Next Stage") into a new stage.

**Parent reference**: `ai-dlc-workflow.mdc` → "MANDATORY: Skill Discovery & Selection Gate"

## When to run

- Before Step 1 of the current stage rule file
- Before loading stage artifacts or generating stage outputs
- **Re-run** if `aidlc-docs/{stage-name}-skill-selection.md` is missing, has empty `[Answer]:` tags, or `## Current Stage Skill` in `aidlc-docs/aidlc-state.md` shows `pending` for the current stage
- **Workspace Detection exception**: if `aidlc-docs/aidlc-state.md` does not exist yet, create a minimal file with `## Current Stage Skill` when Step 0 completes (full template is written in workspace-detection Step 4)

## Discovery locations (merge and dedupe by folder path)

1. `skills/<phase>/` under the resolved rule-details directory — subfolders containing `SKILL.md` (`<phase>` = `inception`, `construction`, or `operations`)
2. `.cursor/skills/` under the workspace root — subfolders containing `SKILL.md` (project skills; flat layout)

## Execution

1. **Discover** skills from both locations above
2. **Create** `aidlc-docs/{stage-name}-skill-selection.md` per `common/question-format-guide.md`, scoped to current phase and stage:
   - **If skills found**: one option per skill (name + one-line description from `SKILL_CARD.md` or first line of `SKILL.md` + path), plus "Use standard AI-DLC rules only (no skill)", plus mandatory **Other** (custom skill path)
   - **If none found**: "No skill available for this — proceed with standard AI-DLC rules", plus mandatory **Other** (custom skill path)
3. **Set** `## Current Stage Skill` in `aidlc-docs/aidlc-state.md` to `pending` (see template in `inception/workspace-detection.md`)
4. **Inform** the user the question file is ready; **wait** for `[Answer]:` tags to be filled and user confirmation
5. **Resolve** the answer:
   - **Standard rules** → execute the stage rule file directly; produce contract artifacts per that file
   - **Skill selected** → execute `SKILL.md` for methodology (HOW), then **mandatory** `common/skill-artifact-adapter.md` to produce the **same** contract artifacts the stage rule defines (WHAT). Do **not** add skill/adapter logic to stage rule files
   - Invalid path → report and re-ask; do not guess
6. **Update** `aidlc-docs/aidlc-state.md` — set skill to `standard rules` or the resolved skill name/path
7. **Log** in `audit.md` before proceeding to Step 1:

```markdown
## [Stage Name] — Skill Selection
**Timestamp**: [ISO timestamp]
**User Input**: "[Complete raw answer from skill-selection file]"
**AI Response**: "[Resolved: standard rules | <skill-name> | <skill-path>]"
**Context**: Skill gate for [phase]/[stage-name]

---
```

## Skill vs stage rule responsibilities

| Concern | Skill path | Standard rules path |
|---------|------------|---------------------|
| Methodology (HOW) | Skill `SKILL.md` | Stage rule steps |
| Contract artifacts (WHAT) | `skill-artifact-adapter.md` → **same outputs** | Stage rule steps |
| Approval gates, audit, state | Stage rule file (unchanged) | Stage rule file (unchanged) |

**Example**: Any skill in any stage — adapter reads that stage's rule file for contract paths; no per-stage file edits required.

## Does not replace approval gates

Stage completion gates (e.g. "Request Changes" / "Continue to Next Stage") still run **after** contract artifacts are validated via the adapter (or after standard-rule execution).
