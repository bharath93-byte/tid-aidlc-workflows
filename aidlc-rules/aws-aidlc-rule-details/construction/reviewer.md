# Code Reviewer - Detailed Steps

## Overview

This stage reviews **only the current changes** for a unit after Code Generation. The change set is obtained by comparing the working tree and branch commits against `origin/main` (merge-base). The review is **strict** about SOLID principles and evaluates logic correctness, security, maintainability, performance, and reliability.

**Note**: Do not review the entire codebase. Limit analysis to the diff vs `origin/main`, plus minimal surrounding context only when required to verify a finding in the changed code.

## Prerequisites

- Code Generation must be complete for the unit
- Unit application code exists in the workspace root (never under `aidlc-docs/`)
- Git repository is available with a reachable `origin/main` branch

---



## Steps to Execute



## Step 1: Log Stage Start

- [ ] Log start of Code Reviewer in `aidlc-docs/audit.md` with ISO 8601 IST timestamp
- [ ] Record unit name and that the review base is `origin/main`



## Step 2: Collect Current Changes vs `origin/main`

- [ ] Resolve workspace root from `aidlc-docs/aidlc-state.md`
- [ ] Compute the merge-base with `origin/main` only (do not use local `main`):

```bash
git fetch origin main
BASE=$(git merge-base HEAD origin/main)
git diff --stat "$BASE"...HEAD
git diff "$BASE"...HEAD
git status --short
git diff
git diff --cached
```

- [ ] Review set = commits on the current branch since merge-base with `origin/main` **plus** uncommitted staged and unstaged changes
- [ ] If `origin/main` is missing or unreachable, stop and ask the user to fetch/configure the remote — do not fall back to local `main` or another branch
- [ ] If the combined diff is empty, report that there is nothing to review, log the result, and present the completion message with verdict **Approve**
- [ ] Scope review to changed files/hunks only



## Step 3: Load Review Context

- [ ] Read the unit code generation plan: `aidlc-docs/construction/plans/{unit-name}-code-generation-plan.md` (if present)
- [ ] Read unit stories / design artifacts needed to judge intent (only as needed for the diff)
- [ ] Read PR size budget and any approved exception from `aidlc-docs/inception/application-design/unit-of-work.md` when present
- [ ] **Brownfield only**: Use reverse-engineering artifacts for expected structure when assessing regressions in changed files



## Step 3b: Check PR Size Budget

- [ ] From the collected diff, count **production/application source** files and their additions+deletions
- [ ] **Exclude** from both file and line counts: unit tests, auto-generated lock files, migrations, and mocks
- [ ] Compare counted scope to unit budget: ≤ 10 files; target ≤ 200 / hard max 300 changed lines; review target `< 15 minutes`
- [ ] If counted files > 10 or counted lines > 300 **and** no approved exception is documented in `unit-of-work.md`, add a finding:
  - Severity: **Major** (treat as **Blocker** for merge recommendation if the overrun is severe or unexplained)
  - Dimension: Maintainability
  - Finding: `PR size over unit budget` — report counted files/lines vs limits and require split or documented exception
- [ ] If an approved exception exists, note it under Residual Risks (do not fail solely on size)



## Step 4: Review Logic Correctness

- [ ] Verify conditionals, edge cases, state transitions, and error/empty paths in the diff
- [ ] Flag broken invariants, incorrect algorithms, and race-prone updates introduced by the change
- [ ] Flag missing or too-weak tests for behavior changed in the diff



## Step 5: Review Security

- [ ] Check for injection, XSS, SSRF, path traversal, insecure deserialization
- [ ] Check AuthN/AuthZ gaps, privilege bypass, IDOR in changed paths
- [ ] Check secrets/credentials/PII leakage, weak crypto, unsafe defaults
- [ ] Check unvalidated input crossing trust boundaries



## Step 6: Review Maintainability and SOLID (Strict)

- [ ] Apply SOLID **strictly** to types/functions/modules touched by the diff — prefer flagging violations over missing them
- [ ] Evaluate each principle:


