"""Extract text from all RTF files in a directory and produce a simple report.

Refactored from the production `rtf-check.py` utility. No machine-specific
default path is embedded in the public version.
"""
from __future__ import annotations

import argparse
import glob
import io
from pathlib import Path
from striprtf.striprtf import rtf_to_text


def convert_dir(src_dir: Path) -> tuple[Path, Path | None]:
    src_dir = src_dir.resolve()
    files = sorted(src_dir.glob("*.rtf"), key=lambda p: p.name.lower())
    out_path = src_dir / "extracted_text.txt"
    report_path = src_dir / "rtf_decode_report.txt"
    errors: list[str] = []
    total_chars = 0

    with io.open(out_path, "w", encoding="utf-8", newline="\n") as out:
        for index, path in enumerate(files, 1):
            try:
                raw = path.read_bytes()
                text = rtf_to_text(raw.decode("latin-1", errors="ignore"))
                total_chars += len(text)
                out.write(text.rstrip() + "\n")
                out.write(f"-----{index}----{path.name}-------\n")
                out.write(f"character count: {len(text)}\n\n")
            except Exception as exc:  # preserve batch processing on one bad file
                errors.append(f"{path.name}: {exc!r}")

    if errors:
        report_path.write_text("RTF conversion errors:\n" + "\n".join(f" - {x}" for x in errors), encoding="utf-8")
        report = report_path
    else:
        report = None
    print(f"Files: {len(files)}; total characters: {total_chars}; output: {out_path}")
    return out_path, report


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("directory", type=Path)
    args = parser.parse_args()
    convert_dir(args.directory)


if __name__ == "__main__":
    main()
