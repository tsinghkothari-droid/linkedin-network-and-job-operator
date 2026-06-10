#!/usr/bin/env python3
"""Verify LinkedIn browser session from exploration feed snapshot."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


def verify_snapshot(path: Path) -> dict:
    result = {"snapshot": str(path), "ok": False, "signals": [], "errors": []}
    if not path.exists():
        result["errors"].append("Snapshot not found — run explore_linkedin.bat or attach + snapshot feed")
        return result
    text = path.read_text(encoding="utf-8", errors="ignore")
    if "linkedin.com/feed" in text.lower() or "profile viewers" in text.lower():
        result["signals"].append("feed_or_profile_stats")
    if re.search(r"paragraph \[ref=[^\]]+\]: [\w].{2,60}", text):
        result["signals"].append("visible_profile_text")
    if "0 notifications" in text and len(text) < 200:
        result["errors"].append("Snapshot may be empty or not logged in")
    result["ok"] = "feed_or_profile_stats" in result["signals"] and len(text) > 500
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--workspace", default="linkedin-job-workspace")
    parser.add_argument("--snapshot", help="Override snapshot path")
    parser.add_argument("--out")
    args = parser.parse_args()

    root = Path(__file__).resolve().parent.parent
    ws = Path(args.workspace)
    if not ws.is_absolute():
        ws = root / ws
    snap = Path(args.snapshot) if args.snapshot else ws / "exploration" / "snapshots" / "feed.yml"
    result = verify_snapshot(snap)
    text = json.dumps(result, indent=2)
    if args.out:
        Path(args.out).write_text(text, encoding="utf-8")
    print(text)
    raise SystemExit(0 if result["ok"] else 1)


if __name__ == "__main__":
    main()