| Principle                 | Fail when                                                                                                     |
| ------------------------- | ------------------------------------------------------------------------------------------------------------- |
| **S**ingle Responsibility | A type/module gains unrelated reasons to change; mixed concerns in one unit                                   |
| **O**pen/Closed           | Extending behavior requires unsafe edits to stable core; missing seam where the change clearly needs one      |
| **L**iskov Substitution   | Overrides/implementations break expectations (stronger preconditions, weaker postconditions, surprise errors) |
| **I**nterface Segregation | Callers forced to depend on unused methods; fat interfaces introduced or widened without need                 |
| **D**ependency Inversion  | New/updated logic depends on concretions where an abstraction is required; infrastructure wired into domain   |


- [ ] For each SOLID finding: name the principle, explain the violation, cite `file:line`, and give a concrete refactor direction
- [ ] Flag duplication, hidden side effects, and layering breaks introduced by the change



## Step 7: Review Performance

- [ ] Flag hot-path waste in the diff: N+1 queries, unbounded allocations, accidental O(n²), sync work on critical paths
- [ ] Flag missing pagination/limits on new list/query APIs
- [ ] Flag unnecessary work in loops and blocking calls in async contexts



## Step 8: Review Reliability

- [ ] Flag missing/incorrect retries, timeouts, cancellation, or idempotency where the change needs them
- [ ] Flag partial-failure handling gaps, resource leaks, over-broad catch, swallowed errors
- [ ] Flag fragile external-service assumptions and insufficient failure logging



## Step 9: Assign Severity and Verdict

- [ ] Classify each finding:


| Severity    | Meaning                                                                       |
| ----------- | ----------------------------------------------------------------------------- |
| **Blocker** | Wrong, unsafe, or merge-risk; must fix before continuing                      |
| **Major**   | Clear defect or SOLID/design break with real cost; should fix before continue |
| **Minor**   | Real issue, limited blast radius; fix soon                                    |
| **Nit**     | Small clarity/consistency note; optional                                      |


