---
name: aidlc-review-guidelines-from-prs
description: >-
  Derives reusable review and coding guidelines from a repo's merged-PR review comments —
  for use in later code review and development, not rules about PRs themselves. Standalone
  AIDLC skill: fetches PR inline comments, clusters recurring reviewer feedback
  (sentence-transformers + HDBSCAN), then synthesizes each theme into
  collective-feedback-guidelines.md. Repo-agnostic. Auto-wires into aidlc-gacr/guidelines/
  when GACR is present and the file is missing; otherwise writes to review-guidelines/. Use
  when the user says "aidlc-review-guidelines-from-prs", wants to learn a team's review
  standards from PR history, or distill recurring PR feedback into coding guidelines.
disable-model-invocation: true
metadata:
  author: vselva1
  version: "1.6"
---

# aidlc-review-guidelines-from-prs

**Derive review & coding guidelines from PR review comments.** Fetches what reviewers keep
saying on merged PRs, clusters the recurring feedback, and synthesizes it into a reusable
**collective-feedback guidelines** document (used for later review and development — these
are coding standards distilled *from* PRs, not rules *about* PRs). 3-stage pipeline:

1. **Fetch** — `scripts/export_feedback.py` pulls slim inline review comments from merged
   PRs → `feedback-corpus.json`.
2. **Embed + cluster** — `scripts/cluster_feedback.py` encodes every comment with
   `sentence-transformers` (`all-MiniLM-L6-v2`) and groups them into recurring themes with
   HDBSCAN → `feedback-clusters.json` + `clusters-digest.txt`. (Theme count varies with the
   repo — could be a handful or 100+.)
3. **Synthesize (LLM)** — you, acting as a Staff Engineer, distill each theme into one
   definitive guideline → `collective-feedback-guidelines.md` (path resolved in Step 1b).

**Standalone.** This skill runs end-to-end on its own — it does **not** require `aidlc-gacr`,
`aidlc-init`, `state-loader`, or any other AIDLC skill.

**GACR wiring (automatic, optional).** When `.cursor/skills/aidlc-gacr/` exists in the
workspace **and** `aidlc-gacr/guidelines/collective-feedback-guidelines.md` is **missing**,
outputs are placed where GACR already expects them (`references/` + `guidelines/`). If GACR
is absent, or the guidelines file already exists, outputs go under `./review-guidelines/` unless
the user asks to refresh the GACR copy.

This skill is also **repo-agnostic** — run it inside any repo; the target repo is asked for
explicitly (it need not be the checked-out repo).

**Announce at start:** "Running **aidlc-review-guidelines-from-prs** — deriving review guidelines from PR comments."

`<skill_path>` below = the directory containing this `SKILL.md`.

## Requirements

- `python3` and `gh` (GitHub CLI, authenticated via `gh auth login` or `GITHUB_TOKEN`).
- Python deps from `scripts/requirements.txt` (installed into a venv in Step 2).
- Network access for `gh` and, on first run, the ~90MB embedding-model download.

## Output layout (resolved in Step 1b)

**Mode A — GACR wired** (`aidlc-gacr` present, guidelines file missing):

```
.cursor/skills/aidlc-gacr/
├── references/
│   ├── feedback-corpus.json
│   ├── feedback-clusters.json
│   ├── clusters-digest.txt
│   └── parts/                         # resumable fetch cache
└── guidelines/
    └── collective-feedback-guidelines.md   # deliverable
```

**Mode B — standalone** (`aidlc-gacr` absent, or guidelines already exist):

```
review-guidelines/
├── feedback-corpus.json
├── feedback-clusters.json
├── clusters-digest.txt
├── parts/
└── collective-feedback-guidelines.md       # deliverable
```

---

## Step 1 — Ask for the target repo (always, explicitly)

**Never assume the repo.** Ask the user which repo to analyze, offering:

> *"Which repo should I distill review guidelines from? Reply `iam` (default:
> `Trimble-Cloud-Core-Platform/iam`), `this` to use the current checked-out repo, or paste
> any `owner/name`."*

Resolve `REPO`:

- `iam` **or** `Trimble-Cloud-Core-Platform/iam` → use the default
  `Trimble-Cloud-Core-Platform/iam` (this is `DEFAULT_REPO` in `export_feedback.py`).
- `this` / current repo → derive from `git config --get remote.origin.url` and normalize to
  `owner/name` (strip `git@github.com:`, `https://github.com/`, trailing `.git`). Confirm it
  back to the user.
- Anything else → treat it as an explicit `owner/name` (validate it contains a single `/`).

Optionally ask for scope (defaults are fine): `--since YYYY-MM-DD`, `--limit N` for a quick
trial run. Confirm `REPO` before proceeding.

### Step 1b — Resolve output paths (automatic)

From the workspace root, check:

- `GACR_DIR` = `.cursor/skills/aidlc-gacr/` (must exist and contain `SKILL.md`)
- `GACR_GUIDELINES` = `GACR_DIR/guidelines/collective-feedback-guidelines.md`

