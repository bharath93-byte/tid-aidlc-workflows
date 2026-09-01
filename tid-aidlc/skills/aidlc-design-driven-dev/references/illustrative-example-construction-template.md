# Illustrative Example Template (construction)

Epic-level companion to `illustrative-example.md`. Same happy-path spine, plus corner cases grounded in **implemented code**. Written after every story is `done` and TDD Step 5.5 is approved. Not per-story and not per-LLD.

## File Location

`DOCS_DIR/illustrative-example-construction.md`

Referenced from `aidlc-tdd` Step 5.6.

## Standard Structure

~~~~markdown
# [Epic Name] — Construction Illustrative Example

**Created**: YYYY-MM-DD
**Design example**: ./illustrative-example.md

## Scenario

Reuse the actor, goal, and primary path from the design illustrative example. Do not invent a different happy path.

## Related Documents

- [Design illustrative example](./illustrative-example.md)
- [High-Level Design](./high-level-design.md)
- [Feature LLD](./designs/<feature>/LLD.md)
- [Sub-feature EARS](./designs/<feature>/<subfeature>-EARS.md)
- [Vision](./vision.md)
- [ADR](./adr.md)

## Happy-path flow (as implemented)

Same numbered spine as the design example. Replace design-only names with **real** files, routes, tests, or log/metric names.

1. … (`path/to/handler.py`, route `POST /…`, test `tests/…`)
2. …

## Sample payload (as implemented)

Request/response or event as the code actually accepts/emits.

```json
{
  "example": true
}
```

## Corner Cases

Required. Ground each row in implemented code, not design-only fiction.

| Case                      | Source (LLD edge / EARS negative) | Behavior (fail-open / fail-closed per ADR/LLD) | Evidence (file, route, test, log, metric) |
| ------------------------- | --------------------------------- | ---------------------------------------------- | ----------------------------------------- |
| Empty / malformed input   |                                   |                                                |                                           |
| Missing dependency        |                                   |                                                |                                           |
| Mixed config / rollout    | only if the design has them       |                                                |                                           |

Also cover:

- Each LLD Edge Case and relevant EARS negative/exception for the primary scenario
- Fail-open / fail-closed as the ADR/LLD states

## Non-coverage

What is still out of scope (must match the design example unless a later ADR/LLD change was approved).
~~~~

## Rules

- Pointers must be real (files, routes, tests, log/metric names).
- Do not treat this file as extra acceptance criteria for already-closed stories.
- Skip this gate for ungoverned hotfixes (no epic).
