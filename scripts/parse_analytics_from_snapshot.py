#!/usr/bin/env python3
"""Extract creator analytics metrics from Playwright YAML snapshots."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


def parse_creator_analytics(text: str) -> dict:
    metrics: dict = {}

    imp_matches = re.findall(r'paragraph \[ref=[^\]]+\]: "?([\d,]+)"?\s*$', text, re.M)
    numbers = [int(x.replace(",", "")) for x in imp_matches if x.replace(",", "").isdigit()]

    if numbers:
        metrics["impressions"] = max(numbers)

    growth = re.search(r'paragraph \[ref=[^\]]+\]: "?(\d+)%"?', text)
    if growth:
        metrics["impressions_growth_pct"] = int(growth.group(1))

    eng = re.search(
        r'Social engagements.*?\n.*?paragraph \[ref=[^\]]+\]: "?(\d+)"?',
        text,
        re.S | re.I,
    )
    if not eng:
        for i, line in enumerate(text.splitlines()):
            if "Social engagements" in line:
                for follow in text.splitlines()[i : i + 15]:
                    m = re.search(r'paragraph \[ref=[^\]]+\]: "?(\d+)"?', follow)
                    if m:
                        metrics["engagements"] = int(m.group(1))
                        break
                break
    else:
        metrics["engagements"] = int(eng.group(1))

    for label, key in [
        (r'paragraph \[ref=[^\]]+\]: Reactions.*?\n.*?paragraph \[ref=[^\]]+\]: "?(\d+)"?', "reactions"),
        (r'Comments.*?\n.*?paragraph \[ref=[^\]]+\]: "?(\d+)"?', "comments"),
        (r'Reposts.*?\n.*?paragraph \[ref=[^\]]+\]: "?(\d+)"?', "reposts"),
        (r'Saves.*?\n.*?paragraph \[ref=[^\]]+\]: "?(\d+)"?', "saves"),
    ]:
        m = re.search(label, text, re.S | re.I)
        if m:
            metrics[key] = int(m.group(1))

    return metrics


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--snapshot", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    text = Path(args.snapshot).read_text(encoding="utf-8", errors="ignore")
    metrics = parse_creator_analytics(text)
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    print(json.dumps(metrics, indent=2))


if __name__ == "__main__":
    main()