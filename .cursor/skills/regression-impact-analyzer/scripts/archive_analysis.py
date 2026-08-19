"""Archive completed test analysis artifacts to a datetime-stamped backup folder.

Usage:
    python archive_analysis.py [--analysis-dir <path>]

Moves active analysis files from <ANALYSIS_DIR> into:
    <ANALYSIS_DIR>/backups/<yyyy-MM-dd_HHmmss>_<env>_<branch>/
"""

import argparse
import json
import re
import shutil
import sys
from datetime import datetime
from pathlib import Path

from paths import default_analysis_dir

ITEMS_TO_ARCHIVE = [
    "state.json",
    "comparison-report.json",
    "pr-diff.patch",
    "pr-metadata.json",
    "analysis-report.md",
    "shareable-links.md",
    "main-results",
    "main-report",
    "branch-results",
    "branch-report",
]


def sanitize_branch(branch: str) -> str:
    """Make branch name safe for use in a folder name."""
    safe = re.sub(r'[<>:"/\\|?*]', "-", branch)
    return safe.replace(" ", "_")[:80]


def build_backup_name(state: dict) -> str:
    timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    environment = state.get("environment", "unknown")
    branch = sanitize_branch(state.get("branch", "unknown"))
    return f"{timestamp}_{environment}_{branch}"


def archive(analysis_dir: Path) -> Path:
    if not analysis_dir.exists():
        print(f"ERROR: Analysis directory not found: {analysis_dir}", file=sys.stderr)
        sys.exit(1)

    state_path = analysis_dir / "state.json"
    state = {}
    if state_path.exists():
        with open(state_path, encoding="utf-8") as f:
            state = json.load(f)

    backup_root = analysis_dir / "backups"
    backup_dir = backup_root / build_backup_name(state)
    backup_dir.mkdir(parents=True, exist_ok=False)

    archived = []
    for item in ITEMS_TO_ARCHIVE:
        source = analysis_dir / item
        if not source.exists():
            continue
        destination = backup_dir / item
        shutil.move(str(source), str(destination))
        archived.append(item)

    manifest = {
        "archived_at": datetime.now().isoformat(timespec="seconds"),
        "backup_folder": backup_dir.name,
        "backup_path": str(backup_dir),
        "state": state,
        "archived_items": archived,
    }
    with open(backup_dir / "manifest.json", "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)

    print(f"Archived {len(archived)} item(s) to:")
    print(f"  {backup_dir}")
    return backup_dir


def main():
    parser = argparse.ArgumentParser(description="Archive test analysis artifacts to backups folder")
    parser.add_argument(
        "--analysis-dir",
        default=str(default_analysis_dir()),
        help="Active analysis directory (default: platform-specific; see paths.py)",
    )
    args = parser.parse_args()
    archive(Path(args.analysis_dir))


if __name__ == "__main__":
    main()
