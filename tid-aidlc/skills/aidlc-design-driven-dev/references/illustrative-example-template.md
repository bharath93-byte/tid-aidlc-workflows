# Illustrative Example Template (design)

One **epic-level** walkthrough of a single primary scenario. Not a restatement of HLD/LLD, and **not one file per LLD**. LLDs stay per-feature under `designs/<feature>/LLD.md`. This file may cite several LLDs.

## File Location

`DOCS_DIR/illustrative-example.md`

## When to write

- **Full tier:** after HLD + all LLDs + all EARS are approved.
- **Lightweight (EARS-only):** after EARS are approved; derive the walkthrough from vision + EARS + ADR.
- **Coherence-check only:** skip this file.

## Standard Structure

~~~~markdown
# [Epic Name] — Illustrative Example

**Created**: YYYY-MM-DD
**Tier**: Full | Lightweight

## Scenario

**Actor**: who is acting
**Goal**: what they are trying to accomplish
**Primary path**: one sentence naming the happy path (not every edge case)

## Related Documents

- [High-Level Design](./high-level-design.md)   <!-- omit on Lightweight -->
- [Feature LLD](./designs/<feature>/LLD.md)     <!-- omit on Lightweight; cite each LLD this scenario touches -->
- [Sub-feature EARS](./designs/<feature>/<subfeature>-EARS.md)
- [Vision](./vision.md)
- [ADR](./adr.md)

## Step-by-step flow

Walk the actor through the architecture (HLD) and the components / APIs / data (LLD). Numbered steps. Each step names the component or boundary.

1. …
2. …

## Sample payload

Request/response or event payload **derived from the design** (not invented after the fact).

```json
{
  "example": true
}
```

## How EARS bullets are satisfied

| EARS id  | Bullet (short) | How this scenario satisfies it |
| -------- | -------------- | ------------------------------ |
| FEAT-001 | …              | …                              |

## Non-coverage (out of scope)

What this walkthrough does **not** claim. Edge cases, other actors, and deferred paths belong in LLD/EARS, not as extra scope here.
~~~~

## Rules

- One primary scenario only.
- Do not add features, endpoints, or edge cases that HLD/LLD/EARS (or vision + EARS + ADR on Lightweight) do not already specify.
- Construction (`aidlc-tdd`) treats this file as **scenario context**, not a second spec. The story's `ears_ref` / `lld_ref` remain the requirements contract.
