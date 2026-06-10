#!/usr/bin/env python3
"""Validate LinkedIn data export ZIP before parsing."""

from __future__ import annotations

import argparse
import json
import zipfile
from pathlib import Path

EXPECTED_FILES = {"Connections.csv", "Profile.csv"}


def check_zip(path: Path) -> dict:
    result = {"path": str(path), "valid": False, "files_found": [], "missing": [], "errors": []}
    if not path.exists():
        result["errors"].append("File not found")
        return result
    if path.suffix.lower() != ".zip":
        result["errors"].append("Expected a .zip file")
        return result
    try:
        with zipfile.ZipFile(path) as zf:
            names = {Path(n).name for n in zf.namelist()}
            result["files_found"] = sorted(names)
            result["missing"] = sorted(EXPECTED_FILES - names)
            result["valid"] = not result["missing"]
            if "Connections.csv" not in names:
                result["errors"].append("Connections.csv missing — network analysis limited")
    except zipfile.BadZipFile:
        result["errors"].append("Invalid or corrupted ZIP")
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, help="Path to LinkedIn export ZIP")
    parser.add_argument("--out", help="Write result JSON")
    args = parser.parse_args()

    result = check_zip(Path(args.input))
    text = json.dumps(result, indent=2)
    if args.out:
        Path(args.out).write_text(text, encoding="utf-8")
    print(text)
    raise SystemExit(0 if result["valid"] else 1)


if __name__ == "__main__":
    main()