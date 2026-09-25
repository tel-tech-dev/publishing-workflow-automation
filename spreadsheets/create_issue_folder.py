"""Create a new issue directory from spreadsheet templates and collected text files.

Refactored from the production helper `folder_files_preparation.py`.
"""
from __future__ import annotations

import argparse
import shutil
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
from common.config import ISSUE_OUTPUT_DIR, TEMPLATES_DIR, WORKSPACE_DIR


def create_issue(issue: str) -> Path:
    destination = ISSUE_OUTPUT_DIR / issue
    destination.mkdir(parents=True, exist_ok=True)

    if TEMPLATES_DIR.exists():
        for src in TEMPLATES_DIR.iterdir():
            if not src.is_file():
                continue
            # Legacy templates used a two-character issue prefix. Replace it
            # with the requested issue number when possible.
            name = issue + src.name[2:] if len(src.name) > 2 else src.name
            shutil.copy2(src, destination / name)

    final_texts = WORKSPACE_DIR / issue / "final"
    if final_texts.exists():
        for src in final_texts.iterdir():
            if src.is_file():
                shutil.copy2(src, destination / src.name)

    return destination


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("issue", help="Issue number, e.g. 01")
    args = parser.parse_args()
    print(f"Created/prepared: {create_issue(args.issue)}")


if __name__ == "__main__":
    main()
