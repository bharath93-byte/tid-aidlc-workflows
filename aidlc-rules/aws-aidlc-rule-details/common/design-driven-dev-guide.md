# Design-Driven Development Guide (EARS / HLD / LLD)

**Correct flow (Global Spec-First)**:

```
HLD  →  LLD(s)  →  EARS  →  Story Breakdown  →  Tests (TDD)  →  Code
```

Mapped onto AI-DLC stages:

| Flow step | AI-DLC stage | Artifact |
|-----------|-------------|----------|
| HLD | Application Design | `aidlc-docs/inception/application-design/hld.md` |
| LLD | Application Design (same stage, after HLD) | `aidlc-docs/inception/application-design/lld/{component}.md` |
| EARS | Application Design (same stage, after LLD) | `aidlc-docs/inception/requirements/ears/{feature}-{subfeature}-ears.md` |
| Story Breakdown | Units Generation | `aidlc-docs/inception/application-design/unit-of-work.md` (EARS Coverage + user-story framing per unit), `personas.md` (conditional) |
| Tests (TDD) | Code Generation / TDD Code Generation (per unit) | `@spec`-annotated tests |
| Code | Code Generation / TDD Code Generation (per unit) | `@spec`-annotated production code |

**Why this order**: HLD fixes *what and why* at the project level first. LLD then fixes *how* per component while the HLD is still fresh context — this is the cheapest point to catch architectural mistakes, before a single testable requirement is written. EARS is then derived from decisions already locked in the LLD (never invented independently), so every requirement is traceable to a design decision. Story Breakdown slices approved EARS into PR-sized units. Tests/Code implement one unit at a time, citing the EARS ID(s) they satisfy.

**No separate "User Stories" stage**: there is no early, EARS-less stage that authors prose user stories before design exists. Slicing stories at the HLD stage — before interfaces, schemas, and state contracts are locked down — lets independent story slices invent conflicting assumptions (e.g. one slice's API expects `user_id`, another `identity_id`) and produces vague, unbounded prose stories that invite hallucination during Construction. It also thrashes the prompt-cache prefix: a static, once-compiled system-spec prefix (HLD+LLD+EARS) enables ~90% cache-hit token savings on every downstream call, which per-story LLD/EARS regeneration would erase. Instead, personas and user-story framing are produced in **Units Generation (Story Breakdown)**, Step 2.1 (`inception/units-generation.md`) — after EARS exists — so each unit's story is bounded by concrete `WHEN`/`WHILE`/`IF...THEN` clauses rather than free-text guesswork, and only generated when personas add real value (multi-persona system, customer-facing feature, cross-team alignment) — see `units-generation.md` Step 2.1 for the gate.

**Refinement, not re-derivation, later in Construction**: Functional Design / NFR Requirements / NFR Design / Infrastructure Design (per-unit, Construction phase) still run as before, but they **refine the existing component LLD in place** rather than authoring a new design from scratch — the component's business logic, NFR targets, and infrastructure mapping were already sketched in Application Design; Construction fills in unit-level specifics the earlier, coarser LLD couldn't know yet (see `construction/infrastructure-design.md` Step 6.1).

## Arrow of Intent

The chain `HLD → LLD → EARS → Story Breakdown → Tests → Code` must stay coherent. **Coherence over history**: when one level changes, review and update every downstream level to match — mutate in place, delete what's wrong, never let stale and current content coexist.

**Cascading changes**: HLD change → review affected LLD(s) → review their EARS → review affected stories → review affected tests. LLD change → review its EARS → stories → tests. EARS change → review affected stories → tests, and re-flip any status markers no longer supported by a passing test.

## Templates

- [hld-template.md](./hld-template.md)
- [lld-template.md](./lld-template.md)
- [ears-syntax.md](./ears-syntax.md)
- [story-breakdown-template.md](./story-breakdown-template.md)

## Token-Efficiency Notes

- Depth-adaptive: at **Minimal** depth (see `depth-levels.md`), a single component may get one LLD and one EARS file with a handful of statements — don't force multi-file decomposition on small changes.
- Never restate a template's structure inline in a stage rule file — link to the template and follow it. This guide and the four templates above are the **single source** for structure; stage files only state *when* to produce each artifact and *what context* to ground it in.
- LLD/EARS are refined in place across stages, not regenerated — Construction-phase stages read and edit the existing files rather than creating parallel ones.
