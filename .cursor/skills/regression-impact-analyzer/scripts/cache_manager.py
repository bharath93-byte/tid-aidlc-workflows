"""Cache test-analysis artifacts by PR/env/branch commit SHA to avoid redundant fetches.

Usage:
    python cache_manager.py check --pr 4094 --env qatest --branch dev/IAM-8046 \
        --marker regression --data-region us --repo OWNER/REPO
    python cache_manager.py restore --pr 4094 --env qatest --branch dev/IAM-8046 \
        --marker regression --data-region us --repo OWNER/REPO
    python cache_manager.py store --type pr|main|branch [--analysis-dir <path>]
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

from paths import default_analysis_dir

INDEX_FILE = "index.json"
DEFAULT_REPO = "Trimble-Cloud-Core-Platform/iam"

PR_ITEMS = ["pr-diff.patch", "pr-metadata.json"]
MAIN_ITEMS = ["main-results", "main-report"]
BRANCH_ITEMS = ["branch-results", "branch-report"]


def cache_root(analysis_dir: Path) -> Path:
    return analysis_dir / "cache"


def index_path(analysis_dir: Path) -> Path:
    return cache_root(analysis_dir) / INDEX_FILE


def sanitize_branch(branch: str) -> str:
    safe = re.sub(r'[<>:"/\\|?*]', "-", branch)
    return safe.replace(" ", "_")[:80]


def sanitize_cache_part(value: str) -> str:
    safe = re.sub(r'[<>:"/\\|?*]', "-", value)
    return safe.replace(" ", "_")[:40]


def short_sha(sha: str) -> str:
    return (sha or "")[:12]


def load_index(analysis_dir: Path) -> dict:
    path = index_path(analysis_dir)
    if not path.exists():
        return {"pr": {}, "main": {}, "branch": {}}
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    for key in ("pr", "main", "branch"):
        data.setdefault(key, {})
    return data


def save_index(analysis_dir: Path, index: dict) -> None:
    root = cache_root(analysis_dir)
    root.mkdir(parents=True, exist_ok=True)
    with open(index_path(analysis_dir), "w", encoding="utf-8") as f:
        json.dump(index, f, indent=2, ensure_ascii=False)


def get_pr_head_sha(repo: str, pr_number: int) -> str:
    data = subprocess.run(
        ["gh", "pr", "view", str(pr_number), "--repo", repo, "--json", "headRefOid"],
        capture_output=True,
        text=True,
        check=True,
    )
    return json.loads(data.stdout)["headRefOid"]


def get_main_sha(repo: str) -> str:
    data = subprocess.run(
        ["gh", "api", f"repos/{repo}/commits/main", "--jq", ".sha"],
        capture_output=True,
        text=True,
        check=True,
    )
    return data.stdout.strip()


def pr_key(pr_number: int, head_sha: str) -> str:
    return f"{pr_number}:{short_sha(head_sha)}"


def main_key(environment: str, data_region: str, marker: str, main_sha: str) -> str:
    return (
        f"{environment}:{data_region}:{sanitize_cache_part(marker)}:{short_sha(main_sha)}"
    )


def branch_key(
    environment: str, data_region: str, marker: str, branch: str, head_sha: str
) -> str:
    return (
        f"{environment}:{data_region}:{sanitize_cache_part(marker)}:"
        f"{sanitize_branch(branch)}:{short_sha(head_sha)}"
    )


def cache_dir_for_pr(analysis_dir: Path, pr_number: int, head_sha: str) -> Path:
    return cache_root(analysis_dir) / "pr" / str(pr_number) / short_sha(head_sha)


def cache_dir_for_main(
    analysis_dir: Path, environment: str, data_region: str, marker: str, main_sha: str
) -> Path:
    return (
        cache_root(analysis_dir)
        / "main"
        / environment
        / data_region
        / sanitize_cache_part(marker)
        / short_sha(main_sha)
    )


def cache_dir_for_branch(
    analysis_dir: Path,
    environment: str,
    data_region: str,
    marker: str,
    branch: str,
    head_sha: str,
) -> Path:
    return (
        cache_root(analysis_dir)
        / "branch"
        / environment
        / data_region
        / sanitize_cache_part(marker)
        / sanitize_branch(branch)
        / short_sha(head_sha)
    )


def cache_has_items(cache_dir: Path, items: list[str]) -> bool:
    if not cache_dir.exists():
        return False
    for item in items:
        if not (cache_dir / item).exists():
            return False
    return True


def copy_items(source_dir: Path, dest_dir: Path, items: list[str]) -> list[str]:
    dest_dir.mkdir(parents=True, exist_ok=True)
    copied = []
    for item in items:
        src = source_dir / item
        if not src.exists():
            continue
        dst = dest_dir / item
        if dst.exists():
            if dst.is_dir():
                shutil.rmtree(dst)
            else:
                dst.unlink()
        if src.is_dir():
            shutil.copytree(src, dst)
        else:
            shutil.copy2(src, dst)
        copied.append(item)
    return copied


def apply_reuse_flags(reuse: dict, skip_to_phase: int | None) -> dict:
    """Return reuse flags safe to persist in state for this run.

    Partial cache hits must not skip downloads for sides that will be re-tested.
    """
    return {
        "pr_diff": reuse["pr_diff"] and skip_to_phase == 5,
        "main_artifacts": reuse["main_artifacts"] and skip_to_phase in (3, 5),
        "branch_artifacts": reuse["branch_artifacts"] and skip_to_phase == 5,
    }


def resolve_state_shas(state: dict, repo: str) -> dict:
    """Fill missing commit SHAs in state from GitHub."""
    pr_number = state.get("pr_number")
    if pr_number and not (state.get("pr_head_sha") or state.get("branch_sha")):
        head_sha = get_pr_head_sha(repo, pr_number)
        state["pr_head_sha"] = head_sha
        state["branch_sha"] = head_sha
    if not state.get("main_sha"):
        state["main_sha"] = get_main_sha(repo)
    if state.get("pr_head_sha") and not state.get("branch_sha"):
        state["branch_sha"] = state["pr_head_sha"]
    return state


def store_cache(analysis_dir: Path, cache_type: str, repo: str) -> None:
    state_path = analysis_dir / "state.json"
    if not state_path.exists():
        print("ERROR: state.json not found; nothing to store", file=sys.stderr)
        sys.exit(1)

    with open(state_path, encoding="utf-8") as f:
        state = json.load(f)

    state = resolve_state_shas(state, repo)
    with open(state_path, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2, ensure_ascii=False)

    index = load_index(analysis_dir)
    marker = state.get("marker", "regression")
    data_region = state.get("data_region", "us")

    if cache_type == "pr":
        pr_number = state["pr_number"]
        head_sha = state.get("pr_head_sha") or state.get("branch_sha")
        if not head_sha:
            print("ERROR: pr_head_sha missing in state", file=sys.stderr)
            sys.exit(1)
        target = cache_dir_for_pr(analysis_dir, pr_number, head_sha)
        copied = copy_items(analysis_dir, target, PR_ITEMS)
        index["pr"][pr_key(pr_number, head_sha)] = str(target.relative_to(analysis_dir)).replace("\\", "/")

    elif cache_type == "main":
        environment = state["environment"]
        main_sha = state.get("main_sha")
        if not main_sha:
            print("ERROR: main_sha missing in state", file=sys.stderr)
            sys.exit(1)
        target = cache_dir_for_main(analysis_dir, environment, data_region, marker, main_sha)
        copied = copy_items(analysis_dir, target, MAIN_ITEMS)
        index["main"][main_key(environment, data_region, marker, main_sha)] = str(
            target.relative_to(analysis_dir)
        ).replace("\\", "/")

    elif cache_type == "branch":
        environment = state["environment"]
        branch = state["branch"]
        head_sha = state.get("branch_sha") or state.get("pr_head_sha")
        if not head_sha:
            print("ERROR: branch_sha missing in state", file=sys.stderr)
            sys.exit(1)
        target = cache_dir_for_branch(
            analysis_dir, environment, data_region, marker, branch, head_sha
        )
        copied = copy_items(analysis_dir, target, BRANCH_ITEMS)
        index["branch"][branch_key(environment, data_region, marker, branch, head_sha)] = str(
            target.relative_to(analysis_dir)
        ).replace("\\", "/")

    else:
        print(f"ERROR: unknown cache type: {cache_type}", file=sys.stderr)
        sys.exit(1)

    save_index(analysis_dir, index)
    print(json.dumps({"stored": cache_type, "items": copied, "cache_dir": str(target)}, indent=2))


def check_cache(
    analysis_dir: Path,
    repo: str,
    pr_number: int,
    environment: str,
    branch: str,
    marker: str,
    data_region: str,
) -> dict:
    pr_head_sha = get_pr_head_sha(repo, pr_number)
    main_sha = get_main_sha(repo)
    index = load_index(analysis_dir)

    pr_cache_rel = index["pr"].get(pr_key(pr_number, pr_head_sha))
    main_cache_rel = index["main"].get(main_key(environment, data_region, marker, main_sha))
    branch_cache_rel = index["branch"].get(
        branch_key(environment, data_region, marker, branch, pr_head_sha)
    )

    pr_cache = analysis_dir / pr_cache_rel if pr_cache_rel else None
    main_cache = analysis_dir / main_cache_rel if main_cache_rel else None
    branch_cache = analysis_dir / branch_cache_rel if branch_cache_rel else None

    reuse_pr = bool(pr_cache and cache_has_items(pr_cache, PR_ITEMS))
    reuse_main = bool(main_cache and cache_has_items(main_cache, MAIN_ITEMS))
    reuse_branch = bool(branch_cache and cache_has_items(branch_cache, BRANCH_ITEMS))

    skip_to_phase = None
    if reuse_main and reuse_branch:
        skip_to_phase = 5
    elif reuse_main:
        skip_to_phase = 3

    reuse = {
        "pr_diff": reuse_pr,
        "main_artifacts": reuse_main,
        "branch_artifacts": reuse_branch,
    }

    return {
        "pr_number": pr_number,
        "environment": environment,
        "branch": branch,
        "marker": marker,
        "data_region": data_region,
        "pr_head_sha": pr_head_sha,
        "main_sha": main_sha,
        "branch_sha": pr_head_sha,
        "reuse": reuse,
        "apply_reuse": apply_reuse_flags(reuse, skip_to_phase),
        "skip_to_phase": skip_to_phase,
        "cache_paths": {
            "pr": str(pr_cache) if pr_cache else None,
            "main": str(main_cache) if main_cache else None,
            "branch": str(branch_cache) if branch_cache else None,
        },
    }


def restore_cache(
    analysis_dir: Path,
    repo: str,
    pr_number: int,
    environment: str,
    branch: str,
    marker: str,
    data_region: str,
) -> dict:
    plan = check_cache(
        analysis_dir, repo, pr_number, environment, branch, marker, data_region
    )
    restored = {"pr": [], "main": [], "branch": []}

    analysis_dir.mkdir(parents=True, exist_ok=True)

    apply = plan["apply_reuse"]

    if apply["pr_diff"] and plan["cache_paths"]["pr"]:
        restored["pr"] = copy_items(Path(plan["cache_paths"]["pr"]), analysis_dir, PR_ITEMS)

    if apply["main_artifacts"] and plan["cache_paths"]["main"]:
        restored["main"] = copy_items(Path(plan["cache_paths"]["main"]), analysis_dir, MAIN_ITEMS)

    if apply["branch_artifacts"] and plan["cache_paths"]["branch"]:
        restored["branch"] = copy_items(Path(plan["cache_paths"]["branch"]), analysis_dir, BRANCH_ITEMS)

    plan["restored"] = restored
    return plan


def main():
    parser = argparse.ArgumentParser(description="Manage test-analysis artifact cache")
    parser.add_argument("--analysis-dir", default=str(default_analysis_dir()))
    sub = parser.add_subparsers(dest="command", required=True)

    check = sub.add_parser("check", help="Check what can be reused from cache")
    check.add_argument("--repo", required=True)
    check.add_argument("--pr", type=int, required=True, dest="pr_number")
    check.add_argument("--env", required=True)
    check.add_argument("--branch", required=True)
    check.add_argument("--marker", required=True)
    check.add_argument("--data-region", required=True, dest="data_region")

    restore = sub.add_parser("restore", help="Restore reusable cache entries into active analysis dir")
    restore.add_argument("--repo", required=True)
    restore.add_argument("--pr", type=int, required=True, dest="pr_number")
    restore.add_argument("--env", required=True)
    restore.add_argument("--branch", required=True)
    restore.add_argument("--marker", required=True)
    restore.add_argument("--data-region", required=True, dest="data_region")

    store = sub.add_parser("store", help="Store artifacts from active analysis dir into cache")
    store.add_argument("--type", choices=["pr", "main", "branch"], required=True)
    store.add_argument("--repo", default=DEFAULT_REPO)

    resolve = sub.add_parser("resolve-shas", help="Fetch missing SHAs into state.json from GitHub")
    resolve.add_argument("--repo", default=DEFAULT_REPO)

    args = parser.parse_args()
    analysis_dir = Path(args.analysis_dir)

    if args.command == "check":
        result = check_cache(
            analysis_dir,
            args.repo,
            args.pr_number,
            args.env,
            args.branch,
            args.marker,
            args.data_region,
        )
        print(json.dumps(result, indent=2))
    elif args.command == "restore":
        result = restore_cache(
            analysis_dir,
            args.repo,
            args.pr_number,
            args.env,
            args.branch,
            args.marker,
            args.data_region,
        )
        print(json.dumps(result, indent=2))
    elif args.command == "store":
        store_cache(analysis_dir, args.type, args.repo)
    elif args.command == "resolve-shas":
        state_path = analysis_dir / "state.json"
        if not state_path.exists():
            print("ERROR: state.json not found", file=sys.stderr)
            sys.exit(1)
        with open(state_path, encoding="utf-8") as f:
            state = json.load(f)
        state = resolve_state_shas(state, args.repo)
        with open(state_path, "w", encoding="utf-8") as f:
            json.dump(state, f, indent=2, ensure_ascii=False)
        print(json.dumps({
            "pr_head_sha": state.get("pr_head_sha"),
            "main_sha": state.get("main_sha"),
            "branch_sha": state.get("branch_sha"),
        }, indent=2))


if __name__ == "__main__":
    main()
