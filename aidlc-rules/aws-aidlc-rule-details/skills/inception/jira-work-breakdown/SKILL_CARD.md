# Skill Card: tp-ai-kit-jira-work-breakdown

## Description
Jira Work Breakdown creates Jira epics and issues from an approved delivery plan by mapping plan units (U-IDs) to Jira tickets with summaries and descriptions that link back to the plan. Requires the e-tools MCP server. This skill is ready for internal use.

## Owner
Platform AI Team (`platform-ai-team`)

## Version
1.0.0 — 2026-06-13

## Inputs
- Approved delivery plan with numbered units (U-IDs) from delivery-planning
- Jira project key and board access (via e-tools MCP: `https://mcp.trimble.tools/mcp`)

## Outputs
- Jira epics and issues created and linked to the delivery plan
- Jira issue URLs for each created ticket

## Known Risks and Mitigations
- **Risk:** Tickets created without an approved plan result in incorrect scope.
  **Mitigation:** Skill requires an approved delivery plan document before creating any Jira tickets.
- **Risk:** Duplicate tickets created if skill is run multiple times.
  **Mitigation:** Skill checks for existing tickets with matching U-ID references before creating.

## References
- skills/jira-integration/jira-work-breakdown/SKILL.md
- skills/sdlc-planning/delivery-planning/SKILL.md (upstream)
- e-tools MCP server: `https://mcp.trimble.tools/mcp`

## Security Notes
Makes API calls to the Trimble e-tools MCP server to create Jira tickets. Requires valid Jira credentials configured in the MCP server. No credentials are stored by this skill directly.
