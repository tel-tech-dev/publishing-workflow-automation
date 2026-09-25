"""Configuration helpers for the public portfolio version.

Machine-specific paths are kept in config.json (ignored by Git).  The
repository ships only config.example.json.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CONFIG = PROJECT_ROOT / "config.example.json"
LOCAL_CONFIG = PROJECT_ROOT / "config.json"


def load_config() -> dict[str, Any]:
    path = LOCAL_CONFIG if LOCAL_CONFIG.exists() else DEFAULT_CONFIG
    with path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    return data


CONFIG = load_config()
WORKSPACE_DIR = Path(CONFIG["workspace_dir"]).expanduser()
ISSUE_OUTPUT_DIR = Path(CONFIG["issue_output_dir"]).expanduser()
PHOTO_ARCHIVE_DIR = Path(CONFIG["photo_archive_dir"]).expanduser()
TEMPLATES_DIR = Path(CONFIG.get("templates_dir", ISSUE_OUTPUT_DIR / "templates")).expanduser()
PHOTO_PROCESSING_DIR = Path(CONFIG.get("photo_processing_dir", WORKSPACE_DIR / "photo-processing")).expanduser()
CHROMEDRIVER_PATH = str(Path(CONFIG.get("chromedriver_path", "chromedriver")))
OPENOFFICE_PATH = str(Path(CONFIG.get("openoffice_path", "soffice")))
PUBLICATION_YEAR = int(CONFIG.get("publication_year", 2026))

# Prefixes are kept for a few source-derived modules that still use legacy
# string concatenation internally. New code should prefer pathlib.Path.
WORKSPACE_PREFIX = WORKSPACE_DIR.as_posix().rstrip("/") + "/"
ISSUE_OUTPUT_PREFIX = ISSUE_OUTPUT_DIR.as_posix().rstrip("/") + "/"
PHOTO_ARCHIVE_PREFIX = PHOTO_ARCHIVE_DIR.as_posix().rstrip("/") + "/"
PHOTO_PROCESSING_PREFIX = PHOTO_PROCESSING_DIR.as_posix().rstrip("/") + "/"
