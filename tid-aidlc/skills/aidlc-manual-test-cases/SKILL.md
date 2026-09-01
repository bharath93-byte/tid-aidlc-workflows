---
name: aidlc-manual-test-cases
description: >-
  Generates ticket-specific manual (not unit) test cases from the current
  AI-DLC epic's vision, HLD, LLD, EARS, and optional demo-gaps. Chains
  state-loader when EPIC_DIR / pipeline state is not already in session
  context (same as aidlc-init / aidlc-vision). Writes JSON keyed
  by ticket and a formatted Excel workbook (Summary + bar chart + All Cases +
  one sheet per story; single story = one sheet). Use when the user says
  "aidlc-manual-test-cases", "create ticket test cases", "manual test cases
  from ears", or wants a QA spreadsheet / Jira-ready cases with verification
  steps and live verification surfaces.
disable-model-invocation: true
---

# aidlc-manual-test-cases

Build **manual** test cases (not unit tests) for stories in the **current epic**.
Each case is executable against a deployed or deployable env: exercise the
feature, then **verify on the live surfaces the design names** (API, DDB, logs,
metrics, flags, IaC — whatever *this* epic uses).

**Announce at start:** "Running **aidlc-manual-test-cases** for `{epic}`. Manual
cases only — live surfaces, not pytest."

Do **not** create Jira issues. Write JSON, then Excel. Jira MCP is a follow-up.

This skill is **epic-agnostic**. Do not hard-code routes, tables, metrics, or
phase names from a previous epic. Derive them from *this* epic's docs.

---

## Step 0 — Chain state-loader if epic state is not in context

Same contract as `aidlc-init` / `aidlc-vision-doc`: this skill does **not**
resolve `EPIC_DIR` itself. **state-loader** does.

**Already known?** If this session already has all of:

- `EPIC_DIR`
- `epic-id` / `epic-name`
- `status` (and `stories` if `state.json` was loaded)

…then **skip** state-loader. Reuse those values. Do not re-ask. Do not open a
second folder.

**Not known?** **Chain** the state-loader skill now — stop this skill's later
steps until it finishes:

1. Read and **execute** [`.cursor/skills/state-loader/SKILL.md`](../state-loader/SKILL.md)
   end-to-end (pipeline-config → identify epic → load `state.json` → print the
   banner). That skill asks the user **once** only if context and topic both
   fail.
2. After the banner, state-loader hands off. Take `EPIC_DIR`, `epic-id`,
   `epic-name`, `status`, and `stories` from that run.
3. If the user answered an epic name/key during state-loader, do **not**
   re-prompt. Continue here.

Canonical `EPIC_DIR` is `aidlc-docs/<epic-name>_<epic-id>/` (state-loader
`governance.epic_dir_patterns`). Never invent a parallel `aidlc-docs/<name>/`.

**Then** (only after `EPIC_DIR` is set) check docs exist:

- Need `{EPIC_DIR}/vision.md` and at least one `*-EARS.md` (or EARS section).
- If `status` is `not-started` / `context-ready`, or there are no EARS, **stop**:
  finish design (`aidlc-init` / `aidlc-design-driven-dev`) first.
- Lightweight (EARS-only) epics: HLD/LLD may be missing — use EARS + vision + ADR.

Print: `[manual-tc] epic={epic-name} ({epic-id}); EPIC_DIR={path}; status={status}`

---

## Step 1 — Resolve the ticket set

From `EPIC_DIR/state.json` `stories` plus optional extras. **Do not invent Jira keys.**

Priority for each story's JSON key:

1. User-named tickets this turn (if they scoped to a subset, generate **only** those)
2. `jira_key` / `issue_key` on the story object, if present
3. Live Jira (`jira_get-issue` / search) when MCP is authorized and the story
   summary matches
4. `designs/**/jira-stories.json` local id mapped to a real key if one exists
5. Else keep the `T*` (or stories-map) id and list it in `_meta.unmapped_stories`

Optional demo-gaps (skip silently if absent):

- `.cursor/skills/aidlc-demo/{TICKET}/demo-gaps/demo-gaps.md`
- `{EPIC_DIR}/demo-gaps/{TICKET}.md` or `{EPIC_DIR}/sessions/demo-gaps.md`

