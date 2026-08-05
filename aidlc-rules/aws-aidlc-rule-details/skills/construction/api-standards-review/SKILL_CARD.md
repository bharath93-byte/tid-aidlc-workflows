# Skill Card: tp-ai-kit-api-standards-review

## Description
API Standards Review designs, reviews, and rewrites HTTP OpenAPI specifications against the live Trimble API Standard using Spectral lint rules. This skill is ready for internal use.

## Owner
Platform AI Team (`platform-ai-team`)

## Version
1.0.0 — 2026-06-13

## Inputs
- OpenAPI YAML or JSON specification (new or existing)
- Trimble API Standard (fetched live from the canonical source)

## Outputs
- Reviewed and annotated OpenAPI spec with violations flagged
- Standards-aligned rewrite of the specification
- Spectral lint report

## Known Risks and Mitigations
- **Risk:** Trimble API Standard changes and the skill evaluates against a stale version.
  **Mitigation:** Skill fetches the live standard on each invocation via the connect-api-spec skill integration.
- **Risk:** Spec rewrite introduces breaking changes.
  **Mitigation:** Skill highlights breaking vs non-breaking changes and requires explicit user approval before rewriting.

## References
- skills/api-standards-review/api-standards-review/SKILL.md
- Trimble API Standard (internal)
- CONTRIBUTING.md

## Security Notes
Makes outbound HTTP calls to fetch the live Trimble API Standard. No user data is transmitted. No credentials are required or stored.
