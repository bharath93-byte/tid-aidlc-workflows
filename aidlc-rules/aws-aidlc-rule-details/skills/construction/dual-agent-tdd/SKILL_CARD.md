# Skill Card: dual-agent-tdd

## Description
Dual-Agent TDD splits Code Generation into a Tester Task (black-box RED from spec and API contract only) and a Builder Task (GREEN implementation that must not edit tests). The Orchestrator prepares packets, dispatches both as `generalPurpose` Task sub-agents (same pattern as `aidlc-tdd`), and records RED/GREEN evidence. The user does not open extra chats or run tests; only approval gates are manual.

## Owner
Platform AI Team

## Version
1.1.0 — 2026-08-19

## Inputs
- Unit requirements (EARS, stories)
- Public contract (OpenAPI/AsyncAPI or orchestrator-written public-contract.md)
- Test framework constraints
- User opt-in to Dual-Agent TDD at Workflow Planning or Code Generation

## Outputs
- `aidlc-docs/construction/plans/{unit-name}-dual-agent-tdd-plan.md`
- `aidlc-docs/construction/{unit-name}/dual-agent/` packets, Task prompt bodies, firewall manifest, RED/GREEN evidence
- Application tests (Tester) and production code (Builder) at workspace root
- Same Code Generation contract artifacts as the stage rule (`construction/dual-agent-tdd.md`)

## When to use it
When unbiased black-box tests matter (the test author must not see implementation).

## When NOT to use it
Default single-session TDD; Standard code generation.

## Known Risks and Mitigations
- **Risk:** Tester Task reads production source despite instructions (Task agents have workspace access).
  **Mitigation:** Allowlist in the Task prompt and firewall-manifest; files-touched audit; RED gate (tests must fail); reviewer flags Builder test edits and non-black-box tests.
- **Risk:** Prompt isolation is weaker than a separate human chat.
  **Mitigation:** Method remains opt-in; default TDD is unchanged; Orchestrator must not dump `src/` into the Tester prompt.

## References
- `construction/dual-agent-tdd.md`
- `common/dual-agent-separation.md`
- `tid-aidlc/skills/aidlc-dual-agent-tdd/SKILL.md`
