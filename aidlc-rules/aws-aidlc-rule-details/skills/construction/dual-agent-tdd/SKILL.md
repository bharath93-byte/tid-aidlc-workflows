---
name: dual-agent-tdd
description: >-
  Dual-Agent TDD for Code Generation: Orchestrator prepares firewalled packets;
  a Tester session writes black-box tests (RED) with zero implementation
  visibility; a Builder session implements until green without editing tests.
  Use when the user requests Dual-Agent TDD, Builder vs Tester, or a test
  author firewall.
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
requires_agents: false
security_reviewed: false
last_reviewed: "2026-08-18"
skill_card: ./SKILL_CARD.md
---

# Dual-Agent TDD

> **Trigger**: "Dual-Agent TDD", "Builder vs Tester", "firewalled tests", "unlinked tester session", or Code Generation Step 0 when this skill is selected
>
> **Purpose**: HOW to launch unlinked Tester and Builder sessions. WHAT (artifacts, gates, firewall) is defined by `construction/dual-agent-tdd.md` and `common/dual-agent-separation.md`. After this skill, run `common/skill-artifact-adapter.md`.

**Announce at start:** "Running **Dual-Agent TDD** for unit `{unit-name}`."

## Rules to load first

1. `common/dual-agent-separation.md` — firewall, packets, RED/GREEN evidence
2. `construction/dual-agent-tdd.md` — stage steps, approval gates, completion message

Do not write tests or production code in the Orchestrator (this) session.

## Launch UX (HOW)

1. Complete Part 1 of `construction/dual-agent-tdd.md` (plan, packets, launch prompts).
2. Show the user the Tester prompt path and this instruction:

```text
Open a NEW agent session (do not continue this chat).
Paste the contents of aidlc-docs/construction/{unit-name}/dual-agent/tester-launch-prompt.md.
Do not @-mention or attach production source, src/, or builder-packet.md.
When tests are written, return here and say Tester session is done.
```

3. Wait for confirmation. Run RED evidence per the stage rule. Do not start Builder if new tests are already green.
4. Show the Builder instruction:

```text
Open a NEW agent session (do not continue this chat).
Paste the contents of aidlc-docs/construction/{unit-name}/dual-agent/builder-launch-prompt.md.
Do not change Tester assertions or skip tests to get green.
When the suite is green (or you must escalate an invalid test), return here and say Builder session is done.
```

5. Wait for confirmation. Run GREEN evidence, optional addendum, PR size, Code Reviewer, and the stage 2-option completion message.

## Launch prompt must include

- Role (Tester or Builder)
- Packet path and firewall-manifest path
- Allowlist / denylist
- Write paths
- Stop condition
- Instruction not to open the other role's packet

## Horizontal slicing

Batching the Tester suite for one unit is allowed only because the Tester is firewalled. Do not use this skill to write tests and production code in one session.

## When NOT to use this skill

- User did not opt into Dual-Agent TDD — use `construction/tdd-code-generation.md` (default) or `aidlc-tdd`
- User wants Standard code-then-tests — `construction/code-generation.md`
- Evaluator / unattended runs that cannot open a second session — stay on default TDD
