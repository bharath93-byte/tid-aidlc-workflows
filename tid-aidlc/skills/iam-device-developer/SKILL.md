---
name: iam-device-developer
description: Runs the device implementation workflow for a Jira story using TDD: (1) create branch—skip for now, (2) fetch Jira story, (3) TDD-oriented plan with user modifications and approval, (4) implement Red–Green–Refactor with approval after each, (5) agent review with approval, (6) linter, (7) run all device unit tests. Steps 8–10 (sub-task, commit, push) skipped for now. Use when the user runs /iam-device-developer, says "device developer workflow", "implement device story", or provides a Jira story ID with intent to implement device code.
---

# IAM Device Developer Workflow

Execute these steps in order. Do not skip steps. **User approval is required at Steps 3, 4, and 5** before proceeding to the next step.

---

## Step 1: Create a new branch (skip for now)

1. **Do not create a branch.** Work on the current branch. Confirm to the user: "Branch creation skipped for now."

---

## Step 2: Fetch Jira story

1. **Get the story ID** from the user (e.g. `IAM-5851`). If not provided, ask for it.

2. **Fetch story details** using the Jira MCP:
   - Call `mcp_jira_jira_getIssue` with `issueKey: "<STORY_ID>"`.
   - From the response, extract and show: **summary**, **description**, and **acceptance criteria** (e.g. from `fields.summary`, `fields.description`, and custom fields like `customfield_10802` or similar). Note the issue key for reference.

3. **Attachments:** Skip downloading or fetching any attachments (including "developer context"). Use only the story's summary, description, and acceptance criteria from the getIssue response for planning and implementation.

4. Confirm to the user that story details are loaded (attachment download skipped).

---

## Step 3: Plan the story (TDD-oriented, no code changes)

**Plan only.** Do not create, edit, or delete any files in this step. Output the plan as markdown. The user can interact to request modifications on top of the agent's plan; incorporate feedback and iterate until the user approves.

1. **Create a detailed TDD-oriented plan** using the story summary, description, and acceptance criteria:
   - **Test cases first (Red):** For each acceptance criterion, list the exact unit tests to add or change in `devices/tests/` (test names, what they assert, which file). These tests will be written first and must fail before any production code.
   - **Production code (Green):** Which files to change (e.g. `devices/src/`, API spec under `api-specification/`), what to add/update to make the new tests pass. No code until tests exist and fail.
   - **Refactor (optional):** Any obvious clean-up (extract helpers, rename) to do after tests pass, without changing behavior.
   - **Documentation:** Where to update docs or API specification (can be part of Green or Refactor).
   - **Integration tests** (optional): If applicable, what integration tests to add.
   - **Flow diagrams:** Include Mermaid diagrams for data/control flow where helpful.
   - **Order of implementation:** State explicitly—"(1) Write failing tests only; (2) Run tests, confirm they fail; (3) Implement production code until tests pass; (4) Optional refactor; re-run tests."
   - Search the codebase as needed. Produce a clear numbered list with file paths and brief actions.

2. **Present the plan and ask for user inputs:**
   - Show the plan (and diagrams) to the user.
   - Say: *"Review this TDD plan. You can request modifications on top of this plan—add, remove, or change items. When you're satisfied, reply with 'approved', 'finalized', or 'looks good' to proceed to Step 4 (Implement—Red)."*

3. **Incorporate feedback and finalize:**
   - If the user gives feedback, revise the plan and present again. Repeat until the user explicitly approves (e.g. "approved", "finalized", "looks good", "go ahead").
   - **Do not proceed to Step 4** until the user explicitly approves.

---

## Step 4: Implement using TDD (Red → Green → Refactor)

Follow the approved plan in strict TDD order. **Pause and ask for user approval after each of 4a, 4b, and 4c** before proceeding.

### Step 4a: Red — Write failing tests first

1. **Add or change only tests** in `devices/tests/` (and test helpers if needed) that encode the acceptance criteria from the plan. Do **not** write or change production code yet.
2. **Run the relevant tests** (e.g. `cd devices && poetry run pytest tests/... -v -k "<pattern>"`). Confirm that the new tests **fail** for the expected reason (missing or incorrect behavior).
3. **Present to the user:** Summarise what tests were added and that they fail as expected. Say: *"Red step complete: failing tests are in place. Reply with 'approved', 'go', or 'proceed' to continue to Step 4b (Green—implement production code)."*
4. **Do not proceed to Step 4b** until the user explicitly approves.

### Step 4b: Green — Implement production code to pass tests

1. **Implement only the production code** (and API spec/docs as per plan) needed to make the new tests pass. Do not add new tests in this step.
2. **Run the same tests** until they **all pass**. Fix any issues in production code (or fix tests only if they were wrong).
3. **Present to the user:** Confirm tests pass. Say: *"Green step complete: all tests pass. Reply with 'approved', 'go', or 'proceed' to continue to Step 4c (Refactor), or say 'skip refactor' to go to Step 5 (Agent review)."*
4. **Do not proceed to Step 4c or Step 5** until the user explicitly approves (or explicitly skips refactor).

### Step 4c: Refactor (optional)

