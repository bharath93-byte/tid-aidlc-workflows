# Skill Card: tp-ai-kit-platform-designer

## Description
`tp-ai-kit-platform-designer` produces a Technical Design Document (TDD) with Architecture Decision Records (ADRs) for integrating Trimble platform services. It grills the user with KB-informed questions, reads the user's repository for tech-stack context, fetches from the platform Knowledge Base, and synthesises an architect-oriented TDD using an integration-shape template.

**Availability:** Internal — Platform AI Team
**Status:** beta
**Version:** 1.14.0
**Introduced:** 1.14.0

---

## Owner
**Team:** Platform AI Team
**GitHub Team:** trimble-oss/platform-ai-team
**Contact:** platform-ai-kit-maintainers-ug@trimble.com

---

## License / Terms of Use
Internal use only. Not for redistribution outside the organization.

---

## Use Case
**Who should use this:** Developers and architects designing a Trimble platform integration.
**When to use it:** When integration architecture decisions need to be locked before implementation — auth flow, API contracts, service topology, comms pattern, error propagation.
**When NOT to use it:** When the user only needs service selection guidance (platform-advisor) or is ready to generate implementation code (platform-developer).

---

## Deployment Geography
Runs locally in developer AI tools (Cursor IDE, GitHub Copilot, Claude Code). No cloud deployment.
Data stays in the developer's local environment unless the AI tool routes to a cloud model endpoint.

---

## Known Risks and Mitigations

| Risk | Severity | Mitigation |
|---|---|---|
| TDD design decisions are non-deterministic (LLM-generated) | High | Human review required; chain `tp-ai-kit-verification-before-completion` before treating TDD as final |
| KB gaps may leave design decisions unresolved | Medium | Skill surfaces all gaps explicitly in TDD section 7; engineer must validate |
| Repo discovery may miss dynamic or runtime configuration | Medium | Skill notes what it could not find; grill questions cover the rest |
| Multi-service designs may produce conflicting ADRs | Medium | Re-grill step after repo discovery resolves conflicts before synthesis |
| MCP server unavailable (network, auth) | Medium | Skill checks MCP at startup and exits with setup instructions |
| Agent loops if synthesizer returns inconclusive results | Low | Maximum iteration caps defined in orchestrator-base |

---

## Skill Output
**Output type:** Technical Design Document (Markdown with YAML frontmatter)
**Output format:** 7-section TDD with ADRs, shaped by integration pattern template
**Output location:** Inline chat response; `.ai/artifacts/platform-designer-handoff-<session_id>.md`
**Determinism:** Non-deterministic (LLM-generated); human review required before implementation.

---

## Skill Version
**Introduced:** unreleased
**Last governance review:** 2026-07-02
**SkillSpector scan:** PENDING
**Risk score:** PENDING

---

## Ethical Considerations
- **Human review expectation:** All TDD outputs MUST be reviewed by a human before being used as the basis for implementation.
- **Bias risk:** Model outputs may reflect training data biases; apply domain and platform expertise when reviewing.
- **Data sensitivity:** Do not paste secrets, PII, or proprietary data into skill prompts.
- **Misuse concern:** TDD is advisory; integration architecture requires engineering validation and platform team sign-off where required.

---

## References
- Source: `skills/integrations/platform-designer/SKILL.md` in `platform-cursor-kit`
- Orchestrator: `.cursor/references/integrations-platform/designer/orchestrator.md`
- Shared pipeline: `.cursor/references/integrations-platform/orchestrator-base.md`
- platform-kb MCP: https://kb.stage.trimble-ai.com/v1/mcp

---

## Supporting Skills
| Skill | Relationship |
|---|---|
| `tp-ai-kit-platform-advisor` | Optional upstream — advisor handoff pre-fills intent context |
| `tp-ai-kit-platform-developer` | Downstream — consumes the TDD handoff artifact |
| `tp-ai-kit-api-standards-review` | Optional peer — validates designed API contracts |
| `tp-ai-kit-verification-before-completion` | Recommended gate before treating TDD as final |
