# Skill Card: dual-agent-tdd

## Description
Dual-Agent TDD splits Code Generation into an unlinked Tester session (black-box RED from spec and API contract only) and an unlinked Builder session (GREEN implementation that must not edit tests). The Orchestrator prepares packets and records RED/GREEN evidence.

## Owner
Platform AI Team

## Version
1.0.0 — 2026-08-18

## Inputs
- Unit requirements (EARS, stories)
- Public contract (OpenAPI/AsyncAPI or orchestrator-written public-contract.md)
- Test framework constraints
- User opt-in to Dual-Agent TDD at Workflow Planning or Code Generation

## Outputs
- `aidlc-docs/construction/plans/{unit-name}-dual-agent-tdd-plan.md`
- `aidlc-docs/construction/{unit-name}/dual-agent/` packets, launch prompts, firewall manifest, RED/GREEN evidence
- Application tests (Tester) and production code (Builder) at workspace root
- Same Code Generation contract artifacts as the stage rule (`construction/dual-agent-tdd.md`)

## When to use it
When unbiased black-box tests matter and the user can open two additional agent sessions.

## When NOT to use it
Default single-session TDD; Standard code generation; unattended evaluator runs.

## Known Risks and Mitigations
- **Risk:** Tester session reads production source despite instructions.
  **Mitigation:** Allowlist in firewall-manifest; RED gate (tests must fail); reviewer flags Builder test edits and non-black-box tests.
- **Risk:** Two extra sessions add friction.
  **Mitigation:** Method is opt-in; default TDD remains single-session.

## References
- `construction/dual-agent-tdd.md`
- `common/dual-agent-separation.md`
- `tid-aidlc/skills/aidlc-dual-agent-tdd/SKILL.md`
