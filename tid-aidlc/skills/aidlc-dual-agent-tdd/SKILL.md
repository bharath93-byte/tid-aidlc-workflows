---
name: aidlc-dual-agent-tdd
description: >-
  Dual-Agent TDD: Orchestrator prepares firewalled packets then dispatches
  Tester (RED) and Builder (GREEN) as generalPurpose Task sub-agents so tests
  are written without implementation in the Tester prompt. Use when the user
  says Dual-Agent TDD, Builder vs Tester, or wants a test-author firewall.
---

# AIDLC Dual-Agent TDD

**Announce at start:** "Running **aidlc-dual-agent-tdd** for `{unit or story}`."

This skill is the Cursor HOW layer for Dual-Agent TDD. Load and follow:

1. `common/dual-agent-separation.md` (under the resolved `aws-aidlc-rule-details/` directory)
2. `construction/dual-agent-tdd.md` for stage gates and contract artifacts

If those rule files are not in the workspace, stop and tell the user Dual-Agent TDD requires AI-DLC rules. Do not invent a weaker firewall.

## Manual vs automatic

**Manual:** plan/packet approval; stop if RED tests are already green or a Task reports blockers after retries; Request Changes / Continue to Next Stage.

**Automatic:** Tester Task → Orchestrator test run (`red-evidence.md`) → Builder Task → Orchestrator test run (`green-evidence.md`). Do **not** ask the user to open a chat, paste a prompt, or run the suite.

## Dispatch (mandatory) — same pattern as `aidlc-tdd`

Do **not** write tests or production code in this Orchestrator chat.

After the user approves the Dual-Agent plan:

1. Dispatch `tester` as a `generalPurpose` Task. Pass the full body of `aidlc-docs/construction/{unit-name}/dual-agent/tester-launch-prompt.md`. Include: repo root, allowlist paths only, denylist, test write paths, discovered test command. If `{EPIC_DIR}/illustrative-example.md` exists, include its path as **expected-behavior context** (design artifact, not production source; scenario-not-spec — do not expand beyond `ears_ref`/`lld_ref`). Do **not** dump `coding-guidelines` into the Tester prompt (test-author firewall). Instruct: do not Read/Grep/Glob production source or `builder-packet.md`. Missing `illustrative-example.md` is not a firewall violation. Return PASS/FAIL, artifacts touched, test command + result, blockers.

   Print: `[aidlc-dual-agent-tdd] [{unit}] Tester Task complete.`

2. Orchestrator: verify files touched vs `firewall-manifest.md`. Run the suite. Write `red-evidence.md`. If new tests pass without new production code, stop and ask the user.

3. Dispatch `builder` as a `generalPurpose` Task. Pass `builder-launch-prompt.md` plus the Tester test file list. Instruct: do not edit Tester assertions. **Read `.cursor/skills/coding-guidelines/SKILL.md` first** as a hard constraint. If `{EPIC_DIR}/illustrative-example.md` exists, include its path (scenario-not-spec: implement only `ears_ref`/`lld_ref`). Return PASS/FAIL, artifacts touched, test command + result, blockers.

   Print: `[aidlc-dual-agent-tdd] [{unit}] Builder Task complete.`

4. Orchestrator: run the suite. Write `green-evidence.md`. On failure, re-dispatch Builder (maximum 3 cycles), then escalate to the user.

## Sub-agent dispatch rules

Every `tester` and `builder` dispatch **must** be a `generalPurpose` Task sub-agent for context isolation (same rule as `aidlc-tdd` implementer / test-auditor). Each prompt must include: repo root + branch, packet paths, allowlist/denylist (Tester), write paths, discovered build/test commands, and an instruction to return PASS/FAIL, artifacts touched, and blockers. **Builder** prompts also list `.cursor/skills/coding-guidelines/SKILL.md` and `{EPIC_DIR}/illustrative-example.md` when present. **Tester** prompts may list the illustrative example as behavior context only — not the production style guide.

Discover build/test/lint commands the same way as `aidlc-tdd` (README → package.json → Makefile → language manifests → CI).

## Horizontal slicing exception

Batch RED for the unit is allowed **only** because the Tester is firewalled. `aidlc-tdd` still forbids the same agent writing all tests then all implementation.

## When NOT to use this skill

- User wants default seam-by-seam TDD in one story loop — use `aidlc-tdd`
- User wants Standard code-then-tests — AI-DLC `construction/code-generation.md`
