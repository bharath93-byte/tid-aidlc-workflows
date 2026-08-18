#!/usr/bin/env python3
"""Export slim PR review comments for repo rule / standards analysis.

Repo-agnostic: works against any GitHub repo via `--repo owner/name`.

Uses GitHub REST API. By default fetches only inline review comments:
  GET /repos/{owner}/{repo}/pulls/{pull_number}/comments

Extracts path, line, and body text — no authors or GitHub metadata.

Optional:
  --include-thread   issue conversation comments (noisier, more bot traffic)
  --include-reviews  review summary bodies (approve / request-changes text)

Auth: GITHUB_TOKEN / GH_TOKEN, or `gh auth login`.

Examples:
  # Inline review comments only (best for coding-standard rules)
  python scripts/export_feedback.py --repo owner/name --out-dir ./review-guidelines

  # Resume after interruption (skips PRs already in parts/)
  python scripts/export_feedback.py --repo owner/name --out-dir ./review-guidelines
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

DEFAULT_REPO = "Trimble-Cloud-Core-Platform/iam"
API_ROOT = "https://api.github.com"

NOISE = re.compile(
    r"dependabot|github-actions|sonarcloud|codecov|@dependabot",
    re.I,
)


def token() -> str:
    if env := (os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")):
        return env.strip()
    try:
        return subprocess.check_output(["gh", "auth", "token"], text=True).strip()
    except (subprocess.CalledProcessError, FileNotFoundError) as exc:
        raise SystemExit("Set GITHUB_TOKEN or run `gh auth login`") from exc


def repo_parts(repo: str) -> tuple[str, str]:
    owner, name = repo.split("/", 1)
    return owner, name


def is_noise(text: str) -> bool:
    t = text.strip()
    return not t or NOISE.search(t)


class Client:
    def __init__(self, token_value: str) -> None:
        self._token = token_value

    def _get_url(self, url: str) -> tuple[Any, str | None]:
        headers = {
            "Authorization": f"Bearer {self._token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        }
        for attempt in range(6):
            req = urllib.request.Request(url, headers=headers)
            try:
                with urllib.request.urlopen(req, timeout=120) as resp:
                    body = json.loads(resp.read().decode())
                    return body, _next_link(resp.headers.get("Link"))
            except urllib.error.HTTPError as err:
                if err.code in {403, 429, 502, 503} and attempt < 5:
                    time.sleep(min(60, 2 ** attempt * 2))
                    continue
                if err.code == 404:
                    return None, None
                raise SystemExit(f"HTTP {err.code}: {err.read().decode()}") from err
        raise SystemExit("retries exhausted")

    def get_json(self, path: str, params: dict[str, str] | None = None) -> tuple[Any, str | None]:
        query = f"?{urllib.parse.urlencode(params)}" if params else ""
        return self._get_url(f"{API_ROOT}{path}{query}")

    def paginate(self, path: str, params: dict[str, str] | None = None) -> list[Any]:
        items: list[Any] = []
        url: str | None = f"{API_ROOT}{path}"
        if params:
            url += f"?{urllib.parse.urlencode(params)}"
        while url:
            body, next_url = self._get_url(url)
            if body is None:
                break
            if not isinstance(body, list):
                raise SystemExit(f"expected list from {path}, got {type(body)}")
            items.extend(body)
            url = next_url
        return items

    def list_pr_numbers(
        self,
        owner: str,
        repo: str,
        state: str,
        since: str | None,
        limit: int | None,
    ) -> list[int]:
        """List PR numbers via gh CLI (handles merged + large repos reliably)."""
        repo_slug = f"{owner}/{repo}"
        gh_state = state if state in {"open", "closed", "all"} else "merged"
        cmd = [
            "gh",
            "pr",
            "list",
            "--repo",
            repo_slug,
            "--state",
            gh_state,
            "--limit",
            "10000",
            "--json",
            "number,updatedAt",
        ]
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        except (subprocess.CalledProcessError, FileNotFoundError) as exc:
            raise SystemExit(f"gh pr list failed: {exc}") from exc

        rows = json.loads(result.stdout)
        numbers: list[int] = []
        for row in rows:
            updated = row.get("updatedAt") or ""
            if since and updated < since:
                continue
            numbers.append(row["number"])

        numbers.sort()
        if limit:
            numbers = numbers[:limit]
        return numbers


def _next_link(link_header: str | None) -> str | None:
    if not link_header:
        return None
    for part in link_header.split(","):
        if "rel=\"next\"" in part:
            return part.split(";")[0].strip().strip("<>")
    return None


def slim_inline(raw: list[dict[str, Any]]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for row in raw:
        text = (row.get("body") or "").strip()
        if is_noise(text):
            continue
        out.append(
            {
                "path": row.get("path") or "",
                "line": row.get("line") or row.get("original_line"),
                "text": text,
            }
        )
    return out


def slim_thread(raw: list[dict[str, Any]]) -> list[str]:
    out: list[str] = []
    for row in raw:
        text = (row.get("body") or "").strip()
        if not is_noise(text):
            out.append(text)
    return out


def slim_reviews(raw: list[dict[str, Any]]) -> list[dict[str, str]]:
    out: list[dict[str, str]] = []
    for row in raw:
        text = (row.get("body") or "").strip()
        if not is_noise(text):
            out.append({"state": row.get("state") or "", "text": text})
    return out


def fetch_pr(
    client: Client,
    owner: str,
    repo: str,
    number: int,
    include_thread: bool,
    include_reviews: bool,
) -> dict[str, Any]:
    inline = slim_inline(
        client.paginate(f"/repos/{owner}/{repo}/pulls/{number}/comments", {"per_page": "100"})
    )

    record: dict[str, Any] = {"number": number, "inline": inline}

    if include_thread:
        record["thread"] = slim_thread(
            client.paginate(f"/repos/{owner}/{repo}/issues/{number}/comments", {"per_page": "100"})
        )
    if include_reviews:
        record["reviews"] = slim_reviews(
            client.paginate(f"/repos/{owner}/{repo}/pulls/{number}/reviews", {"per_page": "100"})
        )

    return record


def has_content(record: dict[str, Any]) -> bool:
    if record.get("inline"):
        return True
    if record.get("thread"):
        return True
    if record.get("reviews"):
        return True
    return False


def write_markdown(path: Path, meta: dict[str, Any], prs: list[dict[str, Any]]) -> None:
    lines = [
        "# PR review feedback",
        f"Repo: `{meta['repo']}` | PRs: {meta['with_feedback']}",
        "",
    ]
    for pr in prs:
        lines.append(f"## PR #{pr['number']}")
        if pr.get("inline"):
            lines.append("### Inline")
            for c in pr["inline"]:
                lines.extend([f"**{c['path']}:{c.get('line', 'n/a')}**", c["text"], "", "---", ""])
        if pr.get("thread"):
            lines.append("### Thread")
            for t in pr["thread"]:
                lines.extend([t, "", "---", ""])
        if pr.get("reviews"):
            lines.append("### Reviews")
            for r in pr["reviews"]:
                lines.extend([f"**{r['state']}**", r["text"], "", "---", ""])
        lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def merge(out_dir: Path, repo: str, markdown: Path | None) -> Path:
    parts = sorted(out_dir.glob("parts/*.json"), key=lambda p: int(p.stem))
    prs = [json.loads(p.read_text(encoding="utf-8")) for p in parts]
    with_feedback = [p for p in prs if has_content(p)]
    meta = {
        "repo": repo,
        "exported_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "pr_count": len(prs),
        "with_feedback": len(with_feedback),
    }
    out = out_dir / "feedback-corpus.json"
    out.write_text(json.dumps({"meta": meta, "prs": with_feedback}, indent=2), encoding="utf-8")
    if markdown:
        write_markdown(markdown, meta, with_feedback)
    print(f"merged {len(with_feedback)} PRs with feedback -> {out}")
    return out


def main() -> None:
    parser = argparse.ArgumentParser(description="Export slim PR review comments")
    parser.add_argument("--repo", default=DEFAULT_REPO)
    parser.add_argument("--out-dir", default="./review-guidelines")
    parser.add_argument("--state", default="merged", choices=["open", "closed", "merged", "all"])
    parser.add_argument("--since", help="ISO date, e.g. 2024-01-01")
    parser.add_argument("--limit", type=int)
    parser.add_argument("--workers", type=int, default=8)
    parser.add_argument("--include-thread", action="store_true")
    parser.add_argument("--include-reviews", action="store_true")
    parser.add_argument("--include-empty", action="store_true")
    parser.add_argument("--markdown", metavar="PATH")
    parser.add_argument("--merge-only", action="store_true")
    args = parser.parse_args()

    out_dir = Path(args.out_dir)
    parts_dir = out_dir / "parts"
    parts_dir.mkdir(parents=True, exist_ok=True)

    if args.merge_only:
        merge(out_dir, args.repo, Path(args.markdown) if args.markdown else None)
        return

    client = Client(token())
    owner, repo_name = repo_parts(args.repo)
    numbers = client.list_pr_numbers(owner, repo_name, args.state, args.since, args.limit)
    pending = [n for n in numbers if not (parts_dir / f"{n}.json").exists()]

    print(f"total={len(numbers)} pending={len(pending)} workers={args.workers}")

    def work(n: int) -> None:
        record = fetch_pr(
            client, owner, repo_name, n, args.include_thread, args.include_reviews
        )
        if not args.include_empty and not has_content(record):
            print(f"skip #{n} (empty)")
            return
        (parts_dir / f"{n}.json").write_text(json.dumps(record), encoding="utf-8")
        print(f"done #{n} ({len(record.get('inline', []))} inline)")

    if pending:
        with ThreadPoolExecutor(max_workers=args.workers) as pool:
            futures = [pool.submit(work, n) for n in pending]
            for f in as_completed(futures):
                f.result()

    merge(out_dir, args.repo, Path(args.markdown) if args.markdown else None)


if __name__ == "__main__":
    main()
