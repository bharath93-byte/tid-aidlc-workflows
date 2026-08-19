"""Distill recurring PR review feedback into coding guidelines.

Pipeline (matches the 3-stage design):
  1. Vector Embeddings  -> sentence-transformers (all-MiniLM-L6-v2), local & free.
  2. Clustering         -> HDBSCAN (fallback: DBSCAN) over cosine distance.
  3. LLM Synthesis      -> loop each cluster through an LLM ("Staff Engineer"
                           prompt) to distill a single definitive guideline.

The corpus is the exported PR review comments at
  .cursor/skills/aidlc-gacr/references/feedback-corpus.json

Outputs:
  - references/feedback-clusters.json : machine-readable buckets (always written)
  - guidelines/collective-feedback-guidelines.md : synthesized guidelines
        (written automatically only when an LLM backend is configured; otherwise
        the clusters file is used by an agent to synthesize the markdown)

Setup:
  python -m venv .venv && . .venv/bin/activate
  pip install -r scripts/requirements.txt

Usage:
  python scripts/cluster_feedback.py                 # embed + cluster, dump clusters.json
  OPENAI_API_KEY=... python scripts/cluster_feedback.py --synthesize   # + LLM guidelines

Note: the first run downloads the ~90MB embedding model to the HuggingFace cache.
Set HF_HOME to a writable path (e.g. HF_HOME=$PWD/.venv/hf_cache) if the default
~/.cache/huggingface is not writable.
"""

from __future__ import annotations

import argparse
import json
import os
import re
from collections import Counter
from pathlib import Path

import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

# --------------------------------------------------------------------------- #
# Paths
# --------------------------------------------------------------------------- #
SKILL_DIR = Path(__file__).resolve().parents[1]
CORPUS_PATH = SKILL_DIR / "references" / "feedback-corpus.json"
CLUSTERS_PATH = SKILL_DIR / "references" / "feedback-clusters.json"
GUIDELINES_PATH = SKILL_DIR / "guidelines" / "collective-feedback-guidelines.md"

# --------------------------------------------------------------------------- #
# 1. Load + filter the corpus
# --------------------------------------------------------------------------- #
# Author replies / acknowledgements carry no reusable guidance. Drop them so the
# clusters describe *what reviewers ask for*, not the back-and-forth chatter.
_ACK_PATTERNS = re.compile(
    r"^\s*(thanks?|thank you|done|fixed|updated|resolved|resolving|good catch|"
    r"nice catch|lgtm|ok|okay|sure|agreed|agree|makes sense|will do|got it|"
    r"ack|acknowledged|sounds good|\+1|yep|yes|no|nope|as discussed|"
    r"addressed|changed|re-?added|removed|added)\b",
    re.IGNORECASE,
)
# Comments that are pure "?" discussion with no imperative are usually questions
# among reviewers; we still keep them because reviewers often phrase asks as
# questions ("do we need this?"). We only require a minimum signal length.
_MIN_WORDS = 5
# Long, multi-section write-ups are almost always automated reviews, not the
# crisp reviewer asks we want to distill.
_MAX_WORDS = 100
# Automated review bots (Bugbot / CodeRabbit style) emit markdown headers,
# severity badges and HTML prompt comments. Strip them: we want *human* asks.
_BOT_PATTERNS = re.compile(
    r"(<!--|^\s*#{1,6}\s|\*\*(high|medium|low|critical)\b|prompt for ai)",
    re.IGNORECASE,
)


def load_comments() -> list[dict]:
    data = json.loads(CORPUS_PATH.read_text())
    seen: set[str] = set()
    comments: list[dict] = []
    for pr in data["prs"]:
        for c in pr.get("inline", []):
            text = (c.get("text") or "").strip()
            words = len(text.split())
            if words < _MIN_WORDS or words > _MAX_WORDS:
                continue
            if _ACK_PATTERNS.match(text):
                continue
            if _BOT_PATTERNS.search(text):
                continue
            key = text.lower()
            if key in seen:
                continue
            seen.add(key)
            comments.append(
                {
                    "pr": pr.get("number"),
                    "path": c.get("path"),
                    "line": c.get("line"),
                    "text": text,
                }
            )
    return comments


# --------------------------------------------------------------------------- #
# 2. Embed + cluster
# --------------------------------------------------------------------------- #
def embed(texts: list[str]) -> np.ndarray:
    print("Generating local semantic embeddings (all-MiniLM-L6-v2)...")
    model = SentenceTransformer("all-MiniLM-L6-v2")  # ~90MB, cached after first run
    return model.encode(
        texts, batch_size=64, show_progress_bar=True, normalize_embeddings=True
    )


