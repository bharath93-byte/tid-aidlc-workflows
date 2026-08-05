# Examples

## Example 1: New API intake

Use this abbreviated example to show the expected shape of a design request.

```markdown
## 1. Document metadata
- Section status: Complete
- API or service name: Work items API
- Existing service or greenfield service: Existing service
- Owner team: Platform engineering
- Architect or primary contact: Jane Doe
- Date: 2026-04-06

## 2. Service purpose and consumers
- Section status: Complete
- Business problem this API solves: Allow clients to create, update, and search work items across products.
- Primary consumers: Web app, internal integrations
- Secondary consumers: Reporting and automation tools
- Key use cases:
  - Create a work item
  - List work items by status
  - Update assignee and due date
- Non-goals:
  - Workflow engine orchestration

## 3. Resource model and URL design
- Section status: Complete
- Primary resources: workItems, workItemComments
- Relationships between resources: comments belong to a work item
- Proposed path sketches:
  - `/work-items`
  - `/work-items/{workItemId}`
  - `/work-items/{workItemId}/comments`
- Why the URL structure matches the resource model: the URL identifies resources with plural nouns and nests child resources beneath the owning work item.
- Any action endpoints that must use `POST`: none

## 8. Pagination, filtering, and sorting
- Section status: Complete
- Does this API return collections: yes
- Pagination model: cursor
- Default `pageSize`: 100
- Maximum `pageSize`: 500
- Required `links` fields:
  - `self`
  - `first`
  - `next`
- Supported filters:
  - `status`
  - `assigneeId`
- Supported sort fields and default sort:
  - `sortBy=-createdAt`
```

## Example 2: Review output excerpt

Use this abbreviated example to show the expected review style.

```markdown
## Review summary
- API or service: Work items API
- Spec reviewed: `specs/work-items.yaml`
- Standards applied:
  - live Trimble API Standard
- Overall recommendation: Approve with conditions
- Confidence level: Medium

## Executive summary
The contract is directionally sound, but it is not ready for approval yet. The main blockers are missing standard error payload examples, undocumented `Accept` behavior, and no declared default sort for collection endpoints.

## Blocking findings
| ID | Standards area | Severity | Finding | Why it matters | Suggested fix |
| --- | --- | --- | --- | --- | --- |
| B-01 | Errors | Blocking | `GET /work-items` documents `200` but does not model standard error payloads for `400`, `401`, `403`, or `404`. | Client integrations cannot rely on the published failure contract. | Add the expected non-2xx responses and use the Trimble Standard Error Payload. |
| B-02 | Sorting | Blocking | Collection endpoints do not declare supported sort fields or the default sort. | The Trimble API Standard requires documented sorting behavior for list responses. | Document `sortBy`, supported fields, and the default sort direction. |
| B-03 | Headers | Blocking | The spec does not describe `Accept` or `Content-Type` behavior. | Content negotiation rules must be explicit for interoperable clients. | Document supported media types and response content types for each relevant operation. |

## Deviations register
| ID | Deviation | Justification | Impact | Acceptable now | Owner |
| --- | --- | --- | --- | --- | --- |
| D-01 | Returns optional unset fields as explicit `null` values for one legacy resource. | Existing clients already depend on the presence of those keys in responses. | Medium | Yes | API architect |
```
