---
name: aidlc-dual-agent-tdd
description: >-
  Dual-Agent TDD: Orchestrator in this chat prepares firewalled packets; user
  pastes Tester then Builder prompts into new unlinked Cursor Agent chats so
  tests are written without seeing implementation. Use when the user says
  Dual-Agent TDD, Builder vs Tester, or wants a test-author firewall.
---

# AIDLC Dual-Agent TDD

**Announce at start:** "Running **aidlc-dual-agent-tdd** for `{unit or story}`."

This skill is the Cursor HOW layer for Dual-Agent TDD. Load and follow:

1. `common/dual-agent-separation.md` (under the resolved `aws-aidlc-rule-details/` directory)
2. `construction/dual-agent-tdd.md` for stage gates and contract artifacts

If those rule files are not in the workspace, stop and tell the user Dual-Agent TDD requires AI-DLC rules. Do not invent a weaker firewall.

## Cursor launch (mandatory)

Do **not** dispatch Tester or Builder as Task sub-agents from this chat. Sub-agents can still read `src/`.

**Tester**

```text
Open a new Agent chat (Composer/Agent), not this thread.
Paste the full contents of:
aidlc-docs/construction/{unit-name}/dual-agent/tester-launch-prompt.md
Do not @-mention src, app, lib, or builder-packet.md.
Do not use codebase search against production source.
When finished, come back to the Orchestrator chat and say: Tester session is done.
```

**Builder** (only after Orchestrator records RED)

```text
Open a new Agent chat (Composer/Agent), not this thread.
Paste the full contents of:
aidlc-docs/construction/{unit-name}/dual-agent/builder-launch-prompt.md
Do not edit Tester assertions or skip tests to get green.
When the suite is green (or a test is invalid and you must escalate), come back and say: Builder session is done.
```

## Orchestrator duties in this chat

- Write packets and launch prompts per `construction/dual-agent-tdd.md`
- Wait for the user after each launch
- Run the suite; write `red-evidence.md` / `green-evidence.md`
- Never write tests or production code unless the user explicitly asks this session to patch
- After GREEN: Code Reviewer, then the stage 2-option completion message

## Horizontal slicing exception

Batch RED for the unit is allowed **only** because the Tester is firewalled. `aidlc-tdd` still forbids the same agent writing all tests then all implementation.

## When NOT to use this skill

- User wants default seam-by-seam TDD in one story loop — use `aidlc-tdd`
- User wants Standard code-then-tests — AI-DLC `construction/code-generation.md`
- Cannot open a second Agent chat — use `aidlc-tdd` instead
