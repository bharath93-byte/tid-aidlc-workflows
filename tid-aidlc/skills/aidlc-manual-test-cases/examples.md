# Manual test-case JSON — schema example and Jira mapping

Surfaces, routes, and EARS ids come from **the current epic**. This sample is
shape-only — do not copy the fake names into another epic.

```json
{
  "_meta": {
    "epic": "example-epic",
    "epic_id": "IAM-0000",
    "generated_at": "2026-08-25T12:00:00Z",
    "type": "manual",
    "sources": ["vision", "hld", "lld", "ears"],
    "unmapped_stories": []
  },
  "IAM-0001": {
    "ticket": "IAM-0001",
    "title": "Short story title from state.json",
    "feature": "example-feature",
    "ears_file": "designs/example-feature/example-feature-EARS.md",
    "lld_file": "designs/example-feature/LLD.md",
    "demo_gaps_file": null,
    "test_cases": [
      {
        "id": "IAM-0001-TC-001",
        "summary": "Verify the designed happy path and check the named live surface",
        "description": "EARS-001: after the documented entry point, the store/metric the LLD names must update.",
        "priority": "High",
        "type": "Functional",
        "preconditions": [
          "Feature deployed in the target env",
          "Auth and config required by this story are present"
        ],
        "steps": [
          {
            "step": 1,
            "action": "Call the route / job / event this story owns",
            "expected_result": "Business success status (as designed)."
          },
          {
            "step": 2,
            "action": "Inspect the verification surface the LLD names (table, EMF, log, flag)",
            "expected_result": "The write / metric / log field the EARS bullet requires is present."
          }
        ],
        "verification_surfaces": ["API", "Logs"],
        "ears_refs": ["EARS-001"],
        "demo_gap_refs": [],
        "labels": ["manual", "example-feature"]
      }
    ]
  }
}
```

## Jira MCP field mapping (follow-up, not this skill)

| JSON | Jira |
|------|------|
| `summary` | issue summary |
| `description` + `preconditions` + `ears_refs` | description (wiki) |
| `steps[].action` | test step action |
| `steps[].expected_result` | test step expected result |
| `priority` | priority |
| `labels` | labels |
| `ticket` | parent / link |

Do not invent custom field ids; confirm create-meta at publish time.

## Excel output

`scripts/json_to_xlsx.py` on `{EPIC_DIR}/manual-test-cases.json`:

- **1 ticket** → one sheet named after the ticket
- **2+ tickets** → Summary (KPIs + bar chart) + All Cases + one sheet per ticket
