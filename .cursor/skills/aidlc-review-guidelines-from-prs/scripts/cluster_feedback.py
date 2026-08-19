"""Embed + cluster PR review comments into recurring themes.

Repo-agnostic stage 2 of the pipeline:
  1. export_feedback.py  -> feedback-corpus.json  (PR review comments)
  2. cluster_feedback.py -> feedback-clusters.json + clusters-digest.txt  (this script)
  3. LLM synthesis        -> collective-feedback-guidelines.md  (done by the agent)

Pipeline within this script:
  * Vector embeddings via sentence-transformers (all-MiniLM-L6-v2), local & free.
  * Clustering via HDBSCAN (fallback: DBSCAN) over cosine distance.
It writes machine-readable clusters (JSON) plus a compact, human/LLM-readable digest
so an agent can distill each theme into a guideline.

Setup:
  pip install -r scripts/requirements.txt
Note: first run downloads the ~90MB embedding model to the HuggingFace cache. If the
default ~/.cache/huggingface is not writable, set HF_HOME to a writable path.

Usage:
  python scripts/cluster_feedback.py --corpus review-guidelines/feedback-corpus.json \
      --clusters-out review-guidelines/feedback-clusters.json \
      --digest-out review-guidelines/clusters-digest.txt
"""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from pathlib import Path

import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

# --------------------------------------------------------------------------- #
# 1. Load + filter the corpus
# --------------------------------------------------------------------------- #
# Author replies / acknowledgements carry no reusable guidance.
_ACK_PATTERNS = re.compile(
    r"^\s*(thanks?|thank you|done|fixed|updated|resolved|resolving|good catch|"
    r"nice catch|lgtm|ok|okay|sure|agreed|agree|makes sense|will do|got it|"
    r"ack|acknowledged|sounds good|\+1|yep|yes|no|nope|as discussed|"
    r"addressed|changed|re-?added|removed|added)\b",
    re.IGNORECASE,
)
# Automated review bots (Bugbot / CodeRabbit style) emit markdown headers,
# severity badges and HTML prompt comments. Strip them: we want *human* asks.
_BOT_PATTERNS = re.compile(
    r"(<!--|^\s*#{1,6}\s|\*\*(high|medium|low|critical)\b|prompt for ai)",
    re.IGNORECASE,
)


def load_comments(corpus_path: Path, min_words: int, max_words: int) -> list[dict]:
    data = json.loads(corpus_path.read_text())
    seen: set[str] = set()
    comments: list[dict] = []
    for pr in data.get("prs", []):
        for c in pr.get("inline", []):
            text = (c.get("text") or "").strip()
            words = len(text.split())
            if words < min_words or words > max_words:
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
def embed(texts: list[str], model_name: str) -> np.ndarray:
    print(f"Generating local semantic embeddings ({model_name})...")
    model = SentenceTransformer(model_name)  # cached after first run
    return model.encode(
        texts, batch_size=64, show_progress_bar=True, normalize_embeddings=True
    )


def cluster(embeddings: np.ndarray, min_cluster_size: int, min_samples: int) -> np.ndarray:
    """Return a cluster label per row (-1 == noise)."""
    try:
        import hdbscan

        print("Clustering with HDBSCAN...")
        model = hdbscan.HDBSCAN(
            min_cluster_size=min_cluster_size,
            min_samples=min_samples,
            metric="euclidean",  # embeddings are L2-normalized ~= cosine
            cluster_selection_method="leaf",  # many tight themes, not one blob
        )
        return model.fit_predict(embeddings.astype("float64"))
    except ImportError:
        from sklearn.cluster import DBSCAN

        print("HDBSCAN not available, falling back to DBSCAN...")
        distance = np.clip(1.0 - cosine_similarity(embeddings), 0, None)
        return DBSCAN(eps=0.45, min_samples=min_samples, metric="precomputed").fit_predict(
            distance
        )


def build_clusters(comments: list[dict], labels: np.ndarray, embeddings: np.ndarray):
    """Group comments by label and pick a representative (medoid) per cluster."""
    buckets: dict[int, list[int]] = {}
    for idx, label in enumerate(labels):
        if label != -1:
            buckets.setdefault(int(label), []).append(idx)

    clusters = []
    for _label, idxs in buckets.items():
        sub = embeddings[idxs]
        centroid = sub.mean(axis=0)
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


def write_digest(clusters: list[dict], digest_path: Path, sample: int) -> None:
    lines: list[str] = []
    for i, cl in enumerate(clusters, 1):
        lines.append(
            f"=== CLUSTER {i} (size {cl['size']}) paths={cl['top_paths'][:2]} ==="
        )
        for t in cl["comments"][:sample]:
            lines.append(" - " + " ".join(t.split())[:200])
        lines.append("")
    digest_path.write_text("\n".join(lines), encoding="utf-8")


# --------------------------------------------------------------------------- #
# main
# --------------------------------------------------------------------------- #
def main() -> None:
    parser = argparse.ArgumentParser(description="Embed + cluster PR review comments")
    parser.add_argument("--corpus", required=True, help="feedback-corpus.json path")
    parser.add_argument("--clusters-out", help="output clusters JSON (default: beside corpus)")
    parser.add_argument("--digest-out", help="output digest txt (default: beside corpus)")
    parser.add_argument("--model", default="all-MiniLM-L6-v2")
    parser.add_argument("--min-cluster-size", type=int, default=6)
    parser.add_argument("--min-samples", type=int, default=2)
    parser.add_argument("--min-words", type=int, default=5)
    parser.add_argument("--max-words", type=int, default=100)
    parser.add_argument("--digest-sample", type=int, default=6, help="comments/cluster in digest")
    args = parser.parse_args()

    corpus_path = Path(args.corpus)
    clusters_path = Path(args.clusters_out) if args.clusters_out else corpus_path.with_name(
        "feedback-clusters.json"
    )
    digest_path = Path(args.digest_out) if args.digest_out else corpus_path.with_name(
        "clusters-digest.txt"
    )

    comments = load_comments(corpus_path, args.min_words, args.max_words)
    print(f"Extracted {len(comments)} actionable comments after filtering.")
    if not comments:
        raise SystemExit("No comments after filtering — check the corpus path/content.")

    embeddings = embed([c["text"] for c in comments], args.model)
    labels = cluster(embeddings, args.min_cluster_size, args.min_samples)
    clusters = build_clusters(comments, labels, embeddings)
    print(f"Found {len(clusters)} clusters (noise dropped).")

    clusters_path.write_text(json.dumps(clusters, indent=2), encoding="utf-8")
    write_digest(clusters, digest_path, args.digest_sample)
    print(f"Wrote {clusters_path}")
    print(f"Wrote {digest_path}")
    print(
        "\nNext: hand clusters-digest.txt to the agent to synthesize "
        "collective-feedback-guidelines.md."
    )


if __name__ == "__main__":
    main()