| Condition | `OUT_DIR` (corpus + clusters) | `GUIDELINES_PATH` (deliverable) |
|-----------|--------------------------------|----------------------------------|
| `GACR_DIR` exists **and** `GACR_GUIDELINES` **missing** | `GACR_DIR/references/` | `GACR_GUIDELINES` |
| otherwise | `./review-guidelines/` | `./review-guidelines/collective-feedback-guidelines.md` |

Create `OUT_DIR` and the parent of `GUIDELINES_PATH` if needed.

Announce which mode was chosen, e.g. *"GACR wiring: outputs → aidlc-gacr/references + guidelines
(collective-feedback-guidelines.md missing)."* or *"Standalone: outputs → review-guidelines/."*

If `GACR_GUIDELINES` **already exists** and the user wants to refresh it in place, they can
say so — then set `OUT_DIR` and `GUIDELINES_PATH` to the GACR locations above even though the
file exists.

---

## Step 2 — Set up the Python environment

Create an isolated venv beside the skill and install deps (idempotent — reuse if present):

```bash
python3 -m venv <skill_path>/.venv
<skill_path>/.venv/bin/pip install -q -r <skill_path>/scripts/requirements.txt
```

Use `<skill_path>/.venv/bin/python` for all script runs below. Point the model cache at a
writable location to avoid `~/.cache` permission issues:

```bash
export HF_HOME="<skill_path>/.venv/hf_cache"
```

---

## Step 3 — Fetch PR review comments (stage 1)

```bash
gh auth status   # confirm authentication first
<skill_path>/.venv/bin/python <skill_path>/scripts/export_feedback.py \
  --repo "<REPO>" --out-dir "<OUT_DIR>" [--since <DATE>] [--limit <N>]
```

This writes `<OUT_DIR>/feedback-corpus.json` (and caches per-PR JSON under
`<OUT_DIR>/parts/`, so a re-run resumes rather than refetching). Large repos take a while —
run it in the background and report progress. Report the PR/comment counts when done.

---

## Step 4 — Embed + cluster into themes (stage 2)

```bash
HF_HOME="<skill_path>/.venv/hf_cache" <skill_path>/.venv/bin/python \
  <skill_path>/scripts/cluster_feedback.py \
  --corpus "<OUT_DIR>/feedback-corpus.json" \
  --clusters-out "<OUT_DIR>/feedback-clusters.json" \
  --digest-out "<OUT_DIR>/clusters-digest.txt"
```

The script filters out bot reviews / acknowledgements / very long write-ups, embeds the rest,
and clusters them. Report the number of themes found.

**Tuning (only if needed):** if it produces one giant blob or too few themes, re-run with a
smaller `--min-cluster-size` (finer) or larger (coarser). Defaults (`--min-cluster-size 6
--min-samples 2`, leaf selection) aim for many tight themes.

---

## Step 5 — Synthesize guidelines (stage 3, LLM)

Read `<OUT_DIR>/clusters-digest.txt` (and open `feedback-clusters.json` for full membership
when a theme is ambiguous). Acting as a **Staff Engineer writing the team's code-review
playbook**, distill the themes into a categorized guidelines document.

Per-theme distillation rule (apply to each cluster):
> "Read these review comments that all express the same concern. Distill their core intent
> into ONE definitive, actionable guideline (1–3 sentences, imperative voice). Don't
> reference individual PRs or people."

Then **group** related themes into categories (e.g. Logging, Error Handling, Testing,
Naming, Formatting, Security, Config, Type Hints & Docs, PR Hygiene…) and merge fragments of
the same idea. Note how often each theme recurred (from cluster `size`). Drop themes that are
pure repo-specific chatter (e.g. one-off config-value corrections) rather than reusable
guidance.

Write `GUIDELINES_PATH` using this template:

```markdown
# Collective Feedback Guidelines

Guidelines distilled from recurring reviewer feedback across merged PRs in `<REPO>`.
Built by: fetch review comments → sentence-transformers embeddings → HDBSCAN clustering
(<N> themes) → LLM synthesis. Each guideline notes how often the theme recurred.

## 1. <Category>
- **<Definitive imperative guideline>.** <One line of context if useful.> _(recurred ~<n>x)_
- ...

## 2. <Category>
- ...
```

Render the draft in chat, then write the file. Keep guidelines imperative, specific, and
deduplicated.

---

## Step 6 — Report

Summarize: `REPO`, output mode (GACR wired vs standalone), paths used, PRs/comments fetched,
themes found, categories produced, and `GUIDELINES_PATH`. Note that re-running refreshes the
corpus (resumable) and regenerates the guidelines.

---

## Notes

- **Standalone by default** when `aidlc-gacr` is not in the repo — no GACR dependency.
- **Auto GACR wiring** only when GACR is present **and** its guidelines file is missing, so
  critics can load `guidelines/collective-feedback-guidelines.md` without manual copying.
- **Repo-agnostic:** the only repo-specific input is `--repo`; output location depends on GACR
  presence as above.
- **Resumable fetch:** `parts/` under `OUT_DIR` caches per-PR JSON; delete it to force refetch.
- **First-run model download** (~90MB) is cached under `HF_HOME`.
- Do not commit `.venv/` or large corpus artifacts unless the user wants them tracked.