Print: `[manual-tc] tickets={keys}; sources=vision/hld/lld/ears[+demo-gaps]`

---

## Step 2 — Read sources (mandatory, quiet)

Read **this epic's** docs. Do not quiz the user.

| Source | Path |
|--------|------|
| Vision | `{EPIC_DIR}/vision.md` |
| ADR | `{EPIC_DIR}/adr.md` if present |
| HLD | `{EPIC_DIR}/high-level-design.md` if present |
| LLD | every `{EPIC_DIR}/designs/**/LLD.md` |
| EARS | every `{EPIC_DIR}/designs/**/*-EARS.md` |
| Stories | `state.json` `ears_ref` / `lld_ref` / title |
| Demo gaps | paths from Step 1, if they exist |
| Story text | `designs/**/jira-stories.json` and/or Jira MCP when authorized |

Map each ticket to its feature via `ears_ref` / `lld_ref` (folder name under
`designs/`). If a story has no EARS section, still write cases from LLD + vision
and note the gap in `_meta`.

---

## Step 3 — What to cover (manual only)

**Not unit tests.** Primary action is exercise the real entry point from *this*
design (route, job, CLI, event), then inspect a live surface. Never default to
`GET /users/{userId}` or any other leftover route.

For **every** EARS bullet on that story, and **every** distinct demo-gap if
present, write at least one case. Also cover integration surfaces the docs name
even when EARS is silent.

### Verification surfaces (derive, then name)

Build the surface list **from this epic** (vision Integrations, HLD/LLD
dependencies, EARS). Prefer these **generic kinds** — fill in the concrete
name from the docs (table, namespace, flag key):

| Kind | Use when the design mentions… |
|------|-------------------------------|
| `API` | HTTP / handler / route |
| `DynamoDB:<table>` | A DynamoDB table or item shape |
| `Config` | ConfigManager / central config keys |
| `FeatureFlag` | FeatureFlagManager / a named flag |
| `EMF/CloudWatch` | EMF / CloudWatch metrics |
| `CloudWatch Alarms` | Alarms / pages |
| `Datadog` | Datadog metrics or log monitors |
| `Logs` | Structured logger / log event names |
| `Lambda env` | Env vars the feature reads |
| `Middleware` | Middleware order / bypass |
| `HTTP response` | Status, body, headers |
| `Terraform/IaC` | Table, alarms, seeds, monitors |
| `Cross-service` | Other BLUs / callers |

Add a new kind if the epic needs it (S3, SQS, RDS, …). Do **not** copy another
epic's table/metric/flag names.

### Case families (per ticket)

1. **Happy path** — one case per EARS AC unless two ACs are one action
2. **Negative / malformed** — missing keys, wrong types, bad payloads
3. **Observability** — metrics, logs, alarms the design requires
4. **Data plane** — store/item shape, TTL, writes the LLD specifies
5. **Failure / fail-open or fail-closed** — as **this** ADR/LLD states
6. **Demo-gap** — one case per unique gap file bullet (if any)
7. **Config / rollout** — cache TTL, mixed fleet, kill-switch — **only if**
   the design has them
