#!/usr/bin/env python3
"""Prepare a Google Drive upload plan for an AI-DLC epic's Markdown docs.

Walks EPIC_DIR, collects every `.md` file (ignoring `.xml` and other files),
mirrors the folder structure (skipping folders that contain no `.md` anywhere
beneath them, e.g. an XML-only `system-prompts/`), assigns human-readable
titles, and writes one JSON payload per file plus a manifest describing the
folder tree to create in Drive.

The manifest is consumed by the `aidlc-google-mcp-sync` skill, which creates
the Drive folders (resolving parent IDs at runtime) and then calls the Google
Drive MCP `create_file` tool with each payload's `textContent`.

Usage:
    python prepare_payloads.py --epic-dir <path> [--out <dir>] [--root-title <title>]

Output dir defaults to a temp folder printed at the end.
"""
import argparse
import json
import re
import sys
import tempfile
from pathlib import Path

# Known folder-name -> friendly title overrides. Anything not listed falls back
# to a generic prettifier (hyphens/underscores -> spaces, Title Case).
FOLDER_TITLE_OVERRIDES = {
    "designs": "Designs",
    "policy-config": "Policy & Configuration",
    "evaluation-response": "Evaluation & Response",
    "counter-store": "Counter Store",
    "framework-core": "Framework Core",
    "observability": "Observability",
    "system-prompts": "System Prompts",
}

# Known file-stem -> friendly title overrides (case-insensitive match on stem).
FILE_TITLE_OVERRIDES = {
    "vision": "Vision Document",
    "high-level-design": "High-Level Design",
    "hld": "High-Level Design",
    "adr": "Architecture Decision Records",
    "audit": "Audit Log",
    "lld": "Low-Level Design",
}


def prettify(name: str) -> str:
    """hyphen/underscore separated -> Title Case words."""
    words = re.split(r"[-_\s]+", name.strip())
    return " ".join(w[:1].upper() + w[1:] if w else w for w in words if w)


def folder_title(dir_name: str) -> str:
    return FOLDER_TITLE_OVERRIDES.get(dir_name.lower(), prettify(dir_name))


def file_title(stem: str) -> str:
    low = stem.lower()
    if low in FILE_TITLE_OVERRIDES:
        return FILE_TITLE_OVERRIDES[low]
    # `<component>-EARS` -> "EARS Specifications"
    if low.endswith("-ears") or low == "ears":
        return "EARS Specifications"
    return prettify(stem)


def has_md(dir_path: Path) -> bool:
    """True if this directory contains a .md file anywhere beneath it."""
    return any(dir_path.rglob("*.md"))


def build_plan(epic_dir: Path, out_dir: Path, root_title: str) -> dict:
    md_files = sorted(epic_dir.rglob("*.md"))
    if not md_files:
        raise SystemExit(f"No .md files found under {epic_dir}")

    # Collect the set of relative directories that must exist (only those that
    # contain .md files somewhere beneath them). "" denotes the epic root.
    needed_dirs: set[str] = set()
    for md in md_files:
        rel_parent = md.parent.relative_to(epic_dir)
        parts = rel_parent.parts
        for i in range(1, len(parts) + 1):
            needed_dirs.add("/".join(parts[:i]))

    folders = []
    for rel in sorted(needed_dirs, key=lambda p: (p.count("/"), p)):
        parts = rel.split("/")
        parent_rel = "/".join(parts[:-1])  # "" for top-level
        folders.append(
            {"rel_path": rel, "parent_rel": parent_rel, "title": folder_title(parts[-1])}
        )

    out_dir.mkdir(parents=True, exist_ok=True)
    files = []
    for idx, md in enumerate(md_files, start=1):
        rel_parent = str(md.parent.relative_to(epic_dir))
        if rel_parent == ".":
            rel_parent = ""
        title = file_title(md.stem)
        content = md.read_text(encoding="utf-8")
        payload = {
            "title": title,
            "textContent": content,
            "contentMimeType": "text/markdown",
        }
        payload_name = f"{idx:02d}.json"
        (out_dir / payload_name).write_text(json.dumps(payload), encoding="utf-8")
        files.append(
            {
                "num": f"{idx:02d}",
                "title": title,
                "src": str(md),
                "rel_parent": rel_parent,
                "payload": str(out_dir / payload_name),
                "chars": len(content),
            }
        )

    manifest = {
        "epic_dir": str(epic_dir),
        "root_title": root_title,
        "out_dir": str(out_dir),
        "folders": folders,
        "files": files,
    }
    (out_dir / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    return manifest


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--epic-dir", required=True, help="Path to the epic dir under aidlc-docs/")
    ap.add_argument("--out", default=None, help="Output dir for payloads + manifest")
    ap.add_argument(
        "--root-title",
        default=None,
        help="Friendly title for the epic's top-level Drive folder "
        "(defaults to a Title-Cased epic dir name)",
    )
    args = ap.parse_args()

    epic_dir = Path(args.epic_dir).expanduser().resolve()
    if not epic_dir.is_dir():
        raise SystemExit(f"Epic dir not found: {epic_dir}")

    out_dir = (
        Path(args.out).expanduser().resolve()
        if args.out
        else Path(tempfile.mkdtemp(prefix="gdrive_sync_"))
    )
    root_title = args.root_title or prettify(epic_dir.name)

    manifest = build_plan(epic_dir, out_dir, root_title)

    print(f"Epic dir     : {manifest['epic_dir']}")
    print(f"Root title   : {manifest['root_title']}")
    print(f"Output dir   : {manifest['out_dir']}")
    print(f"Folders      : {len(manifest['folders'])}")
    print(f"Files (.md)  : {len(manifest['files'])}")
    print()
    print("Folder tree (relative -> Drive title):")
    print(f'  ""  ->  {manifest["root_title"]}  (epic root)')
    for f in manifest["folders"]:
        print(f'  {f["rel_path"]}  ->  {f["title"]}')
    print()
    print("Files:")
    for f in manifest["files"]:
        loc = f["rel_parent"] or "(root)"
        print(f'  {f["num"]}  {loc:>28}  ->  {f["title"]}  ({f["chars"]} chars)')
    print()
    print(f"Manifest: {out_dir / 'manifest.json'}")


if __name__ == "__main__":
    main()
