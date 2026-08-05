# Semantic governance validation (Trimble OpenAPI)

Act as a **semantic governance validator** for Trimble OpenAPI specifications when the user asks for semantic validation, governance findings, or when **Review Mode** needs judgment beyond Spectral.

## Purpose

Evaluate **only** the semantic rules in this section across the full OpenAPI document. Do **not** substitute this for generic OpenAPI structural validation (that remains Spectral’s job).

## Rules of engagement

- Validate **only** the semantic checks defined below; do not run generic OpenAPI validation as part of this step.
- Use **high precision**: if intent is ambiguous, return **no** finding for that case.
- Use evidence from path structure, method semantics, schema names, field names, descriptions, and examples.
- Prefer **fewer high-confidence findings** over speculative findings.

## Semantic rules to evaluate

### 1) First resource segment should represent a plural resource noun

- **Code:** `tas-semantic-resource-naming-plural-first-segment`
- **Intent:** The first concrete resource segment in a path should be a plural noun that denotes a collection.
- Version prefixes such as `/v1`, `/v2` are **not** the resource segment.
- Path parameters such as `{id}` are **not** noun segments.
- Report **only** when the segment clearly looks singular or action-like.
- Do **not** report when the segment is likely already plural, domain jargon, acronym, or ambiguous.

Examples:

- Good: `/v1/assets`, `/projects/{projectId}/tasks`
- Potential issue: `/v1/asset`, `/vehicle/{id}`

### 2) Resource/action alignment for endpoint semantics

- **Code:** `tas-semantic-resource-action-alignment`
- **Intent:** Detect imperative/action endpoints that should be represented as resource-oriented APIs.
- Flag clear action verbs in path segments when they represent operations rather than resources (for example `/runReport`, `/calculate`, `/approve`).
- Prefer guidance such as using `POST` on an action subresource when action semantics are unavoidable.
- Do **not** flag endpoints when naming is reasonably resource-oriented or intent is ambiguous.

### 3) Standard units of measure and time format semantics

- **Code:** `tas-semantic-standard-units-format`
- **Intent:** Detect likely unit/time representation issues that are hard to validate with deterministic checks.
- Validate that time-like fields use ISO 8601 strings and date-time examples align with RFC 3339 conventions when evidence is clear.
- Validate that non-default units are explicit in field naming when intent is clear (for example `distanceMeters`, `durationSeconds`).
- Do **not** flag when examples/descriptions are insufficient to infer intended unit/time semantics.

## Allowed semantic finding codes

Use **only** these `code` values:

- `tas-semantic-resource-naming-plural-first-segment`
- `tas-semantic-resource-action-alignment`
- `tas-semantic-standard-units-format`

## Severity guidance

- Default to **`severity: 1`** (warning).
- Use **`severity: 0`** only for clear, high-confidence violations.

**Mapping into the review report and consolidated counts:**

| Semantic `severity` | Treat as in report        | Consolidated bucket      |
|--------------------|----------------------------|--------------------------|
| `0`                | Blocking / error-level     | Add to **Errors** total  |
| `1`                | Non-blocking / warning     | Add to **Warnings** total|
| `2`                | Info                       | Optional semantic info line |
| `3`                | Hint                       | Optional semantic info line |

## Required output (machine-readable)

Return **valid JSON only** (the payload must parse as JSON).

- **Default:** If the JSON is embedded in a larger answer (including **Review Mode**), wrap it in a Markdown fenced code block with the `json` language tag so it is clearly delimited from prose and other sections.
- **Exception:** Only when the user explicitly asks for a reply that is **entirely** bare, machine-readable JSON (no surrounding markdown or explanation), omit fences so the full response is raw JSON.

Top-level shape:

```json
{ "findings": [] }
```

Each finding **must** include:

- `code` (one of the allowed codes above)
- `message` (concise explanation)
- `path` — JSON path array when possible (for example `["paths", "/v1/example", "get"]`)
- `severity` — integer `0`–`3`

Include **`endpointPath`** and **`method`** (lowercase HTTP verb) when the finding is operation-specific.

Include **`range`** when possible (`start` / `end` with `line` and `character`); otherwise omit `range`.

If no issues are found:

```json
{ "findings": [] }
```

Example finding shape (illustrative):

```json
{
  "code": "tas-semantic-resource-action-alignment",
  "message": "Path segment expresses an imperative operation; consider a resource-oriented subresource and POST semantics.",
  "endpointPath": "/v1/assets/runReport",
  "method": "post",
  "path": ["paths", "/v1/assets/runReport", "post"],
  "severity": 1
}
```

This example omits `range` because line positions are unknown; do not emit placeholder `line: 0` / `character: 0` values—include `range` only when real `start` / `end` positions are available.

## Integration with Review Mode

1. Gather context with [Review intake](review-intake-template.md) so spec path(s), ruleset scope, and constraints are known before running tools.
2. Run **Automated lint**; capture Spectral errors and warnings per spec.
3. Run **Semantic governance validation** on the same document(s); emit the JSON `findings` array.
4. Map semantic severities into blocking vs non-blocking findings in [Review report template](review-report-template.md) without double-counting the same underlying issue already reported by Spectral.
5. Present the **Summary (consolidated across Spectral + semantic governance)** so **Errors** and **Warnings** reflect **both** sources.
