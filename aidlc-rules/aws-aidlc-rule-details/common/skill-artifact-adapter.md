# Skill Artifact Adapter Standard

**Purpose**: Skills may use any internal methodology. AWS AI-DLC **stage rules** define the **artifact contract** — paths, structure, and gates downstream stages depend on. This adapter ensures **the same contract artifacts are produced whether the user selects a skill or standard rules** — without editing individual skills **or** individual stage rule files.

**When this applies**: Whenever Step 0 resolves to a skill (not "standard rules only"). Execute after the skill's work and **before** the stage presents completion.

**Parent reference**: `common/skill-discovery-gate.md` → resolve skill → **run this adapter**

---

## Scalability rule (critical)

| ✅ Do | ❌ Do not |
|-------|----------|
| Enforce output contract here in `common/skill-artifact-adapter.md` | Add skill-specific or adapter-specific text to `inception/*.md`, `construction/*.md`, or any stage rule file |
| Discover contract dynamically from the current stage rule file at runtime | Duplicate contract definitions inside skills |
| Produce identical `aidlc-docs/` outputs for skill **or** standard-rules paths | Let a skill finish a stage with only skill-native files |

**Outcome**: User picks `grill-with-docs`, `jira-work-breakdown`, or standard rules — downstream stages always find the same `aidlc-docs/` paths the stage rule already defines.

---

## Core principles

1. **Skill = HOW** — process, questioning style, tooling, intermediate thinking
2. **Stage rule = WHAT** — mandatory `aidlc-docs/` paths, section structure, approval gates (unchanged)
3. **Adapter = bridge** — after skill work, map output into the **same artifacts** standard-rule execution would produce
4. **Supplementary ≠ substitute** — skill-native files (ADRs, glossaries) go to `skill-workspace/` **in addition to** contract artifacts
5. **One contract, two paths**:

| Path | Execution | Final artifacts |
|------|-----------|-----------------|
| Standard rules | Follow stage rule file step-by-step | Per stage rule |
| Skill selected | Follow `SKILL.md` for methodology → **run this adapter** | **Same** as stage rule |

---

## Standard adapter flow (mandatory when a skill is selected)

| Phase | Action |
|-------|--------|
| **1. Discover contract** | Read the current stage rule file (`{phase}/{stage}.md`). Extract every mandatory `aidlc-docs/` output (`Create \`aidlc-docs/...`) and every ⛔ gate. **This is the contract** — not this adapter's table below. |
| **2. Execute skill** | Follow the selected skill's `SKILL.md`. Skill may replace **intermediate** steps only. |
| **3. Adapt** | Produce every contract artifact at the path and structure the stage rule specifies. Fill gaps; normalize format. |
| **4. Validate** | All contract paths exist; required sections present; stage gates satisfied (document equivalents in manifest if skill satisfied a gate differently). |
| **5. Record** | Write `aidlc-docs/{stage-name}-skill-adapter-manifest.md`. Log in `audit.md`. |
| **6. Continue** | Stage approval gates and `aidlc-state.md` updates per the **unchanged** stage rule file. |

---

## Dynamic contract discovery (preferred)

At runtime, parse the active stage rule file for:

- Lines matching ``Create `aidlc-docs/...` `` or ``- Create `aidlc-docs/...` ``
- **⛔ GATE** blocks and their prerequisites
- Final generation steps (often the last steps before state/approval)

The [Stage artifact contracts](#stage-artifact-contracts-reference) table below is a **reference index only**. When it differs from the stage rule file, **the stage rule file wins**.

---

## Adapter manifest

Create `aidlc-docs/{stage-name}-skill-adapter-manifest.md` when a skill is used:

```markdown
# Skill Adapter Manifest — [Stage Name]

- **Skill**: [name] ([path to SKILL.md])
- **Stage rule**: [{phase}/{stage}.md]
- **Contract steps discovered**: [e.g. Step 7 — from stage rule file]

## Mapping

| Contract artifact (required) | Source | Notes |
|-------------------------------|--------|-------|
| `aidlc-docs/...` | skill output / adapted / generated | |

## Validation

- [ ] All mandatory contract artifacts exist at correct paths
- [ ] Required sections present per stage rule
- [ ] Stage gates satisfied (or equivalent documented)
- [ ] Supplementary skill files linked from contract artifacts where relevant

## Supplementary skill outputs

| Path | Purpose |
|------|---------|
| `aidlc-docs/{phase}/skill-workspace/{skill-name}/...` | [e.g. ADRs, glossary] |
```

---

## Supplementary skill workspace

```text
aidlc-docs/{phase}/skill-workspace/{skill-name}/
```

Skill-native outputs that are **not** in the stage contract. Contract files must **reference** these when they contain supporting detail.

---

## Stage artifact contracts (reference index)

Illustrative only — discover the live contract from the stage rule file.

| Stage | Rule file | Typical contract outputs |
|-------|-----------|--------------------------|
| Workspace Detection | `inception/workspace-detection.md` | `aidlc-docs/aidlc-state.md` |
| Reverse Engineering | `inception/reverse-engineering.md` | `aidlc-docs/inception/reverse-engineering/*.md` (8 artifacts) |
| Requirements Analysis | `inception/requirements-analysis.md` | `requirement-verification-questions.md`, `requirements.md` |
| User Stories | `inception/user-stories.md` | `stories.md`, `personas.md` |
| Workflow Planning | `inception/workflow-planning.md` | `execution-plan.md` |
| Application Design | `inception/application-design.md` | `components.md`, `component-methods.md`, `services.md`, etc. |
| Units Generation | `inception/units-generation.md` | `unit-of-work.md`, `unit-of-work-dependency.md`, `unit-of-work-story-map.md` |
| Functional Design | `construction/functional-design.md` | `business-logic-model.md`, `business-rules.md`, `domain-entities.md` |
| NFR Requirements | `construction/nfr-requirements.md` | `nfr-requirements.md`, `tech-stack-decisions.md` |
| NFR Design | `construction/nfr-design.md` | `nfr-design-patterns.md`, `logical-components.md` |
| Infrastructure Design | `construction/infrastructure-design.md` | `infrastructure-design.md`, `deployment-architecture.md` |
| Code Generation | `construction/code-generation.md` | plan + workspace code + `aidlc-docs/construction/{unit}/code/` |
| Build and Test | `construction/build-and-test.md` | `build-and-test/*.md` instruction set |

---

## Worked example (illustrative — contract read from stage rule, not hardcoded here)

**Stage**: Requirements Analysis · **Skill**: `grill-with-docs`

1. **Discover contract** from `inception/requirements-analysis.md` → finds Step 7: `aidlc-docs/inception/requirements/requirements.md` with intent summary, functional/NFR requirements, incorporated answers, key summary
2. **Execute skill** → interview produces ADRs/glossary in skill-native form
3. **Adapt** → write `requirements.md` matching Step 7 structure; map interview Q&A to `requirement-verification-questions.md` or document gate equivalence in manifest
4. **Supplementary** → ADRs/glossary under `aidlc-docs/inception/skill-workspace/grill-with-docs/`
5. **Invalid** → stage complete with only ADRs and no `requirements.md`

---

## Validation rules (blocking)

Do **not** present stage completion or mark the stage complete in `aidlc-state.md` until:

1. Every contract artifact from the **stage rule file** exists at the specified path
2. Required sections are present per that step
3. Stage gates are satisfied
4. `{stage-name}-skill-adapter-manifest.md` is written (skill path only)
5. Adaptation logged in `audit.md`

---

## Standard rules only (no skill)

Execute the stage rule file directly. Same contract artifacts. No adapter manifest required.