1. **Only if the user approved refactor:** Improve code (naming, structure, remove duplication) without changing behavior. Do not add or remove tests unless correcting a mistake.
2. **Re-run the same tests** (and linter if desired) to ensure nothing broke.
3. **Present to the user:** Confirm refactor is done and tests still pass. Say: *"Refactor complete; tests still pass. Proceeding to Step 5 (Agent review)."*
4. If the user had said "skip refactor", go directly to Step 5 after Step 4b approval.

---

## Step 5: Agent review

1. **Review with standards:**
   - Apply the review checklist in `.cursor/rules/device-developer-review.mdc` and any other project rules in `.cursor/rules/`.
   - Check style, error handling, tests, and docs. Fix any issues found.

2. **Verify every acceptance criterion:**
   - List each acceptance criterion from the Jira story. For each, state how it is satisfied and confirm **Done** or **Not done**.
   - If any criterion is not satisfied, implement the missing part and repeat.

3. **Present to the user and ask for approval:**
   - Say: *"Review complete. Reply with 'approved', 'go', or 'proceed' to continue to Step 6 (Linter)."*
   - **Do not proceed to Step 6** until the user explicitly approves.

---

## Step 6: Run defined repo rules (linter)

1. **Run the devices linter** from the repository root:
   - `cd devices && poetry run ruff check --config ../ruff.toml ./src`
   - On Windows PowerShell use: `cd devices; poetry run ruff check --config ../ruff.toml ./src`
   - Fix any reported issues.

2. **Fix if any** and re-run until the command passes.

3. Say: *"Linter passed. Proceeding to Step 7 (run all device unit tests)."*

---

## Step 7: Run all device unit tests

1. **Run the full device test suite** from the repository root:
   - `cd devices && poetry run pytest tests/ -v`
   - On Windows PowerShell use: `cd devices; poetry run pytest tests/ -v`

2. **Confirm all tests pass.** If any fail, fix the issue (production code or test) and re-run until the full suite passes.

3. **Tell the user:** "All device unit tests passed. Proceeding to Step 8 (sub-task skipped)."

---

## Step 8: Create Jira sub-task (skip for now)

1. **Do not create a Jira sub-task.** Skip this step. Confirm to the user: "Sub-task creation skipped for now."

---

## Step 9: Commit (skip for now)

1. **Update docs first:** Before committing, run the `update-devices-docs` skill to verify `devices/docs/` is consistent with the changes made in this session. Fix any stale sections identified.

2. **Do not commit.** Skip this step. Confirm to the user: "Commit skipped for now. Stage and commit manually when ready (run `update-devices-docs` skill first)."

---

## Step 10: Push to origin (skip for now)

1. **Do not run** `git push`. Confirm to the user: "Push skipped for now."

---

## Summary checklist (for the agent)

- [ ] Step 1: Branch creation skipped (work on current branch).
- [ ] Step 2: Fetched story via Jira MCP; skipped attachment download.
- [ ] Step 3: Created TDD-oriented plan; user requested modifications; got user approval.
- [ ] Step 4a Red: Wrote failing tests only; ran tests and confirmed they fail; got user approval.
- [ ] Step 4b Green: Implemented production code; all tests pass; got user approval (or user skipped refactor).
- [ ] Step 4c Refactor: Optional refactor done; tests still pass (or skipped by user).
- [ ] Step 5: Ran agent review (device-developer-review + AC verification); got user approval.
- [ ] Step 6: Ran ruff in devices; fixed issues.
- [ ] Step 7: Ran all device unit tests; all passed.
- [ ] Step 8: Sub-task creation skipped.
- [ ] Step 9: Commit skipped.
- [ ] Step 10: Push skipped.

---

## Final summary (present to user)

At the end of the workflow, present a **tabulated checklist** to the user, for example:

| # | Step | Status |
|---|------|--------|
| 1 | Create a new branch | Skipped |
| 2 | Fetch Jira story | ✓ / — |
| 3 | Plan (TDD-oriented); user modifications; get user approval | ✓ / — |
| 4a | Red: Write failing tests; confirm fail; get user approval | ✓ / — |
| 4b | Green: Implement production code; tests pass; get user approval | ✓ / — |
| 4c | Refactor (optional); tests still pass | ✓ / — / Skipped |
| 5 | Agent review; get user approval | ✓ / — |
| 6 | Run ruff in devices | ✓ / — |
| 7 | Run all device unit tests | ✓ / — |
| 8 | Create Jira sub-task | Skipped |
| 9 | Commit | Skipped |
| 10 | Push to origin | Skipped |

Replace ✓ with the actual status for each step; use — if not done.

---

## Notes

- **User approval required at Steps 3, 4, and 5.** Do not proceed past Step 3, Step 4 (including 4a/4b/4c), or Step 5 without explicit user approval.
- **Skipped for now:** Step 1 (branch), Step 8 (sub-task), Step 9 (commit), Step 10 (push). Work on the current branch; do not create branch, sub-task, commit, or push.
- **TDD:** Workflow follows Red → Green → Refactor. User approval is required after each of 4a (Red), 4b (Green), and 4c (Refactor) before proceeding.
- **Acceptance criteria:** Look for `fields.customfield_*` arrays in the Jira response for checklist/AC.
- **Jira MCP:** Use `mcp_jira_jira_getIssue` with `issueKey` for the story. Sub-task creation is skipped for now.
- **Attachments:** Do not download or fetch story attachments; use only the story's summary, description, and acceptance criteria.
