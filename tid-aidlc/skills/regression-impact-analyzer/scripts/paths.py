"""Cross-platform paths for IAM test analysis artifacts.

Default analysis directory:
  - Windows: %LOCALAPPDATA%\\iam-test-analysis
  - macOS/Linux: $XDG_DATA_HOME/iam-test-analysis or ~/.local/share/iam-test-analysis

Override with environment variable IAM_TEST_ANALYSIS_DIR.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

ENV_OVERRIDE = "IAM_TEST_ANALYSIS_DIR"


def default_analysis_dir() -> Path:
    override = os.environ.get(ENV_OVERRIDE)
    if override:
        return Path(override).expanduser()

    if sys.platform == "win32":
        local_app_data = os.environ.get("LOCALAPPDATA")
        if local_app_data:
            return Path(local_app_data) / "iam-test-analysis"
        return Path.home() / "AppData" / "Local" / "iam-test-analysis"

    xdg_data_home = os.environ.get("XDG_DATA_HOME")
    if xdg_data_home:
        return Path(xdg_data_home) / "iam-test-analysis"
    return Path.home() / ".local" / "share" / "iam-test-analysis"


def main() -> None:
    print(default_analysis_dir())


if __name__ == "__main__":
    main()
