---
name: tp-ai-kit-api-standards-review
description: Design, review, and rewrite HTTP OpenAPI specifications against the live Trimble API Standard. Use when creating a new API spec, validating OpenAPI YAML/JSON, running Trimble Spectral lint, checking standards compliance, or asking for a standards-aligned rewrite.
disable-model-invocation: true
category: sdlc-planning
sdlc_phase: design
status: stable
owner: platform-ai-team
tags: [design, api, openapi, standards]
supported_agents:
  - cursor
  - copilot
  - claude-code
requires_agents: false
security_reviewed: false
last_reviewed: "2026-06-13"
skill_card: ./SKILL_CARD.md
metadata:
  internal: false
---

# API Standards Review

> **Trigger**: "Design an API spec", "Review this OpenAPI YAML", "Lint this spec", "Check this API against standards", "Check Trimble compliance", "Run spectral for this spec" or similar
>
> **Purpose**: Create or review reusable HTTP API contracts against the live Trimble API Standard. Use **automated lint first** when validating existing specs, then layer **manual review** against the live standard and the structured report template.

---

## Before You Start

1. Fetch the live Trimble API Standard before giving design or review guidance:
   - `https://developer.trimble.com/docs/api-standard/llms.txt`
   - `https://developer.trimble.com/docs/api-standard/_llms-txt/latest.txt`
2. Treat the live Trimble API Standard as the primary source of truth for interpretation and gaps Spectral does not cover.
3. If the user provides additional team or repo-local API rules, treat them as additive constraints and explicitly call out conflicts with the Trimble standard.
4. Limit this skill to HTTP/OpenAPI contract work. Do not drift into implementation details unless the user asks.

---

## Automated lint (Trimble Spectral)

Use this **before** deep manual review when the user is validating or reviewing an existing spec. It surfaces rule IDs, paths, and MUST vs SHOULD severity so you spend time on judgment calls, not re-deriving every mechanical check.

### 1. Find OpenAPI specs

- Look for `openapi.yaml`, `openapi.json`, `*.openapi.yaml`, `swagger.yaml`, or paths the user gave.
- If none are found, say so and ask for a path or a new spec.

### 2. Choose how to run the linter

**If the project has the Trimble linter** (for example `scripts/lint-trimble.js`, `npm run lint` that runs it, and `rules/trimble/` or similar):

- From the project root: `npm run lint` or `node scripts/lint-trimble.js [--ruleset both|r2026.1|r2023.1] [spec paths...]`
- Pass explicit paths when the user named files: `npm run lint -- path/to/openapi.yaml`
- Run `npm install` first if dependencies may be missing.
- Prefer this path for **full** Trimble rules (including custom Spectral functions) when the repo provides them.

**If the project does not have the Trimble linter**:

- Run Spectral against the published Trimble ruleset (some custom rules may not apply remotely):

  ```bash
  npx --yes @stoplight/spectral-cli lint -r "https://raw.githubusercontent.com/trimble-oss/openapi-spectral-rules/refs/tags/1.0/spectral.yaml" -f stylish <spec path>
  ```

- Present results using the **Lint report format** below. Optionally suggest adopting the full in-repo linter for complete rule coverage.

### 3. Ruleset version

- Default to r2026.1 unless the user asks for one version.
- When using the project script, pass `--ruleset both`, `--ruleset r2026.1`, or `--ruleset r2023.1` as needed.

### 4. Lint report format (per spec)

Use this as a dedicated section inside Review Mode output (or standalone when the user only asked to lint). **Do not compute or report a numeric score** unless the user explicitly asks later.

```markdown
## Trimble API Standard Lint: <filename> [r2023.1 / r2026.1 / both]

### Errors (MUST/REQUIRED)
- **<rule>**
  - Location: <path / operation / component>
  - Issue: <message>
  - Fix: Align with Trimble API Standard or rule documentation.

### Warnings (SHOULD/RECOMMENDED)
- **<rule>**
  - Location: ...
  - Issue: ...
  - Fix: ...

### Summary (Spectral only — when semantic governance JSON is also in this review, merge counts into totals per consolidation rules in the skill reference)

- Errors: N | Warnings: M
```

If there are no violations for the ruleset(s) run, state that clearly.

#### Summary (consolidated across Spectral + semantic governance)

When semantic governance validation was performed for the same spec(s), present a single consolidated summary **after** both the lint section and the semantic JSON (or embedded semantic findings table):

- **Errors:** total = Spectral errors (MUST/REQUIRED) **+** count of semantic findings with `severity: 0`
- **Warnings:** total = Spectral warnings (SHOULD/RECOMMENDED) **+** count of semantic findings with `severity: 1`
- **Semantic info / hints (optional):** count of semantic findings with `severity: 2` or `severity: 3` (do not add these to Errors or Warnings unless the user asks to roll them up)

Show the breakdown so sources are auditable, for example: `Errors: 4 (Spectral: 3, Semantic: 1) | Warnings: 12 (Spectral: 10, Semantic: 2)`.

### 5. Map lint results into the review report

- Treat **Errors (MUST/REQUIRED)** as **blocking findings** in [Review report template](assets/review-report-template.md) unless the user has documented an approved deviation.
- Treat **Warnings (SHOULD/RECOMMENDED)** as **non-blocking findings** unless the user or standard elevates them.
- Avoid duplicating the same issue in prose; reference the rule ID and location, then add narrative only for context, tradeoffs, or standard interpretation.

