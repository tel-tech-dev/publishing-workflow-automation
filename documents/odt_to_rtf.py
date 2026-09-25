"""Batch ODT -> RTF conversion through a local OpenOffice installation.

The production launcher referenced a separate `odt_to_rtf_gui.py` that was
not present in the supplied source archive. This public module provides the
portable command-line conversion layer only; publication-specific template
or style mapping from the original external converter is not reproduced.
"""
from __future__ import annotations

import argparse
import subprocess
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
from common.config import OPENOFFICE_PATH


def convert_directory(input_folder: Path, output_folder: Path | None = None) -> int:
    input_folder = input_folder.resolve()
    output_folder = (output_folder or input_folder).resolve()
    output_folder.mkdir(parents=True, exist_ok=True)
    files = sorted(input_folder.glob("*.odt"))
    converted = 0

    for source in files:
        target = output_folder / f"{source.stem}.rtf"
        if target.exists():
            print(f"SKIP existing: {target.name}")
            continue
        cmd = [
            OPENOFFICE_PATH,
            "--headless",
            "--convert-to", "rtf",
            "--outdir", str(output_folder),
            str(source),
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"ERROR {source.name}: {result.stderr.strip()}")
            continue
        converted += 1
        print(f"OK: {source.name} -> {target.name}")
    return converted


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-folder", required=True, type=Path)
    parser.add_argument("--output-folder", type=Path)
    args = parser.parse_args()
    count = convert_directory(args.input_folder, args.output_folder)
    print(f"Converted: {count}")


if __name__ == "__main__":
    main()
