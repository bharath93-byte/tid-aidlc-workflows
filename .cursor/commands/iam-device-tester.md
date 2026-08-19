# iam-device-tester workflow

Run the **iam-device-tester** workflow for the Jira story ID provided by the user.

1. Read and follow the workflow in `.cursor/skills/iam-device-tester/SKILL.md`.
2. The user will provide the story ID in this chat (e.g. IAM-5851). If not provided, ask for it.
3. Execute all steps in order:
   - **Step 1:** Fetch Jira story.
   - **Step 2:** Create branch — skip for now.
   - **Step 3:** Plan automation test cases — pause for user modifications and approval before Step 4.
   - **Step 4:** Implement test changes in `tests/automation` — pause for user modifications and approval before Step 5.
   - **Step 5:** Create sub-task — skip for now; pause for user approval before Step 6.
   - **Step 6:** Commit — skip for now; pause for user approval before Step 7.
   - **Step 7:** Push — skip for now; pause for user approval to close workflow.
4. Do not skip the approval gates at steps 3, 4, 5, 6, and 7. At steps 3 and 4, incorporate user modifications before proceeding.
5. Work only in **`tests/automation`**; do not touch the **`devices/`** folder.
6. Present the **final tabulated summary checklist** from the skill at the end.
