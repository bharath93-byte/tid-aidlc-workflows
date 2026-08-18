---
name: iam-device-tester
description: Runs the device test workflow for a Jira story: fetch story, create branch (skip for now), plan automation test cases (approval + modifications), implement automation tests in tests/automation (approval + modifications), create sub-task / commit / push (all skip for now). Use when the user runs /iam-device-tester, says "device tester workflow", "write device tests for story", or provides a Jira story ID with intent to write or update automation tests for device functionality.
---

# IAM Device Tester Workflow

Execute these steps in order. Do not skip steps. Pause for user approval at **Steps 3, 4, 5, 6, and 7**. The user may give modifications at **Steps 3 and 4** before approving.

---

## Step 1: Fetch Jira story

1. **Get the story ID** from the user (e.g. `IAM-5851`). If not provided, ask for it.

2. **Fetch story details** using the Jira MCP:
   - Call `mcp_jira_jira_getIssue` with `issueKey: "<STORY_ID>"`.
   - From the response, extract and show: **summary**, **description**, and **acceptance criteria**. Note the issue key for later steps.
   - Skip attachments; use only the fields above (e.g. acceptance criteria from customfield if your Jira exposes it).

3. Confirm to the user that the story is loaded and you are ready for Step 2.

---

## Step 2: Create branch (skip for now)

1. **Skip branch creation** for this run. Tell the user: "Branch creation skipped. When you want to create the test branch, run: `git fetch origin dev/<STORY_KEY>-c`, then `git checkout -b test/<STORY_KEY>-c origin/dev/<STORY_KEY>-c` (create from `dev/<STORY_KEY>-c`)."

2. Proceed to Step 3.

---

## Step 3: Plan for automation test cases (no code changes yet)

1. **Create a detailed plan for writing or updating automation test cases** using the story summary, description, and acceptance criteria:
   - Which test files to add or modify under **`tests/automation`** (do not touch `devices/`).
   - What scenarios to cover: happy path, edge cases, error cases, fixtures/mocks.
   - Map each acceptance criterion to specific automation test cases where possible.
   - Search the codebase for existing test patterns in **`tests/automation`** and follow them.

2. **Present the plan** to the user. Invite modifications: *"Review this test plan. Add your inputs or constraints if any. When you're satisfied, reply with 'approved', 'finalized', or 'looks good' to proceed to implementing tests."*

3. **Incorporate feedback:** Revise the plan based on the user's modifications. Do not proceed to Step 4 until the user explicitly approves.

---

## Step 4: Implement the test changes

1. **Apply the approved plan**: write or update **automation test cases** in **`tests/automation`** only. Do not touch the **`devices/`** folder. Follow existing patterns and naming. All test changes must live under `tests/automation`.

2. **Present a short summary** of what was implemented (files changed, scenarios added). Invite modifications: *"Review the test implementation. Request any changes; when satisfied, reply with 'approved', 'finalized', or 'looks good' to proceed."*

3. **Incorporate feedback:** Make any requested changes. Do not proceed to Step 5 until the user explicitly approves.

---

## Step 5: Create Jira sub-task (skip for now)

1. **Skip creating the Jira sub-task** for this run. Tell the user: "Sub-task creation skipped. When you want to create it, use Jira MCP to create a sub-task under the story with the test plan to-dos (summary e.g. 'Test tasks: <short story summary>', description = plan from Step 3 in Wiki Markup, parent = story key)."

2. **Pause for approval:** Ask the user to confirm before proceeding to Step 6 (e.g. "Proceed to Step 6 (commit skipped)?").

---

## Step 6: Commit changes (skip for now)

1. **Skip commit** for this run. Tell the user: "Commit skipped. When ready, stage only the test files and commit with message format: `[<SUB_TASK_KEY>] - \"<message>\"` (use sub-task key from Step 5 when you run it)."

2. **Pause for approval:** Ask the user to confirm before proceeding to Step 7 (e.g. "Proceed to Step 7 (push skipped)?").

---

## Step 7: Push changes (skip for now)

1. **Skip push** for this run. Tell the user: "Push skipped. When ready, run: `git push -u origin test/<STORY_KEY>-c`."

2. **Pause for approval:** Confirm with the user that the workflow is complete.

---

## Summary checklist (for the agent)

- [ ] Step 1: Fetched story via Jira MCP; showed summary, description, acceptance criteria.
- [ ] Step 2: Branch creation skipped.
- [ ] Step 3: Created plan for automation test cases; incorporated user modifications; got user approval.
- [ ] Step 4: Implemented/updated automation test cases in `tests/automation`; incorporated user modifications; got user approval.
- [ ] Step 5: Sub-task creation skipped; user confirmed to proceed.
- [ ] Step 6: Commit skipped; user confirmed to proceed.
- [ ] Step 7: Push skipped; user confirmed workflow complete.

---

## Final summary (present to user)

At the end of the workflow, present a **tabulated checklist** to the user, for example:

| # | Step | Status |
|---|------|--------|
| 1 | Fetch Jira story | ✓ / — |
| 2 | Create branch `test/<STORY_KEY>-c` | Skipped |
| 3 | Plan automation test cases; user modifications + approval | ✓ / — |
| 4 | Implement automation tests in `tests/automation`; user modifications + approval | ✓ / — |
| 5 | Create Jira sub-task with test plan to-dos | Skipped |
| 6 | Commit changes | Skipped |
| 7 | Push to origin | Skipped |

Replace ✓ with the actual status for steps 1, 3, 4; use — if not done.

---

## Notes

- **Approval:** Pause for user approval at **Steps 3, 4, 5, 6, and 7**. User may give **modifications at Steps 3 and 4**; incorporate feedback and do not proceed until they approve.
- **Branch (when not skipped):** Create from `dev/<STORY_KEY>-c`; branch name `test/<STORY_KEY>-c` (e.g. `test/IAM-5851-c`).
- **Commit format (when not skipped):** `[<SUB_TASK_KEY>] - "<commit message>"` where SUB_TASK_KEY is the Jira key of the sub-task created in Step 5 (e.g. `[IAM-5891] - "test: add tests for dealer list devices sortBy"`).
- **Jira MCP:** Use `mcp_jira_jira_getIssue` with `issueKey`; use `mcp_jira_jira_createIssue` for the sub-task when Step 5 is not skipped.
- **Scope:** This workflow is for **automation test code only**: add or update automation test cases in **`tests/automation`** only. Do not implement production code changes. Do not touch the **`devices/`** folder.