- [ ] Security auth/injection/secret issues are at least **Major**; exploitability in the changed path → **Blocker**
- [ ] Set verdict:
  - **Request changes** if any **Blocker** or **Major** remains
  - **Approve with nits** if only **Minor**/**Nit** remain
  - **Approve** if no findings
- [ ] Do **not** fix findings in this stage unless the user selects **Fix the review comments** under **How to Proceed**



## Step 10: Write Review Report

- [ ] Save report as `aidlc-docs/construction/{unit-name}/code/code-review.md`
- [ ] Use this structure:

```markdown
# Code Review - [unit-name] (`origin/main`...HEAD [+ working tree])

## Summary
- One paragraph: change intent (inferred), risk level, merge readiness.

## Findings
| Severity | Dimension | Location | Finding |
| -------- | --------- | -------- | ------- |
| Blocker/Major/Minor/Nit | Logic/Security/Maintainability/Performance/Reliability/SOLID | `path:line` | Concise problem + why it matters |

## SOLID
- Bullet list of strict SOLID verdicts on the changed surface (pass/fail per principle touched). Unmentioned principles = not implicated by the diff.

## Residual Risks
- Gaps that cannot be verified from the diff alone.

## Verdict
- **Approve** | **Approve with nits** | **Request changes**

## How to Proceed
Select exactly one option by changing `[ ]` to `[x]`:

- [ ] Fix the review comments — proceed to Step 11 and continue generation/fixes, then re-run Code Reviewer
- [ ] Continue without fixing — accept residual risk and proceed toward completion
- [ ] Other — describe below

Other (if selected):
```

- [ ] Sort findings by severity (Blocker → Nit)
- [ ] Every finding must cite `file:line` (or hunk range) in the changed code
- [ ] Pre-existing issues outside the diff: omit, or mark **Pre-existing (out of scope)** only if the change worsens them
- [ ] Always include the **How to Proceed** checkbox section when the report has findings that may need fixes; omit it only when verdict is **Approve** with no findings



## Step 11: Collect Continuation (How to Proceed)

- [ ] If verdict is **Approve** with no findings (or only Nit and no **How to Proceed** section): set continuation outcome to **Approve (no findings)** and proceed to Step 14
- [ ] If findings remain that may need fixes: ensure **How to Proceed** checkboxes are present in `code-review.md` (do not create a separate question file)
- [ ] Before asking the user, log the prompt with timestamp in `aidlc-docs/audit.md` (path to `code-review.md`, verdict, severity counts)
- [ ] Inform the user to open `aidlc-docs/construction/{unit-name}/code/code-review.md`, mark **exactly one** checkbox under **How to Proceed**, and confirm when done
- [ ] Wait until the user confirms; then read `code-review.md` and validate exactly one `[x]` under **How to Proceed**
- [ ] If zero or multiple options are checked, or **Other** is checked with no description: ask the user to correct the file before continuing
- [ ] Map the selected checkbox to a continuation outcome for Code Generation:
  - **Fix the review comments** → continuation outcome `Fix the review comments` (Code Generation returns to Step 11, then re-runs Code Reviewer)
  - **Continue without fixing** → continuation outcome `Continue without fixing` (log residual-risk acceptance in `aidlc-docs/audit.md`)
  - **Other** → continuation outcome `Other` (follow the user's description; clarify in `code-review.md` if ambiguous)
- [ ] Log the user's selected option (complete raw checkbox state) with ISO 8601 IST timestamp in `aidlc-docs/audit.md`



## Step 12: Present Review Summary

- Present summary in this structure:
  1. **Completion Announcement** (mandatory): Always start with this:

```markdown
# 🔎 Code Review Complete - [unit-name]
```

  2. **AI Summary** (optional): Provide structured bullet-point summary
     - Verdict and counts by severity (Blocker/Major/Minor/Nit)
     - Highest-risk findings (brief)
     - Path to full report
     - Continuation outcome selected under **How to Proceed** (or **Approve (no findings)**)
     - Keep factual; do not invent extra workflow menus
  3. **Return control to Code Generation** with the continuation outcome from Step 11



## Step 13: Record Continuation Outcome

- [ ] Log continuation outcome with timestamp in `aidlc-docs/audit.md`
- [ ] Record the user's complete raw checkbox selection (or that no prompt was needed)
- [ ] Do not mark Code Generation complete here — Code Generation owns PR size check and flow branching after this stage



## Step 14: Hand Off to Code Generation

- [ ] Return one of: `Fix the review comments` | `Continue without fixing` | `Approve (no findings)` | `Other`
- [ ] Update `aidlc-docs/aidlc-state.md` current status to reflect Code Reviewer finished for this unit and the continuation outcome
- [ ] Application fixes (when outcome is Fix) are applied by Code Generation Step 11, not inside this stage

---



## Critical Rules



### Scope Rules

- **ONLY current changes**: Review the diff vs `origin/main` (merge-base) plus uncommitted changes
- **Base branch is** `origin/main` **only**: Never use local `main`; do not substitute another base without explicit user direction
- **No whole-repo review**: Do not expand into unchanged files except minimal context for a diff finding
- **No silent fixes**: Report first; change code only when the user selects **Fix the review comments**



### SOLID Rules

- Enforce SOLID **strictly** on the changed surface
- Every SOLID finding must name the principle and cite location
- Do not waive SOLID violations as style preferences



### Dimension Rules

- Always evaluate: Logic correctness, Security, Maintainability (incl. SOLID), Performance, Reliability, and PR size budget (Step 3b)
- Omit a dimension from the findings table only when it has no issues (do not invent filler)
- Severity must match impact; security exploitability in the changed path is **Blocker**
- Over-budget counted PR size without documented exception is at least **Major**



### Workflow Rules

- Collect continuation via **How to Proceed** checkboxes in `code-review.md` — never a separate question file, never chat-only options
- Validate exactly one checkbox is selected before returning an outcome
- Log all prompts and user responses in `audit.md` with complete raw input
- Review report lives under `aidlc-docs/`; application fixes stay in workspace root (applied by Code Generation when outcome is Fix)
- Return a clear continuation outcome for Code Generation flow branching



## Completion Criteria

- Diff vs `origin/main` collected (or empty-diff path handled)
- PR size budget checked (counted files/lines vs unit limits; exception noted when present)
- All review dimensions evaluated
- Strict SOLID review completed for changed surface
- `aidlc-docs/construction/{unit-name}/code/code-review.md` written
- Continuation outcome determined (**How to Proceed** or **Approve (no findings)**)
- Outcome and user selection recorded in `audit.md`
- Control handed back to Code Generation with the continuation outcome

