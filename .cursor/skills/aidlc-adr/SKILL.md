---
name: aidlc-adr
description: AIDLC ADR authoring skill. Activates on '/aidlc-adr', "generate an ADR", "write architecture decision records", "turn this vision doc into ADRs", or "author an ADR document". Generates a single consolidated Architecture Decision Record (ADR) document from an aidlc-vision / aidlc-vision-doc vision.md, grounded against docs/architecture/SYSTEM_ARCHITECTURE.md. Writes to EPIC_DIR/adr.md, compresses to system-prompts/adr_decisions.xml, and advances status to adr-completed. Two approval gates. Nothing is written to EPIC_DIR until Gate 2 passes.
disable-model-invocation: true
---

# AIDLC ADR

Self-contained. Generates a single consolidated ADR document (multiple
Architecture Decision Records, one file) grounded in an
`aidlc-vision`/`aidlc-vision-doc` vision.md and in the repository's system
architecture. Combines two mechanics:

- **platform-designer synthesis**: one ADR per key decision, each with
  Context → Decision → Rationale → Consequences → Alternatives Considered.
- **scoped-questioning gap-filling**: one question at a time, ranked by
  decision risk, 2-3 trade-off options with an evidence-based recommendation
  — used only for decisions the vision doc left open.

Two approval gates, matching `aidlc-vision`. **Nothing is written to disk
before Gate 2.**

---

## Step 0: Load pipeline state (state-loader)

Before anything else, if it hasn't already run in this session, invoke the **state-loader** skill to load `pipeline-config.json` and the epic's `state.json`. Use the resolved `EPIC_DIR`.

**Prerequisite:** `status` must be `inception-completed` to start a new ADR run. Allow re-run at `adr-completed` for ADR revisions only. If `status` is earlier than `inception-completed`, stop and tell the user to complete `aidlc-vision-doc` first.

---

## Step 1: Locate the vision doc

Ask, if not already provided in the conversation:

> "Which vision doc should I use? Provide the epic key/directory (e.g. `IAM-123` under `aidlc-docs/`) or a path."

Resolution order:

1. If `EPIC_DIR` is known from state-loader, prefer `{EPIC_DIR}/vision.md`.
2. If the user gave a path, read it directly.
3. Otherwise, search `aidlc-docs/*/vision.md` — this is the shared output
   location of both `aidlc-vision` (full Jira/manual workflow) and
   `aidlc-vision-doc` (standalone generator from a loaded context block). If
   exactly one match exists, confirm it. If multiple, list them and ask
   which one.
4. If none found, ask the user to paste the vision content directly, or run
   `aidlc-vision` / `aidlc-vision-doc` first.

Set `VISION_SOURCE` (path) and `FEATURE_SLUG` (derived from the vision doc's
parent directory name, or its title if pasted).

---

## Step 2: Load repository architecture context

Read `docs/architecture/SYSTEM_ARCHITECTURE.md` if it exists. Extract
whatever is relevant to the vision doc's `Functional Scope`, `Data`, and
`Integrations` sections:

- **Technology Stack** and **Key Design Patterns** — so ADRs align with
  established repo conventions instead of proposing an alternative that
  already conflicts with the current stack.
- **Container Architecture** / **AWS Infrastructure** — deployment
  topology, regions, gateways, and existing tables, so a decision does not
  contradict infrastructure that already exists.
- **Database Architecture** — existing table/key schemas, so a new data
  model decision states plainly whether it reuses or deliberately avoids
  reusing an existing table.
- **Observability** — existing structured logging field names and
  conventions, so any ADR touching logging/metrics uses names consistent
  with what the codebase already emits.

If `docs/architecture/SYSTEM_ARCHITECTURE.md` does not exist, note this in
the eventual ADR document's Gaps and Risks table (Step 6) rather than
skipping architecture grounding silently — architecture context may still
come from direct repo inspection if the user asks for it.

