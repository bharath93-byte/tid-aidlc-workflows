---
name: generate-system-prompts
description: Compresses verbose human-readable documents into dense, token-efficient XML system prompts and saves them to the aidlc-docs directory. Supports general text compression and ADR compression mode (adr_decisions.xml). Use when asked to run /generate-system-prompts or when chained from aidlc-init after aidlc-adr.
---
# Generate System Prompts Skill

When the user invokes `/generate-system-prompts`, detect which mode applies:

- **ADR mode** — input is `EPIC_DIR/adr.md` (or chained from `aidlc-init` / `aidlc-adr` after Gate 2). Follow [ADR Compression Mode](#adr-compression-mode) below.
- **General mode** — user provides a block of text. Follow [General Compression Mode](#general-compression-mode) below.

---

## ADR Compression Mode

**Trigger:** chained from `aidlc-init` after ADR, invoked by `aidlc-adr` Step 8b, or user runs `/generate-system-prompts` with `EPIC_DIR/adr.md` as input.

### Step A1: Resolve EPIC_DIR

Use `EPIC_DIR` from state-loader if available. Otherwise derive from the `adr.md` path or ask the user once.

### Step A2: Read source documents

1. Read `{EPIC_DIR}/adr.md` (required).
2. Optionally cross-check `{EPIC_DIR}/vision.md` for consistency.

### Step A3: Compress ADRs to XML

Transform each ADR (`ADR-001`, `ADR-002`, …) into dense XML. Strictly follow these rules:

1. **Remove conversational prose** — keep only decision-critical facts.
2. **Preserve technical accuracy** — do not drop constraints, thresholds, component names, or failure modes.
3. **One `<adr>` node per decision** with `id` and `status` attributes.

Write to `{EPIC_DIR}/system-prompts/adr_decisions.xml` using this structure:

```xml
<architecture_decisions source="aidlc-adr" adr_ref="adr.md">
  <adr id="ADR-001" status="Proposed">
    <title>...</title>
    <decision>...</decision>
    <rationale>...</rationale>
    <consequences>...</consequences>
    <alternatives_rejected>...</alternatives_rejected>
  </adr>
  <gaps_and_risks>...</gaps_and_risks>
</architecture_decisions>
```

### Step A4: Patch context.xml cross-reference

Patch `{EPIC_DIR}/system-prompts/context.xml`:

- If `context.xml` exists, add or update a `<cross_references>` block:
  ```xml
  <cross_references>
    <adr_decisions>system-prompts/adr_decisions.xml</adr_decisions>
  </cross_references>
  ```
- Do **not** regenerate the full `context.xml` — only append or update the cross-reference block.
- If `context.xml` does not exist, create a minimal file containing only the `<cross_references>` block.

### Step A5: Completion output

List files created or updated: `adr_decisions.xml` and `context.xml` (patched). Do not print the full XML in chat.

---

## General Compression Mode

When the user invokes `/generate-system-prompts` and provides a block of text, act as an Expert Prompt Engineer and perform the following steps exactly in order.

### Step 1: Text Compression & XML Formatting
Analyze the provided text and compress it into a dense, token-efficient format optimized for Large Language Models. 
Strictly follow these compression rules:
1. **Remove all conversational prose:** Strip out filler words, human explanations, and narrative flow. 
2. **Use XML Tags:** Organize the content into logical, well-named XML blocks (e.g., `<domain_context>`, `<functional_scope>`, `<constraints>`, `<signals>`, `<actions>`, `<decisions>`). 
3. **Use Dense Structures:** Inside the XML tags, use Markdown bullet points and key-value pairs (e.g., `key: value`).
4. **Preserve Technical Accuracy:** Do not summarize away critical technical constraints, numbers, API endpoints, latency budgets, or business logic. 
5. **Identify Gaps:** Always include an `<out_of_scope>` or `<negative_constraints>` tag if you detect things the system should explicitly *not* do.

### Step 2: Determine Context Name
Determine a short, hyphenated context name for the current chat based on the topic of the text (e.g., `iam-rate-limiting`, `auth-middleware`). If it is ambiguous, briefly ask the user what the context name should be before generating the files.

### Step 3: File Generation
Instead of just printing the XML to the chat, you must automatically create the required XML files in the workspace.
1. If this is for a pipeline epic, write under `aidlc-docs/<epic-name>_<epic-id>/system-prompts/`. Otherwise create `aidlc-docs/{context_name}/system-prompts/` for standalone compression.
2. Write the compressed XML content into one or more `.xml` files inside that directory (e.g., `aidlc-docs/rate-limiting_IAM-123/system-prompts/core_constraints.xml`). 
3. If the provided text is massively long and covers distinctly different domains, split the output into multiple logically named XML files (e.g., `adr_decisions.xml`, `traffic_profile.xml`).

### Step 4: Completion Output
Once the files are written, output a brief success message listing the files created and a 1-2 sentence summary of what was compressed. Do not output the full XML in the chat to save space.
