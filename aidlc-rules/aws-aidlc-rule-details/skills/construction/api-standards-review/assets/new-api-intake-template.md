# New API Intake Template

Use this template when designing a new HTTP API or adding endpoints to an existing service.

## How to use this template

- Fill every `Required` section.
- Fill every `Strongly Recommended` section unless it truly does not apply.
- If a section is skipped or marked not applicable, explain why.
- Document any intentional deviations from the Trimble API Standard.

For each section, set:

- `Section status`: `Complete` | `Not applicable` | `Skipped`
- `Why` if not complete

---

## 1. Document metadata
`Required`

- Section status:
- API or service name:
- Existing service or greenfield service:
- Owner team:
- Architect or primary contact:
- Date:

## 2. Service purpose and consumers
`Required`

- Section status:
- Business problem this API solves:
- Primary consumers:
- Secondary consumers:
- Key use cases:
- Non-goals:

## 3. Resource model and URL design
`Required`

- Section status:
- Primary resources:
- Relationships between resources:
- Which resources are top-level vs sub-resources:
- Proposed path sketches:
- Why the URL structure matches the resource model:
- Any action endpoints that must use `POST`:

## 4. Versioning and publication expectations
`Required`

- Section status:
- Proposed major version in the URL:
- Expected compatibility strategy:
- Whether `x-trimble-api-standard` will be declared in `info`:
- Publication or developer-console considerations:

## 5. Operation inventory
`Required`

- Section status:
- List the planned operations.

| Resource / endpoint area | Operation | HTTP method | Path sketch | Purpose |
| --- | --- | --- | --- | --- |
| Example | Create work item | POST | `/work-items` | Create a work item |

## 6. Authentication and authorization
`Required`

- Section status:
- Authentication model:
- Caller types:
  - user
  - application
  - device
  - other
- Authorization model:
- Protected resources:
- Object-level authorization expectations:
- Admin-only or delegated operations:

## 7. Request and response modeling
`Required`

- Section status:
- Main request bodies:
- Main response bodies:
- Structured payload formats:
- Required fields:
- Optional fields that should be omitted when unset:
- Any non-JSON formats that must be supported:

## 8. Pagination, filtering, and sorting
`Strongly Recommended`

- Section status:
- Does this API return collections:
- Pagination model:
  - none
  - offset
  - cursor
- Default `pageSize`:
- Maximum `pageSize`:
- Required `links` fields:
- Supported filters:
- Supported sort fields and default sort:
- Any search-style POST endpoints:

## 9. Headers and content negotiation
`Strongly Recommended`

- Section status:
- Public request headers:
- Public response headers:
- `Content-Type` expectations:
- `Accept` header expectations:
- Any caching or `Prefer` behavior:

## 10. Errors and failure behavior
`Required`

- Section status:
- Expected non-2xx responses by operation family:
- How `401` differs from `403`:
- Validation error behavior:
- Conflict handling:
- Problem types or error catalog expectations:
- Whether the Trimble Standard Error Payload is used directly:

## 11. Standard metadata and identifiers
`Strongly Recommended`

- Section status:
- Resource identifiers:
- Whether TRNs appear in the contract:
- Metadata fields to expose:
  - `createdAt`
  - `createdBy`
  - `updatedAt`
  - `updatedBy`
  - `deletedAt`
  - `deletedBy`
- Timestamp format expectations:

## 12. Performance and scale expectations
`Required`

- Section status:
- Target latency expectations:
- Expected throughput:
- Expected object counts:
- Typical payload sizes:
- Worst-case payload sizes:
- Why the proposed defaults and limits are safe:

## 13. Deviations or exceptions
`Required if any`

- Section status:
- Which Trimble API Standard rules are intentionally not followed:
- Why:
- User impact:
- Risk:
- Approval owner:

## 14. Open questions
`Required`

- Section status:
- Unresolved product questions:
- Unresolved contract questions:
- Unresolved auth questions:
- Unresolved performance questions:
