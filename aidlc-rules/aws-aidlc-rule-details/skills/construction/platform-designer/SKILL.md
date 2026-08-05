---
name: tp-ai-kit-platform-designer
description: >-
  Produces a Trimble platform integration TDD with ADRs — service topology, auth
  flow, API contract mapping, comms pattern, and error propagation — grounded in
  the platform Knowledge Base and the user's own repository context. Accepts an
  optional platform-advisor handoff or runs fully standalone.
disable-model-invocation: true
internal: true
category: integrations
sdlc_phase: pre-sdlc
status: beta
owner: platform-ai-team
tags: [platform, integration, designer, kb, tdd]
supported_agents:
  - cursor
  - copilot
  - claude-code
requires_agents: true
security_reviewed: false
last_reviewed: "2026-07-02"
skill_card: ./SKILL_CARD.md
---

# Skill: platform-designer

**Trigger:** `/tp-ai-kit-platform-designer` or when a user wants to design an integration
architecture, map API contracts, define auth flows, or produce a Technical Design Document
(TDD) for a Trimble platform integration.

---

## Prerequisites

**platform-kb MCP** (server name: `platform-kb`, url: `https://kb.stage.trimble-ai.com/v1/mcp`) is required.

At startup the skill runs `.cursor/references/integrations-platform/steps/00-mcp-preflight.md`,
which probes `ListLibraries` and handles all three cases automatically:

- **Configured and reachable** → proceeds silently
- **Not configured** → prints the `mcp.json` snippet and stops
- **Tool calls disabled (plan/ask mode)** → tells the user to switch to Agent mode and stops

## Purpose

This skill produces a **Technical Design Document (TDD) with Architecture Decision Records (ADRs)**
for integrating one or more Trimble platform services. It runs a KB-grounded, repo-aware pipeline:

1. **Grilling** — one question at a time, KB-informed forks, to lock service selection, auth model,
   comms pattern, and error contract
2. **Repo discovery** — reads the user's existing codebase (or service-context wiki if present)
   to ground design decisions in the actual tech stack
3. **KB pipeline** — multi-pass fetch, rerank, and gap analysis via platform-kb MCP
4. **TDD synthesis** — produces a 7-section TDD with ADRs using an integration-shape template

The skill works **fully standalone** — a platform-advisor handoff is a convenience shortcut that
pre-fills known context, not a requirement.

## When to use this skill

- "Design my integration with TID / IAM / ENS / File Service / Processing Framework"
- "I need an auth flow design for my service"
- "Produce a TDD for this platform integration"
- "Map the API contracts I need for [capability]"
- "Design the service topology for [feature]"
- After `/tp-ai-kit-platform-advisor` — say "design this" to hand off

## When NOT to use this skill

- User only needs service selection guidance → use `/tp-ai-kit-platform-advisor`
- User is ready to write code and has an existing TDD → use `/tp-ai-kit-platform-developer`

---

## Execution

On invocation, read and follow:

```
.cursor/references/integrations-platform/designer/orchestrator.md
.cursor/references/integrations-platform/orchestrator-base.md
```

---

## Pipeline Overview

```
00 — MCP preflight
01 — Session init (audience, UUID, artifact)
02 — Design grill (KB-informed, fork-derived; 4 rounds standalone / 2 adaptive)
03 — Discover services
02b — Repo discovery (explore → api-analyzer escalation; re-grill on conflicts)
04 — Classify intent (integration shape: user-auth / service-to-service / event-driven / data-pipeline)
05 — KB fetch pass 1 (budget: 5 calls, bias: contractual, pattern, referential)
06 — Rerank + coverage rubric
06b — KB-grounded refinement (one scenario-fork question if budget allows)
07 — Gap analyze
08 — (optional) KB fetch pass 2 (budget: 4 calls)
09 — Synthesize TDD via platform-synthesizer (template selected from integration shape)
10 — Deliver TDD + footer + handoff artifact
```

## Entry modes

### With advisor handoff

If `.ai/artifacts/platform-advisor-handoff-*.md` is present:

- **Adaptive** (`coherence_status` solid, specific gaps): ask one question per unresolved gap (≤ 2 rounds), then proceed
- **Full grill** (`coherence_status` fragmented or intent sparse): run 4-round grill, pre-fill known fields from handoff
- **Skip grill** (no gaps, all design fields present): proceed directly to Step 03

### Standalone (no handoff)

Run full 4-round KB-informed grill starting from service + goal. Each answer triggers a targeted
KB search to derive the next fork question.

---

## TDD Output

The TDD contains seven sections:

1. **Context** — user goal, tech stack from repo, audience
2. **Integration Shape** — classified pattern + rationale
3. **Service Topology** — services, roles, dependency order
4. **Architecture Decisions (ADRs)** — one ADR per key decision
5. **API Contract Mapping** — endpoints, scopes, tokens — KB-sourced
6. **Implementation Guidance** — step-by-step aligned to repo tech stack
7. **Gaps & Risks** — what KB did not cover; what engineer must validate

Template used is determined by the classified integration shape.

---

## Handoff

After TDD delivery, footer includes:
*"Say 'implement this' to hand off to the platform-developer skill."*

Handoff artifact written to: `.ai/artifacts/platform-designer-handoff-<session_id>.md`

---

## Recommendations

- Chain `tp-ai-kit-verification-before-completion` before treating the TDD as final
- Chain `tp-ai-kit-api-standards-review` if the design includes new API contracts
