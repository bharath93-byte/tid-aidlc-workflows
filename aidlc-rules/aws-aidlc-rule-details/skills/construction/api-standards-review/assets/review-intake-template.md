# Review Intake Template

Use this template when reviewing an existing HTTP OpenAPI specification.

## How to use this template

- Fill every `Required` section.
- If a section is not applicable, explain why.
- If the spec intentionally deviates from the Trimble API Standard, document it explicitly.

For each section, set:

- `Section status`: `Complete` | `Not applicable` | `Skipped`
- `Why` if not complete

---

## 1. Review request metadata
`Required`

- Section status:
- API or service name:
- Review requester:
- Team:
- Date:
- Review purpose:
  - pre-design validation
  - architecture review
  - readiness review
  - rewrite preparation

## 2. Spec under review
`Required`

- Section status:
- Spec path or pasted YAML location:
- OpenAPI version:
- Version or branch being reviewed:
- Is this a new API or a change to an existing API:

## 3. Business purpose and consumers
`Required`

- Section status:
- Business problem this API addresses:
- Primary consumers:
- Key use cases:
- Non-goals:

## 4. Authentication and authorization expectations
`Required`

- Section status:
- Authentication model:
- Caller types:
- Protected resources:
- Authorization model:
- Object-level authorization expectations:
- Any admin-only or delegated operations:

## 5. Data and contract expectations
`Strongly Recommended`

- Section status:
- Expected resource model:
- Pagination expectations:
- Filtering expectations:
- Sorting expectations:
- Header expectations:
- Error payload expectations:
- Metadata or identifier conventions:

## 6. Performance and scale expectations
`Required`

- Section status:
- Target latency expectations:
- Expected page sizes:
- Maximum page sizes:
- Payload size concerns:
- Throughput or traffic expectations:

## 7. Known intentional deviations
`Required if any`

- Section status:
- Which standard rules are intentionally not followed:
- Why:
- User impact:
- Risk:
- Who approved or owns the deviation:

## 8. Review focus areas
`Optional`

- Section status:
- Areas that need extra scrutiny:
  - versioning
  - resource naming
  - pagination
  - filtering
  - sorting
  - errors
  - security
  - headers
  - examples

## 9. Missing context already known
`Optional`

- Section status:
- What information is unavailable right now:
- What assumptions the reviewer is allowed to make:
