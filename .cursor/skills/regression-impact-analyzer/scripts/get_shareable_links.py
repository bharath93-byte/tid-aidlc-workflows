"""Generate shareable GitHub artifact download links for test analysis summary.

Usage:
    python get_shareable_links.py [--analysis-dir <path>] [--repo OWNER/REPO]

Reads state.json and outputs a markdown table of run and artifact download URLs.
Falls back to local artifact paths when run IDs are unset (cache hits).
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

from paths import default_analysis_dir

DEFAULT_REPO = "Trimble-Cloud-Core-Platform/iam"

LOCAL_ARTIFACT_DIRS = {
    "main-results (local)": "main-results",
    "main-report (local)": "main-report",
    "branch-results (local)": "branch-results",
    "branch-report (local)": "branch-report",
}


def run_id_link(repo: str, run_id: int | str | None) -> str:
    if not run_id:
        return "n/a"
    return f"https://github.com/{repo}/actions/runs/{run_id}"


def artifact_link(repo: str, run_id: int | str, artifact_id: int | str) -> str:
    return f"https://github.com/{repo}/actions/runs/{run_id}/artifacts/{artifact_id}"


def fetch_artifacts(repo: str, run_id: int | str) -> list[dict]:
    result = subprocess.run(
        ["gh", "api", f"repos/{repo}/actions/runs/{run_id}/artifacts"],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        return []
    data = json.loads(result.stdout)
    return data.get("artifacts", [])


def find_artifact_url(repo: str, run_id: int | str, name: str, artifacts: list[dict]) -> str:
    for artifact in artifacts:
        if artifact.get("name") == name:
            wf_run = artifact.get("workflow_run", {}).get("id", run_id)
            return artifact_link(repo, wf_run, artifact["id"])
    return "not available"


def local_artifact_rows(analysis_dir: Path) -> list[str]:
    rows = []
    for label, folder in LOCAL_ARTIFACT_DIRS.items():
        path = analysis_dir / folder
        if path.exists():
            rows.append(f"| {label} | `{path}` |")
    return rows


def build_links(repo: str, state: dict, analysis_dir: Path) -> str:
    lines = [
        "## Shareable Links",
        "",
        "| Resource | Link |",
        "|----------|------|",
    ]

    orchestrator_run_id = state.get("orchestrator_run_id")
    main_test_run_id = state.get("main_test_run_id")
    branch_test_run_id = state.get("branch_test_run_id")
    github_rows = 0

    if orchestrator_run_id:
        lines.append(
            f"| Orchestrator run | [{orchestrator_run_id}]({run_id_link(repo, orchestrator_run_id)}) |"
        )
        github_rows += 1
        artifacts = fetch_artifacts(repo, orchestrator_run_id)
        for name in (
            "Allure-Single-Report-main",
            "Allure-Single-Report-branch",
            "allure-results-main",
            "allure-results-branch",
        ):
            url = find_artifact_url(repo, orchestrator_run_id, name, artifacts)
            if url != "not available":
                lines.append(f"| {name} | [download]({url}) |")
                github_rows += 1
            else:
                lines.append(f"| {name} | not available |")
                github_rows += 1
    else:
        if main_test_run_id:
            lines.append(
                f"| Main test run | [{main_test_run_id}]({run_id_link(repo, main_test_run_id)}) |"
            )
            github_rows += 1
            main_artifacts = fetch_artifacts(repo, main_test_run_id)
            url = find_artifact_url(repo, main_test_run_id, "Allure-Single-Report", main_artifacts)
            lines.append(
                f"| Allure-Single-Report-main | [download]({url}) |"
                if url != "not available"
                else "| Allure-Single-Report-main | not available |"
            )
            github_rows += 1
            url = find_artifact_url(repo, main_test_run_id, "allure-results", main_artifacts)
            lines.append(
                f"| allure-results-main | [download]({url}) |"
                if url != "not available"
                else "| allure-results-main | not available |"
            )
            github_rows += 1

        if branch_test_run_id:
            lines.append(
                f"| Branch test run | [{branch_test_run_id}]({run_id_link(repo, branch_test_run_id)}) |"
            )
            github_rows += 1
            branch_artifacts = fetch_artifacts(repo, branch_test_run_id)
            url = find_artifact_url(repo, branch_test_run_id, "Allure-Single-Report", branch_artifacts)
            lines.append(
                f"| Allure-Single-Report-branch | [download]({url}) |"
                if url != "not available"
                else "| Allure-Single-Report-branch | not available |"
            )
            github_rows += 1
            url = find_artifact_url(repo, branch_test_run_id, "allure-results", branch_artifacts)
            lines.append(
                f"| allure-results-branch | [download]({url}) |"
                if url != "not available"
                else "| allure-results-branch | not available |"
            )
            github_rows += 1

    local_rows = local_artifact_rows(analysis_dir)
    if local_rows:
        if github_rows == 0:
            lines.append("| GitHub artifact URLs | not available (no run IDs in state) |")
        lines.append("")
        lines.append("### Local artifacts")
        lines.append("")
        lines.append("| Resource | Path |")
        lines.append("|----------|------|")
        lines.extend(local_rows)
        if github_rows == 0:
            lines.append("")
            lines.append(
                "_Artifacts restored from cache or present locally. "
                "Share the backup folder path after archive, or re-run pipelines to populate GitHub run IDs._"
            )

    lines.append("")
    if orchestrator_run_id:
        lines.append(f"**Share this run:** {run_id_link(repo, orchestrator_run_id)}")
    elif main_test_run_id or branch_test_run_id:
        lines.append("**Share test runs:** use the run links above (artifacts section on each run page).")
    elif local_rows:
        lines.append(f"**Local analysis folder:** `{analysis_dir}`")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Generate shareable GitHub links for test analysis")
    parser.add_argument("--analysis-dir", default=str(default_analysis_dir()))
    parser.add_argument("--repo", default=DEFAULT_REPO)
    parser.add_argument("--output", help="Optional path to write markdown (default: stdout only)")
    args = parser.parse_args()

    analysis_dir = Path(args.analysis_dir)
    state_path = analysis_dir / "state.json"
    if not state_path.exists():
        print("ERROR: state.json not found", file=sys.stderr)
        sys.exit(1)

    with open(state_path, encoding="utf-8") as f:
        state = json.load(f)

    markdown = build_links(args.repo, state, analysis_dir)
    print(markdown)

    output_path = Path(args.output) if args.output else analysis_dir / "shareable-links.md"
    output_path.write_text(markdown, encoding="utf-8")
    print(f"\nSaved to: {output_path}", file=sys.stderr)


if __name__ == "__main__":
    main()