8. **Invariants** — non-goals and success criteria from vision (e.g. "never
   429 in shadow") **only if** this epic states them

Skip pytest-only wording as the primary action. Dormant artifacts (wired but
not triggered): "inspect deployed artifact / trigger only if that mode is on."

---

## Step 4 — Write the JSON

`{EPIC_DIR}/manual-test-cases.json` (overwrite). Ticket key → object with
`test_cases` (not a bare list).

```json
{
  "_meta": {
    "epic": "<epic-name>",
    "epic_id": "<epic-id>",
    "generated_at": "ISO-8601 UTC",
    "type": "manual",
    "sources": ["vision", "hld", "lld", "ears"],
    "unmapped_stories": []
  },
  "<TICKET>": {
    "ticket": "<TICKET>",
    "title": "short story title",
    "feature": "<designs/ folder or story slug>",
    "ears_file": "designs/<feature>/<feature>-EARS.md",
    "lld_file": "designs/<feature>/LLD.md",
    "demo_gaps_file": null,
    "test_cases": [
      {
        "id": "<TICKET>-TC-001",
        "summary": "Jira-ready one-line title",
        "description": "Why this case exists (EARS + optional gap + surface).",
        "priority": "High",
        "type": "Functional",
        "preconditions": ["env and data this case needs"],
        "steps": [
          {
            "step": 1,
            "action": "What the tester does",
            "expected_result": "What they must see, including where"
          }
        ],
        "verification_surfaces": ["API", "Logs"],
        "ears_refs": ["<EARS-ID>"],
        "demo_gap_refs": [],
        "labels": ["manual", "<epic-name or feature>"]
      }
    ]
  }
}
```

| Field | Rule |
|-------|------|
| `id` | `{TICKET}-TC-{NNN}` zero-padded, unique, stable |
| `summary` | ≤120 chars, verb-first (`Verify…`, `Validate…`) |
| `priority` | `High` / `Medium` / `Low` |
| `type` | `Functional` / `Negative` / `Observability` / `Resilience` / `Config` / `Integration` / `Regression` / `DemoGap` |
| `steps` | ≥2; last step is a **surface check**, not "function returned X" |
| `verification_surfaces` | from Step 3, **this** epic |
| `ears_refs` | EARS ids this case proves |
| `demo_gap_refs` | kebab-case slugs, or `[]` |
| `labels` | always `manual`; plus epic-name or feature — **not** a hardcoded product tag |

Jira-later: `summary` → issue summary; `steps[].action` / `expected_result` →
test steps; `ticket` → parent. Do not call `jira_create-issue`.

---

## Step 5 — Quality bar

1. Every EARS checkbox for that story has ≥1 case citing it.
2. Every demo-gap bullet (if files exist) has ≥1 tagged case.
3. JSON parses (`python -m json.tool`).
4. No leftover names from another epic (wrong route, table, metric, flag).
5. Last step of each case names **where** to look (surface + what good looks like).

Print: ticket → case count → EARS covered / demo-gaps covered.

---

## Step 6 — Excel workbook (mandatory)

Always run (do not hand-build the xlsx):

```bash
python3 .cursor/skills/aidlc-manual-test-cases/scripts/json_to_xlsx.py \
  {EPIC_DIR}/manual-test-cases.json \
  {EPIC_DIR}/manual-test-cases.xlsx
```

If `openpyxl` is missing, `pip install --target` a throwaway dir and set
`PYTHONPATH`. Do not add it to the repo.

| Tickets in JSON | Workbook |
|-----------------|----------|
| **1** | **One sheet** named after the ticket |
| **2+** | **Summary** (KPIs, count table, **bar chart**) + **All Cases** + **one sheet per ticket** |

Columns: Ticket, Story, Test Case ID, Summary, Description, Type, Priority,
Status, Preconditions, Test Steps, Expected Results, Verification Surfaces,
EARS Refs, Demo Gaps, Labels, Tester, Notes / Actual Result.

Status default `Not Started`; dropdown: Not Started, In Progress, Pass, Fail,
Blocked, Skipped.

Excel-only request + JSON already exists → skip Steps 2–5, run this step.

Print: `[manual-tc] xlsx={path}; mode={single-sheet|summary+all+N-tabs}; tickets={keys}`

---

## Step 7 — Approval gate

Present ticket → case counts, EARS coverage, and the JSON/xlsx paths. **Stop.** Wait for approved / looks good / finalized. Do **not** proceed until that confirmation.

On confirmation, append via **`aidlc-approve`** (`phase: implementation`, action `Manual regression test cases generated and approved.`).

Standalone runs keep current generation behavior except they also wait for this approval. When chained from `aidlc-tdd` Step 5.7, return only after this row exists.

Print: `[manual-tc] Step 7 complete — manual test cases approved.`

## When NOT to use this skill

- pytest / TDD → `aidlc-tdd`
- Break work into Jira stories → `aidlc-jira-story-breakdown`
- Publish cases to Jira now → Jira MCP after this JSON exists
- No epic / no EARS yet → finish `aidlc-init` design first

## Additional resources

- Schema / Jira mapping: [examples.md](examples.md)
- Excel converter: [scripts/json_to_xlsx.py](scripts/json_to_xlsx.py)