### 6. Manual checks (beyond Spectral)

Spectral does not catch everything. After lint, still check the spec against the **Review areas** below and the live standard for items such as plural resource naming, US English in descriptions, pagination/filter/sort shape, and consistency of examples with schemas. Record additional issues in the lint section or the blocking/non-blocking tables as appropriate.

For **semantic governance** checks that are intentionally non-deterministic (resource naming intent, action-oriented paths, unit/time semantics), follow **[Semantic governance rules](assets/semantic-governance-rules.md)** instead of ad-hoc prose-only guesses; merge those results into the **consolidated summary** and the review report’s blocking/non-blocking tables using the severity mapping defined there.

---

## Semantic governance validation (Trimble OpenAPI)

For judgment beyond Spectral (and when the user asks for semantic or governance validation), read and apply **[Semantic governance rules](assets/semantic-governance-rules.md)**. It defines the semantic checks, allowed finding `code` values, JSON `findings` shape, severity mapping, consolidation with Spectral counts, and **Review Mode** integration (intake → lint → semantic → report).

---

## Modes

### Design Mode

Use when the user wants a new OpenAPI spec or a new API contract.

Workflow:

1. Start with [New API intake](assets/new-api-intake-template.md).
2. Ask follow-up questions only for missing blockers.
3. Produce:
   - OpenAPI YAML
   - a short assumptions and decisions summary
4. Align the contract with the live Trimble API Standard and any explicit user-approved constraints.
5. After generating and writing the spec to disk, run **Automated lint** once and fix any errors before handing off.

### Review Mode

Use when the user provides OpenAPI YAML/JSON or asks whether a spec complies with standards.

Workflow:

1. Gather context with [Review intake](assets/review-intake-template.md).
2. **Automated lint**: Find spec(s), run the project Trimble linter or Spectral as in **Automated lint**, default ruleset r2026.1 unless scoped (or as narrowed during intake).
3. **Semantic governance validation**: Apply [Semantic governance rules](assets/semantic-governance-rules.md) to the same spec(s); produce JSON `findings` and map severities into the report.
4. Review the contract against the live Trimble API Standard; reconcile with lint output and semantic findings (no double-counting).
5. Return findings using [Review report template](assets/review-report-template.md), including the **Lint report format** section per spec, semantic JSON (or a clear tabular rendering of the same findings), and the **consolidated** Errors/Warnings summary.

### Rewrite Mode

Use when the user wants the reviewed spec corrected or regenerated after findings.

Workflow:

1. If no review exists yet, run **Review Mode** (lint + structured report) first.
2. Rewrite the OpenAPI YAML to fix blocking findings while preserving stated requirements and approved deviations.
3. Keep the rewritten spec internally consistent across paths, schemas, responses, headers, and error payloads.
4. Re-run **Automated lint** on the updated file(s) and confirm error count is reduced or resolved; summarize any remaining warnings.
5. Optionally re-run **Semantic governance validation** and report the **consolidated** Errors/Warnings if the user cares about semantic findings.

---

## Review Areas

Check the contract across these areas (lint plus manual review):

- OpenAPI completeness and versioning
- resource naming and URL structure
- HTTP verb semantics
- request and response modeling
- field naming and optional/required behavior
- content negotiation and documented headers
- pagination, filtering, and sorting
- standard metadata and identifier conventions
- error payloads and documented non-2xx responses
- security expectations, including authentication, JWT validation, and object-level authorization
- time, duration, unit, and format conventions

---

## Output Expectations

### For Design Mode

Return:

- a short summary of assumptions or unresolved choices
- the generated OpenAPI YAML

### For Review Mode

Return:

- **Trimble Spectral lint** section(s) per spec (see Lint report format)
- **Semantic governance** JSON `findings` (or equivalent structured list) per spec when validation was in scope
- **Consolidated summary** of Errors and Warnings across Spectral + semantic governance (see Automated lint)
- executive summary
- pass/fail checklist by standards area
- blocking findings
- non-blocking findings
- deviations register
- missing inputs
- final recommendation

### For Rewrite Mode

Return:

- a short summary of what changed
- the corrected OpenAPI YAML
- lint re-run summary (errors/warnings remaining)
- any remaining assumptions or approved deviations

---

## Guardrails

- Do not invent business requirements that the user has not provided or approved.
- Do not treat recommended guidance as mandatory unless the standard or the user explicitly requires it.
- Do not silently apply repo-specific conventions as if they were Trimble-wide rules.
- Do not skip documenting conflicts, assumptions, or missing inputs that affect confidence.

---

## Additional Resources

- [Trimble API Standard r2026.1 – Overview](https://developer.trimble.com/docs/api-standard/specification/r2026-1/overview)
- [Trimble API Standard r2023.1 – Overview](https://developer.trimble.com/docs/api-standard/specification/r2023-1/overview)
- [Trimble OpenAPI Spectral rules](https://github.com/trimble-oss/openapi-spectral-rules)
- [New API intake](assets/new-api-intake-template.md)
- [Review intake](assets/review-intake-template.md)
- [Review report template](assets/review-report-template.md)
- [Semantic governance rules](assets/semantic-governance-rules.md)
- [Examples](references/examples.md)
