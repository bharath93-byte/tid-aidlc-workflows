# Skill Card: tp-ai-kit-scoped-questioning

## Description
Scoped Questioning interviews the user one topic at a time until requirements, contracts, trade-offs, and edge cases are explicit enough to proceed safely with planning or implementation. This skill is ready for internal use.

## Owner
Platform AI Team (`platform-ai-team`)

## Version
1.0.0 — 2026-06-13

## Inputs
- Ambiguous plan, API spec, technical design, event schema, or implementation task
- User responses to follow-up questions

## Outputs
- Structured set of explicit, agreed-upon requirements and decisions
- Cleared list of hidden assumptions suitable as input for delivery-planning or prd-authoring

## Known Risks and Mitigations
- **Risk:** Over-questioning leads to friction — user feels interrogated.
  **Mitigation:** Skill enforces single-topic-at-a-time discipline and stops when ambiguity is resolved.
- **Risk:** Missed assumptions slip through if user is terse.
  **Mitigation:** Skill prompts for trade-offs and edge cases systematically, not just happy-path requirements.

## References
- skills/sdlc-core/scoped-questioning/SKILL.md
- skills/sdlc-planning/delivery-planning/SKILL.md (commonly chained after)

## Security Notes
No external calls. No data persistence. Operates entirely on user-provided conversational input.
