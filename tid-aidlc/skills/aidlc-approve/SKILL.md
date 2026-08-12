---
name: aidlc-approve
description: AIDLC approval-gate skill. Provides the shared "approval gate" mechanic needed at every stage of the AIDLC pipeline (inception/vision, ADR, TDD, delivery planning, Jira breakdown, implementation sign-off). Recognizes the trigger phrases "approved", "looks good", "finalized" (case-insensitive), captures the approver's identity, and appends a structured row to aidlc-docs/<epic-key-or-context-name>/audit.md, creating the file with the canonical header if it does not exist. Modeled on aidlc-vision's Gate 1 / Gate 2 pattern. Use whenever a draft, scorecard, or decision needs sign-off before persisting, or when the user says "approve this", "log this approval", or "/aidlc-approve".
disable-model-invocation: true
---

# AIDLC Approve

Self-contained, reusable "gate" mechanic. Any AIDLC skill (`aidlc-vision`,
`aidlc-adr`, and future planning/implementation skills) applies the steps
below at each of its approval gates instead of reimplementing gate logic
and audit logging independently.

---

## When to apply this skill

Apply at any point a workflow would otherwise say "do not proceed until the
user approves" — a completeness scorecard, a generated draft document, a
decision scorecard, a delivery/implementation plan, or any other
persist-worthy artifact.

---

## Step 1: Resolve the audit directory

Every approval is tagged to exactly one directory, identified by:
- **Epic key** (e.g. `IAM-123`), when the work originated from Jira, or
- **Context / story name** (e.g. `rate-limiting-user-userid`), for manual or direct work

Resolution order:

1. Use the `EPIC_KEY` / `FEATURE_SLUG` already established earlier in the
   conversation (set by `aidlc-vision`, `aidlc-context-loader`,
   `aidlc-vision-doc`, `aidlc-adr`, or an equivalent upstream skill).
2. Otherwise, look for an existing `aidlc-docs/<name>/` directory matching
   the current work. If exactly one plausible match exists, confirm it. If
   several, list them and ask which.
3. If none found or still ambiguous, ask:
   > "What epic key or context/story name should this approval be tagged under? (this determines `aidlc-docs/<name>/audit.md`)"

Set `AUDIT_DIR = aidlc-docs/<name>/` and `AUDIT_PATH = aidlc-docs/<name>/audit.md`.

---

## Step 2: Detect the approval trigger

Recognize, case-insensitive: "approved", "looks good", "finalized", or an
equivalent unambiguous affirmative tied to the specific gate under
discussion (e.g. "yes, ship it", "go ahead with this").

Do not log an approval for a vague acknowledgement ("ok", "cool", "sure")
that does not clearly close out the gate — ask for explicit confirmation
instead of guessing.

If the user requests changes instead of approving: log nothing. Revise the
draft and re-present the same gate.

---

## Step 3: Capture the approver

If the approver's identity is not already known for this session:

> "Who is approving this? (name or handle — used in the audit log)"

Reuse a previously captured approver name for the rest of the session
unless the user gives a different one.

---

## Step 4: Determine phase and details

Derive three values from the calling context:

- `PHASE`: the AIDLC phase this gate belongs to — `inception` (vision),
  `adr` (architecture decision records), `design` (TDD/HLD/LLD/EARS),
  `planning` (delivery plan / Jira breakdown),
  `implementation`, or another phase name the calling skill defines. Do not
  invent a phase; ask the calling workflow or the user if ambiguous.
- `SKILL_OR_EVENT`: the skill or step generating this approval (e.g.
  `aidlc-vision / Gate 1`, `aidlc-adr / Gate 2`, `manual review`).
- `DETAILS`: a specific, one-line summary of what was approved — never a
  generic "approved the document". State actual scope, for example
  "Completeness scorecard approved — all 6 categories Present" or "ADR-006
  through ADR-010 decision scorecard approved".

---

## Step 5: Write the audit entry

Row format (matches the existing `aidlc-audit-stamp` hook and the
`aidlc-docs/*/audit.md` files already in this repo):

```
| <UTC timestamp, YYYY-MM-DDTHH:MMZ> | <PHASE> | <SKILL_OR_EVENT> | <DETAILS> | <approver> |
```

If `AUDIT_PATH` does not exist, create it using the template at
[templates/audit-template.md](templates/audit-template.md), substituting
`<name>` and filling the first row.

If it exists, append the row to the existing table. Do not duplicate the
header.

**Reconcile pending stubs:** the `aidlc-audit-stamp` hook auto-creates a row
with `Approver: pending` whenever `vision.md` is written. If the most
recent `pending` row clearly refers to the action now being approved (same
document, same phase), replace `pending` with the captured approver in
place, instead of appending a duplicate row.

---

## Step 6: Confirm

Say: "Approval logged to `<AUDIT_PATH>`."

Return control to the calling workflow so it can proceed past its gate.

---

## Notes

- This skill only writes to `audit.md`. It does not decide what gets
  approved or write the approved artifact itself (`vision.md`, ADR
  document, delivery plan, etc.) — that remains the calling skill's
  responsibility, exactly as `aidlc-vision` Step 6/7 and `aidlc-adr` Step
  6/7 write their own output after their gate closes.
- **Reference:** trigger phrases, the "do not proceed until explicitly
  approved" rule, and the audit table schema are taken directly from
  `aidlc-vision`'s Gate 1 / Gate 2 pattern and from
  `.cursor/hooks/aidlc-audit-stamp.sh`, which already writes rows in this
  exact shape for `vision.md`.
- Works across every AIDLC phase, not only inception — the `PHASE` column
  is what distinguishes inception/design/planning/implementation gates
  within the same audit trail, in the same directory.
- One `audit.md` per epic/context directory. Do not create a second audit
  file for the same `aidlc-docs/<name>/` directory under a different name.