Any conflict between the vision doc and the architecture document (for
example, a claim about deployed regions, or a claim about an existing
component's behavior) MUST be flagged before Step 5 (Gate 1) — surface it as
a discovered discrepancy, and resolve it with scoped-questioning (Step 4) if
it affects a decision, or as an explicit note in the relevant ADR's Context
if it does not change the decision itself.

Set `ARCH_SOURCE` to the path used (or "not found").

---

## Step 3: Extract decision points from the vision doc

Read the vision doc's `Functional Scope`, `Data`, `Integrations`, and
`Constraints` sections (per the canonical `vision-template.md` structure
used by `aidlc-vision-doc`). Extract every implied **technical decision** —
a fork where the vision doc picked, or needs to pick, one design out of
several plausible ones. Cross-check each against `ARCH_SOURCE` from Step 2
so the decision's Context/Rationale can cite actual repo architecture
instead of a generic justification.

Typical decision categories to check for (not exhaustive — derive from what
the vision doc actually discusses; do not force a category that has no
grounding in the source material):

| Category | Look for |
|---|---|
| Storage / persistence choice | Which datastore, and why not alternatives; cross-check against existing tables in `ARCH_SOURCE`'s Database Architecture |
| Algorithm / mechanism choice | e.g. sliding window vs. fixed window vs. token bucket |
| Key / schema design | Composite keys, partitioning, sharding |
| Threshold / config model | Global vs. per-tenant vs. per-region configuration |
| Enforcement layer | Where in the stack a check or decision is enforced; cross-check against `ARCH_SOURCE`'s Container Architecture (gateways, middleware, authorizer layers) |
| Failure mode | Fail open vs. fail closed |
| Rollout strategy | Shadow mode, phased rollout, feature flag |
| Response / error contract | Status codes, headers, error shape; cross-check against `ARCH_SOURCE`'s existing API error format if documented |

For each candidate decision, classify it as:

- **Settled** — the vision doc states a clear choice. Cite the section.
- **Implied but unqualified** — the vision doc hints at a choice without
  rationale or alternatives. Needs a lightweight ADR; no question required.
- **Open** — the vision doc has an explicit open question on this topic, or
  no coverage at all. Needs scoped-questioning (Step 4).

---

## Step 4: Scoped-questioning for open decisions

For every **Open** decision from Step 3, apply the mechanics from
`tp-ai-kit-scoped-questioning` when that skill is available. Do not invoke
it as a separate workflow; this skill remains self-contained, mirroring how
`aidlc-vision` and `aidlc-context-loader` apply the same mechanics inline:

1. Rank open decisions by decision risk (blast radius if the wrong default
   is chosen); start with the highest-risk one.
2. Check the vision doc's own `Open Questions` / `Assumptions` sections,
   `ARCH_SOURCE` (Step 2), and any linked ADRs first. Do not ask the user
   what existing material already answers.
3. Ask one focused question at a time, in this format:

```
Decision: <name> — Open

<Focused question about the gap>

Options:
- Option A: <most repo/vision-aligned choice>. <trade-off>
- Option B: <alternative>. <trade-off>
- Option C: I'll describe it myself

Recommendation: Option A — <evidence-based reason>.
```

4. Record the answer, update `FEATURE_SLUG` context if relevant, and move to
   the next unresolved decision.
5. If the user says "skip", "enough", or "proceed" early, do not guess.
   Mark each remaining open decision `Status: Proposed (unresolved — needs
   review)` in the ADR and list it under Gaps and Risks (Step 6).

Do not expand scoped-questioning beyond the decisions identified in Step 3 —
this skill drafts ADRs from an existing vision, not a new requirements
gathering pass.

---

## Step 5: Gate 1 — Decision scorecard approval

Present:

```
## ADR Decision Scorecard — <FEATURE_SLUG>

| # | Decision | Status | Source |
|---|----------|--------|--------|
| 1 | <decision> | Settled / Resolved via questioning / Unresolved | <vision.md section, ARCH_SOURCE section, or Q&A> |

Vision doc: <VISION_SOURCE>
Architecture doc: <ARCH_SOURCE>
```

Say: *"Review the scorecard. Say **'approved'**, **'looks good'**, or **'finalized'** to draft the ADR document — or tell me what to add, remove, or re-open."*

**Do not proceed to Step 6 until the user explicitly approves.**

---

## Step 6: Generate ADR document draft in chat

Use the template at
[templates/adr-template.md](templates/adr-template.md) as structure.

For each decision from the approved scorecard, write one ADR section with:
`Status` (`Proposed` for all new decisions; `Superseded` only when the user
confirms this replaces an existing ADR), `Context`, `Decision`,
`Rationale`, `Consequences`, and `Alternatives Considered` (at least two
options — even for Settled decisions, pull alternatives from the vision
doc's Non-Goals or rejected-approach language where present. Do not omit
this section even when only one realistic option exists — state that no
credible alternative was identified, and why).

- Number ADRs sequentially (`ADR-001`, `ADR-002`, ...).
- Build the `Index` table linking every ADR by anchor. The anchor slug MUST
  match the GitHub-style markdown heading anchor for the ADR title
  (lowercase, spaces to hyphens, punctuation stripped) so the links resolve.
- Ground each `Context` and `Rationale` in `ARCH_SOURCE` where relevant —
  cite the actual component, table, or pattern name from
  `docs/architecture/SYSTEM_ARCHITECTURE.md` rather than a generic
  statement (for example, "reuses the existing `iam-gateway` REGIONAL
  endpoint with blue/green stages" instead of "uses the API gateway").
- Add a `Phased Implementation Plan` table if the vision doc has a
  phase/rollout section (Functional Scope rollout sequence, or a `Phase`
  column in Personas/Data).
- Add a `Gaps and Risks` table listing every decision marked unresolved in
  Step 4, plus any risk the vision doc's own `Constraints`/`Assumptions`
  sections surface, plus a row noting it if `ARCH_SOURCE` was "not found" in
  Step 2.
- If this ADR document revises a prior version (the vision it is based on
  was itself revised), add a `> **Revision note:** ...` blockquote
  immediately under the affected ADR's `**Status:**` line rather than
  deleting the original text, so the decision history stays visible — this
  matches how `{EPIC_DIR}/adr.md` is revised when decisions are updated.

Where context is insufficient for a section, use a clearly marked
placeholder: `_[TBD — no context provided]_`.

Render the full draft in chat. **Do NOT write any file yet.**

Say: *"Here is the ADR document draft. Review it and say **'approved'**, **'looks good'**, or **'finalized'** to write it to disk — or tell me what to change."*

---

## Step 7: Gate 2 — ADR document approval

If the user requests changes: revise the draft in chat and present again.
Repeat until the user says "approved", "looks good", or "finalized".

**Do not proceed to Step 8 until explicitly approved.**

---

## Step 8: Write to disk

1. Write the approved draft to `{EPIC_DIR}/adr.md`.
2. Confirm: "`{EPIC_DIR}/adr.md` written successfully."

---

## Step 8b: Compress ADR to system prompts

Invoke the **generate-system-prompts** skill in **ADR compression mode** (or apply its ADR Compression Mode steps inline):

1. Read `{EPIC_DIR}/adr.md`.
2. Write `{EPIC_DIR}/system-prompts/adr_decisions.xml`.
3. Patch `{EPIC_DIR}/system-prompts/context.xml` with the `<cross_references>` block pointing to `adr_decisions.xml`.

Do not proceed to Step 8c until `adr_decisions.xml` exists.

---

## Step 8c: Advance pipeline state

1. Update `{EPIC_DIR}/state.json`: set `"status": "adr-completed"`.
2. Append a row to `{EPIC_DIR}/audit.md`:
   - Phase: `adr`
   - Skill/Agent: `aidlc-adr`
   - Action: `ADR approved; adr.md and adr_decisions.xml written; status advanced to adr-completed.`
   - Approver: current system username

---

## Step 9: Final summary

| # | Step | Status |
|---|------|--------|
| 0 | Pipeline state loaded; EPIC_DIR resolved | ✓ |
| 1 | Vision doc located (`<VISION_SOURCE>`) | ✓ |
| 2 | Architecture context loaded (`<ARCH_SOURCE>`) | ✓ |
| 3 | Decision points extracted from vision doc | ✓ |
| 4 | Open decisions resolved via scoped-questioning | ✓ |
| 5 | Gate 1: Decision scorecard approved | ✓ |
| 6 | ADR document draft generated in chat | ✓ |
| 7 | Gate 2: ADR document approved | ✓ |
| 8 | ADR written to `{EPIC_DIR}/adr.md` | ✓ |
| 8b | `adr_decisions.xml` written; `context.xml` patched | ✓ |
| 8c | `state.json` advanced to `adr-completed` | ✓ |

---

## Notes

- **Nothing is written to disk before Gate 2.** Non-negotiable, matching
  `aidlc-vision`.
- **Gate trigger phrases:** "approved" / "looks good" / "finalized"
  (case-insensitive).
- **Mechanics sources:** the ADR synthesis shape (`Context → Decision →
  Rationale → Consequences → Alternatives Considered`, `Index` table,
  `Phased Implementation Plan`, `Gaps and Risks` table) follows
  `tp-ai-kit-platform-designer`'s ADR output shape. The gap-filling loop
  follows `tp-ai-kit-scoped-questioning`'s mechanics, applied inline the
  same way `aidlc-vision` and `aidlc-context-loader` apply them.
- **Vision doc inputs:** accepts output from either `aidlc-vision` (full
  Jira/manual workflow with completeness scoring) or `aidlc-vision-doc`
  (standalone generator from a loaded context block) — both write to
  `aidlc-docs/<epic-name>_<epic-id>/vision.md`.
- **Architecture doc input:** `docs/architecture/SYSTEM_ARCHITECTURE.md`
  (Step 2) grounds every ADR's Context/Rationale in the repo's actual tech
  stack, infrastructure, data model, and observability conventions, so
  decisions don't contradict what already exists.
- **Style reference** for consolidated ADR document shape:
  `aidlc-docs/rate-limiting_IAM-123/adr.md` (epic-local) or
  `docs/architecture/decisions/001-graph-in-dynamodb.md` (repo ADR format).
- **Sub-skill relationship:** standalone, atomic skill in the `aidlc-*`
  family alongside `aidlc-vision`, `aidlc-vision-doc`, and
  `aidlc-context-loader`. Chains `generate-system-prompts` (ADR mode) after
  Gate 2. Expects `vision.md` at `{EPIC_DIR}/vision.md` as input.
