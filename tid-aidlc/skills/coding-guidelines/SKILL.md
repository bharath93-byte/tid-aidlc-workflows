---
name: coding-guidelines
description: >-
  Principal-engineer construction constraints for AI-DLC TDD. Load before any
  production or test code is written in aidlc-tdd (and Dual-Agent TDD Builder).
  Enforces KISS, DRY, YAGNI, SOLID SRP/OCP/ISP, naming, function size,
  fail-fast errors, structured logging, and forbids magic numbers, global
  mutation, and deep nesting. YAGNI maps to the story's lld_ref / ears_ref
  (Lightweight: EARS + ADR); the design illustrative example does not widen
  scope. Use when implementing or refactoring application/test code in the
  TDD loop, or when the user asks for coding guidelines.
---

# Coding guidelines (construction)

Load this skill **before** writing any production or test code in `aidlc-tdd` or Dual-Agent TDD **Builder**. These are generation-time constraints, not a GACR replacement. GACR still reviews against `collective-feedback-guidelines.md`.

**Announce when loaded:** "Applying **coding-guidelines** (KISS / DRY / YAGNI / SOLID; fail-fast; no magic numbers)."

## Scope of what to build (YAGNI)

Implement **only** what the current story's `lld_ref` / `ears_ref` specify.

- **Lightweight / EARS-only:** EARS + ADR. Skip LLD when `lld_ref` is `""`.
- `{EPIC_DIR}/illustrative-example.md` is **scenario context** (happy-path walkthrough). It does **not** add features, endpoints, or edge cases. Out-of-scope lines in that file stay out of scope.
- Do not add unrequested utilities, configurability, or "just in case" abstractions.

## Principles

### KISS

Prefer the simplest design that satisfies the story. No speculative layers, wrappers, or frameworks.

### DRY

Reuse existing helpers and patterns in the repo. Do not copy-paste a third variant of the same logic. Extract only when a second real caller exists (not for a hypothetical one).

### YAGNI

Do not implement behavior the EARS/LLD (or EARS+ADR) do not require. The illustrative example is not extra AC.

### SOLID (enforce these)

- **SRP:** one reason to change per module/function. Split mixed orchestration + I/O + formatting.
- **OCP:** extend via new types or well-named branches at existing seams; do not scatter one-off `if kind ==` forks through unrelated modules.
- **ISP:** do not force callers to depend on methods they do not use. Keep interfaces narrow.

(LSP and DIP: follow existing repo patterns; do not introduce inversion-of-control machinery the story does not need.)

## Naming and size

- Names describe behavior (`increment_window_counter`, not `do_it` / `helper2`).
- Functions stay small enough to read without scrolling past one screen of mixed concerns. If a function both validates, persists, and emits metrics, split at those seams.
- Match the repo's existing naming (modules, tests, log event names).

## Errors and logging

- **Fail fast.** Validate at the boundary; do not swallow exceptions or return sentinel success.
- Log at the point of failure with structured fields the design names (no string-concatenated ad-hoc messages when the codebase uses structured logging).
- Do not catch-and-ignore unless the ADR/LLD explicitly requires fail-open.

## Forbidden

- **Magic numbers** — named constants (or values already defined in the story/LLD) only.
- **Global mutation** — no module-level mutable singletons for request state.
- **Deep nesting** — flatten with early returns; avoid `if/else` pyramids beyond two levels of real branching.
- **Unused utilities** — do not leave helpers that no test or caller uses.

## Dual-Agent TDD

- **Builder (GREEN):** this skill is a hard constraint. Read it before writing production code.
- **Tester (RED):** do **not** dump this skill into the Tester prompt (test-author firewall). Tester follows TDD test anti-patterns only.

## When NOT to use

- Design-only work (`aidlc-design-driven-dev`) — no application code yet.
- GACR critic prompts — critics use `collective-feedback-guidelines.md`.
