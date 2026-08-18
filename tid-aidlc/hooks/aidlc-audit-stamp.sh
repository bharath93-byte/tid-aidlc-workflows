#!/usr/bin/env python3
"""
aidlc-audit-stamp — afterFileEdit hook.

Fires when vision.md is written inside aidlc-docs/.
Appends an audit entry to aidlc-docs/<epic-name>_<epic-id>/audit.md.
Creates audit.md with header if it does not exist.

Input:  JSON on stdin from Cursor's hook system.
Output: exits 0 (no stdout needed for afterFileEdit).
"""

import sys
import json
import os
import re
from datetime import datetime, timezone


def find_file_path(obj):
    """Recursively search a parsed JSON object for a path ending in vision.md."""
    if isinstance(obj, str):
        if "aidlc-docs" in obj and obj.endswith("vision.md"):
            return obj
    elif isinstance(obj, dict):
        for v in obj.values():
            result = find_file_path(v)
            if result:
                return result
    elif isinstance(obj, list):
        for v in obj:
            result = find_file_path(v)
            if result:
                return result
    return None


def main():
    raw = sys.stdin.read()

    file_path = ""
    try:
        data = json.loads(raw)
        file_path = find_file_path(data) or ""
    except Exception:
        pass

    # Fallback: regex scan the raw string
    if not file_path:
        m = re.search(r"aidlc-docs/[^\"'\s\\]+/vision\.md", raw)
        if m:
            file_path = m.group(0)

    if not file_path:
        sys.exit(0)

    # Resolve to absolute path
    if not os.path.isabs(file_path):
        file_path = os.path.join(os.getcwd(), file_path)

    # Safety check: must end with vision.md inside aidlc-docs/
    if not (file_path.endswith("vision.md") and "aidlc-docs" in file_path):
        sys.exit(0)

    epic_dir = os.path.dirname(file_path)
    epic_key = os.path.basename(epic_dir)
    audit_path = os.path.join(epic_dir, "audit.md")

    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    row = f"| {timestamp} | inception | aidlc-vision | vision.md created for {epic_key} | pending |\n"
    header = (
        "| Timestamp (UTC) | Phase | Skill/Event | Details | Approver |\n"
        "|-----------------|-------|-------------|---------|----------|\n"
    )

    try:
        os.makedirs(epic_dir, exist_ok=True)

        if not os.path.exists(audit_path):
            with open(audit_path, "w") as f:
                f.write(f"# Audit Log — {epic_key}\n\n")
                f.write(header)
                f.write(row)
        else:
            with open(audit_path, "r") as f:
                content = f.read()
            with open(audit_path, "a") as f:
                # Only add header if the table isn't there yet
                if "| Timestamp" not in content:
                    f.write(f"\n{header}")
                f.write(row)
    except Exception:
        # Fail open — never block the agent
        pass

    sys.exit(0)


if __name__ == "__main__":
    main()