def cluster(embeddings: np.ndarray) -> np.ndarray:
    """Return a cluster label per row (-1 == noise)."""
    try:
        import hdbscan

        print("Clustering with HDBSCAN...")
        model = hdbscan.HDBSCAN(
            min_cluster_size=6,
            min_samples=2,
            metric="euclidean",  # embeddings are L2-normalized ~= cosine
            cluster_selection_method="leaf",  # many tight themes, not one blob
        )
        return model.fit_predict(embeddings.astype("float64"))
    except ImportError:
        from sklearn.cluster import DBSCAN

        print("HDBSCAN not available, falling back to DBSCAN...")
        distance = np.clip(1.0 - cosine_similarity(embeddings), 0, None)
        return DBSCAN(eps=0.45, min_samples=4, metric="precomputed").fit_predict(
            distance
        )


def build_clusters(comments: list[dict], labels: np.ndarray, embeddings: np.ndarray):
    """Group comments by label and pick a representative (medoid) per cluster."""
    buckets: dict[int, list[int]] = {}
    for idx, label in enumerate(labels):
        if label != -1:
            buckets.setdefault(int(label), []).append(idx)

    clusters = []
    for label, idxs in buckets.items():
        sub = embeddings[idxs]
        centroid = sub.mean(axis=0)
        # medoid == comment closest to the centroid, a good human-readable label
        medoid_local = int(np.argmax(sub @ centroid))
        medoid = idxs[medoid_local]
        paths = Counter(comments[i]["path"] for i in idxs if comments[i]["path"])
        clusters.append(
            {
                "size": len(idxs),
                "representative": comments[medoid]["text"],
                "top_paths": [p for p, _ in paths.most_common(5)],
                "comments": [comments[i]["text"] for i in idxs],
            }
        )
    clusters.sort(key=lambda c: c["size"], reverse=True)
    return clusters


# --------------------------------------------------------------------------- #
# 3. LLM synthesis
# --------------------------------------------------------------------------- #
_SYSTEM_PROMPT = (
    "You are a Staff Engineer writing your team's code-review playbook. "
    "You are given a bucket of real review comments that all express the same "
    "underlying concern. Distill their core intent into ONE definitive, "
    "actionable coding guideline (1-3 sentences, imperative voice). "
    "Do not reference individual PRs or people. Return only the guideline text."
)


def synthesize_with_llm(clusters: list[dict], max_comments: int = 40) -> list[dict]:
    from openai import OpenAI

    client = OpenAI()
    model = os.environ.get("OPENAI_MODEL", "gpt-4o-mini")
    out = []
    for i, cl in enumerate(clusters, 1):
        sample = cl["comments"][:max_comments]
        joined = "\n".join(f"- {c}" for c in sample)
        print(f"Synthesizing guideline {i}/{len(clusters)} (size={cl['size']})...")
        resp = client.chat.completions.create(
            model=model,
            temperature=0.2,
            messages=[
                {"role": "system", "content": _SYSTEM_PROMPT},
                {"role": "user", "content": f"Review comments:\n{joined}"},
            ],
        )
        out.append({**cl, "guideline": resp.choices[0].message.content.strip()})
    return out


def write_markdown(clusters: list[dict]) -> None:
    lines = [
        "# Collective Feedback Guidelines",
        "",
        "Guidelines distilled from recurring reviewer feedback across merged PRs "
        f"in `Trimble-Cloud-Core-Platform/iam`. Each guideline represents a theme "
        f"that reviewers raised repeatedly ({len(clusters)} themes).",
        "",
    ]
    for i, cl in enumerate(clusters, 1):
        lines.append(f"## {i}. {cl.get('guideline', cl['representative'])}")
        lines.append("")
        lines.append(f"_Raised {cl['size']} times._")
        if cl["top_paths"]:
            lines.append("")
            lines.append("Common areas: " + ", ".join(f"`{p}`" for p in cl["top_paths"]))
        lines.append("")
    GUIDELINES_PATH.write_text("\n".join(lines))
    print(f"Wrote {GUIDELINES_PATH}")


# --------------------------------------------------------------------------- #
# main
# --------------------------------------------------------------------------- #
def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--synthesize",
        action="store_true",
        help="Call the LLM to distill guidelines and write the markdown file.",
    )
    args = parser.parse_args()

    comments = load_comments()
    print(f"Extracted {len(comments)} actionable comments after filtering.")

    embeddings = embed([c["text"] for c in comments])
    labels = cluster(embeddings)
    clusters = build_clusters(comments, labels, embeddings)
    print(f"Found {len(clusters)} clusters (noise dropped).")

    CLUSTERS_PATH.write_text(json.dumps(clusters, indent=2))
    print(f"Wrote {CLUSTERS_PATH}")

    if args.synthesize:
        clusters = synthesize_with_llm(clusters)
        CLUSTERS_PATH.write_text(json.dumps(clusters, indent=2))
        write_markdown(clusters)
    else:
        print(
            "\nClusters written. Run with --synthesize (and OPENAI_API_KEY set) "
            "to generate guidelines, or hand feedback-clusters.json to an agent "
            "to synthesize the markdown."
        )


if __name__ == "__main__":
    main()
