# Skill Card: tp-ai-kit-delivery-planning

## Description
Delivery Planning turns PRDs, technical designs, API specs, and ADRs into agent-ready implementation plans with numbered units (U-IDs), explicit dependencies, parallel vs sequential execution groups, and epic split recommendations. This skill is ready for internal use.

## Owner
Platform AI Team (`platform-ai-team`)

## Version
1.0.0 — 2026-06-13

## Inputs
- PRD, TDD, or ADR document (from prd-authoring or manually written)
- API specification (optional)
- System architecture context

## Outputs
- Delivery plan with numbered implementation units (U-IDs)
- Dependency graph and parallelism annotations
- PR-sized breakdown suitable for Jira ticket creation (jira-work-breakdown)

## Known Risks and Mitigations
- **Risk:** Plan produced without complete design inputs leads to rework.
  **Mitigation:** Skill validates that PRD and TDD are present before generating the plan.
- **Risk:** Tasks sized too large, creating unreviable PRs.
  **Mitigation:** Skill enforces PR-sized unit guidance and flags oversized units.

## References
- skills/sdlc-planning/delivery-planning/SKILL.md
- skills/jira-integration/jira-work-breakdown/SKILL.md (downstream)
- skills/sdlc-planning/prd-authoring/SKILL.md (upstream)

## Security Notes
No external calls. No data persistence. Operates on user-provided design documents.
