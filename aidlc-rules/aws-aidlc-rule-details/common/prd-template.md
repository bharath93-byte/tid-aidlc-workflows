# PRD: [Feature Name]

Status: [Draft | In Review | Approved]

## Overview

[2–4 paragraphs: what is changing, for whom, and the rollout model. State locked decisions explicitly.]

## Problem Statement

- **Today**: [Current behavior and pain points]
- **Product requirement**: [What users/integrators need]
- **Operational requirement**: [Safety, rollout, migration constraints]

## Goals / Success Metrics

| Goal | Metric / signal |
| --- | --- |
| [Goal 1] | [Measurable outcome] |
| [Goal 2] | [Measurable outcome] |

## User Stories

| ID | Story | Priority |
| --- | --- | --- |
| US-1 | As a **[role]**, I [action] so that [outcome]. | P0 |
| US-2 | As a **[role]**, I [action] so that [outcome]. | P1 |

## Acceptance Criteria (per story)

### US-1 — [Short title]

- Given [context], when [action], then [expected outcome].
- Given [edge case], when [action], then [expected outcome].

### US-2 — [Short title]

- Given [context], when [action], then [expected outcome].

## Functional Test Scenarios

| ID | Scenario | Expected result |
| --- | --- | --- |
| FT-1 | [End-to-end scenario] | [Pass criteria] |

## Edge Cases & Error Scenarios

| Case | Expected behavior |
| --- | --- |
| [Invalid input / missing resource] | [HTTP code / error envelope / user message] |

## Non-Functional Requirements (Performance, Security, Scalability)

| Area | Requirement |
| --- | --- |
| Performance | [Latency, throughput, load test target] |
| Security | [Auth, data handling, threat notes] |
| Scalability | [Growth assumptions] |

## Out of Scope

- [Explicit non-goals for this release]

## Dependencies

| Dependency | Owner | Notes |
| --- | --- | --- |
| [Service / team / flag] | [Team] | [Blocking or parallel] |

## API Contract Expectations

> Remove this section if the feature has no HTTP API surface.

| Item | Expectation |
| --- | --- |
| Base path | `[path]` |
| Methods | [GET / POST / …] |
| Auth | [Model] |
| Versioning | [Strategy] |
| Errors | [Envelope pattern] |

## Event Contract Expectations

> Remove this section if the feature has no event surface.

| Item | Expectation |
| --- | --- |
| Trigger | [When emitted] |
| Schema | [CloudEvents type, required fields] |
| Idempotency | [Rules] |

## Data Requirements

> Remove this section if no persistent data changes.

| Item | Requirement |
| --- | --- |
| Storage | [Store / table / attribute] |
| Migration | [Backfill, flags, suppression rules] |

## Alternative Approaches Considered (2–3 options, trade-offs, recommendation)

| Option | Description | Trade-offs | Verdict |
| --- | --- | --- | --- |
| **A — [Name] (chosen)** | [Description] | **Pros**: … **Cons**: … | **Recommended** |
| **B — [Name]** | [Description] | **Pros**: … **Cons**: … | Rejected / Deferred |

## Open Questions

- [Question] — [Owner / target date]

---

*Related artifacts: `docs/planning/[feature]/technical-design.md`, `docs/architecture/decisions/`, `docs/plans/`*
