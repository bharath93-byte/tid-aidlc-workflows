---
name: update-devices-docs
description: >-
  Audits and updates the three API/pipeline docs in devices/docs/ to keep them
  in sync with the current source code. Use before every git commit or push that
  touches devices/src/, or when the user asks to sync, refresh, or update the
  device docs.
---

# Update devices/docs

## Docs in scope

| File | Covers |
|---|---|
| `devices/docs/QUERY_BUILDING.md` | Filter pipeline call sequence, normalise/parse/scenario steps, scenario rewrites, field-name translation |
| `devices/docs/LIST_DEVICES_API.md` | Public query parameters, filtering operators, `accounts.status` rules, `include=full` constraints, response shape, error codes |
| `devices/docs/FIELD_OPERATOR_MATRIX.md` | Per-field operator support table, sortBy fields, multi-occurrence fields, backend routing |

---

## Step 1 — Find what changed

Run the diff against the base branch to list changed `devices/src/` files:

```powershell
git diff --name-only HEAD~1 HEAD -- devices/src/
```

If staged but uncommitted:

```powershell
git diff --name-only --cached -- devices/src/
```

---

## Step 2 — Apply the code → doc mapping

For each changed source file, check the corresponding doc section:

| Changed file | What to check |
|---|---|
| `device_service.py` | `QUERY_BUILDING.md` — call sequence, scenario rewrites (EMPTY / NO_STATUS / STATUS_PRESENT / TRANSFERRED_FULL), "What is/isn't rewritten" table, key source files table |
| `device_service.py` routing (`sort_params` default) | `QUERY_BUILDING.md` Step 4 · `FIELD_OPERATOR_MATRIX.md` backend routing section |
| `validators/rsql_helpers.py` | `QUERY_BUILDING.md` Steps 2a and 2b |
| `validators/field_operator_validators.py` | `FIELD_OPERATOR_MATRIX.md` filterable fields table and non-filterable list |
| `validators/business_rule_validators.py` | `LIST_DEVICES_API.md` `include=full` constraints table |
| `constants.py` (`FILTER_FIELDS`, `FilterScenario`) | `QUERY_BUILDING.md` scenario table · `FIELD_OPERATOR_MATRIX.md` |
| `app.py` / route definitions | `LIST_DEVICES_API.md` endpoints section and query parameters table |

---

## Step 3 — Audit each affected doc

For each doc flagged in Step 2, read it and check:

1. **Method / function names** — remove any that were deleted; add any that were introduced.
2. **Code examples** — run through the actual logic and confirm the `input → output` examples are still correct.
3. **Routing notes** — confirm whether AOSS / DDB routing statements match the current defaults in `device_service.py`.
4. **Tables** — operators, fields, `include=full` constraints, sortBy values — match against `constants.py` and `FIELD_REGISTRY`.
5. **Scenario rewrites** — re-read `__build_device_filter_query` and verify every scenario block in `QUERY_BUILDING.md` reflects current code.

---

## Step 4 — Update and verify

Edit only the sections that are stale. After editing:

- Re-read the doc to confirm no contradictions remain.
- Ensure cross-references between docs are consistent (e.g. `FIELD_OPERATOR_MATRIX.md` links to `LIST_DEVICES_API.md`).

---

## Step 5 — Confirm to the user

Report:
- Which docs were changed and what was updated.
- Which docs were checked and found already accurate (no change needed).
