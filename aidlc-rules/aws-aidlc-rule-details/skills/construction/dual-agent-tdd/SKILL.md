---
name: dual-agent-tdd
description: >-
  Dual-Agent TDD for Code Generation: Orchestrator prepares firewalled packets
  then dispatches Tester (RED) and Builder (GREEN) as generalPurpose Task
  sub-agents. Tester sees spec and API contract only. Use when the user
  requests Dual-Agent TDD, Builder vs Tester, or a test author firewall.
disable-model-invocation: true
category: sdlc-construction
sdlc_phase: construction
status: stable
owner: platform-ai-team
tags: [tdd, dual-agent, tester, builder, construction]
supported_agents:
  - cursor
  - copilot
  - claude-code
requires_agents: true
security_reviewed: false
last_reviewed: "2026-08-19"
skill_card: ./SKILL_CARD.md
---

# Dual-Agent TDD

> **Trigger**: "Dual-Agent TDD", "Builder vs Tester", "firewalled tests", or Code Generation Step 0 when this skill is selected
>
> **Purpose**: HOW to dispatch Tester and Builder Tasks. WHAT (artifacts, gates, firewall) is defined by `construction/dual-agent-tdd.md` and `common/dual-agent-separation.md`. After this skill, run `common/skill-artifact-adapter.md`.

**Announce at start:** "Running **Dual-Agent TDD** for unit `{unit-name}`."

## Rules to load first

1. `common/dual-agent-separation.md` — firewall, packets, RED/GREEN evidence, Sub-agent dispatch rules
2. `construction/dual-agent-tdd.md` — stage steps, approval gates, completion message

Do not write tests or production code in the Orchestrator (this) session.

## Manual vs automatic

**Manual (wait for the user):**

- Skill selection (Step 0)
- Dual-Agent plan and packet approval (Part 1)
- Stop if RED tests are already green, or Tester/Builder report blockers after 3 Builder cycles
- Stage completion: Request Changes or Continue to Next Stage

**Automatic (do not ask the user to open chats or run tests):**

- Dispatch Tester Task → Orchestrator runs suite → `red-evidence.md`
- Dispatch Builder Task → Orchestrator runs suite → `green-evidence.md`
- Optional addendum re-dispatch
- Code Reviewer after GREEN (user still picks How to Proceed on findings)

## Dispatch UX (HOW) — same pattern as `aidlc-tdd`

1. Complete Part 1 of `construction/dual-agent-tdd.md`. Wait for plan approval.
2. Dispatch `tester` as a `generalPurpose` Task. Prompt body = `tester-launch-prompt.md` (allowlist only). Do not attach `src/` or `builder-packet.md`.
3. On Tester return: verify files touched vs firewall-manifest. Run the suite. Write `red-evidence.md`. If new tests are already green, **stop and ask the user**.
4. Dispatch `builder` as a `generalPurpose` Task. Prompt body = `builder-launch-prompt.md`. Do not change Tester assertions.
5. On Builder return: run the suite. Write `green-evidence.md`. On failure, re-dispatch Builder (maximum 3 cycles), then escalate to the user.
6. Optional addendum, PR size, Code Reviewer, 2-option completion message.

Print after Tester: `[dual-agent-tdd] [{unit}] Tester Task complete — RED evidence recorded.`
Print after Builder: `[dual-agent-tdd] [{unit}] Builder Task complete — GREEN evidence recorded.`

## Sub-agent dispatch rules

Follow `common/dual-agent-separation.md` **Sub-agent dispatch rules** verbatim. Every `tester` and `builder` dispatch **must** be a `generalPurpose` Task. Each prompt must include: role, packet paths, allowlist/denylist (Tester), write paths, discovered test command, and return PASS/FAIL, artifacts touched, and blockers.

## Horizontal slicing

Batching the Tester suite for one unit is allowed only because the Tester is firewalled. Do not use this skill to write tests and production code in the Orchestrator session.

## When NOT to use this skill

- User did not opt into Dual-Agent TDD — use `construction/tdd-code-generation.md` (default) or `aidlc-tdd`
- User wants Standard code-then-tests — `construction/code-generation.md`
