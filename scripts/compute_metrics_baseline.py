#!/usr/bin/env python3
"""Compute baseline professional growth metrics from workspace artifacts."""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve().parent
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))

from parse_analytics_from_snapshot import parse_creator_analytics  # noqa: E402


def read_csv(path: Path) -> list[dict]:
    if not path.exists():
        return []
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--workspace", required=True)
    parser.add_argument("--subject", required=True)
    parser.add_argument("--out", help="metrics_baseline.json path")
    args = parser.parse_args()

    root = Path(__file__).resolve().parent.parent
    ws = Path(args.workspace)
    subject = json.loads(Path(args.subject).read_text(encoding="utf-8"))
    target_inds = {i.lower() for i in subject.get("target_industries", [])}

    metrics_def = json.loads((root / "templates" / "growth_metrics.json").read_text(encoding="utf-8"))

    network_path = ws / "network.json"
    connections = []
    if network_path.exists():
        connections = json.loads(network_path.read_text(encoding="utf-8")).get("connections", [])

    m1 = 0
    if connections:
        in_target = sum(1 for c in connections if (c.get("industry") or "").lower() in target_inds)
        m1 = round(100 * in_target / len(connections), 1)

    m2 = sum(1 for c in connections if c.get("seniority") in ("Director", "VP", "C-level", "Founder"))

    companies = {c.get("company", "").lower() for c in connections if c.get("company")}
    m3 = len(companies)

    analytics = {}
    ca = ws / "exploration" / "snapshots" / "creator-analytics.yml"
    if ca.exists():
        analytics = parse_creator_analytics(ca.read_text(encoding="utf-8", errors="ignore"))
    pv = ws / "exploration" / "snapshots" / "profile-views.yml"
    m4 = 0
    if pv.exists():
        m = re.search(r'paragraph \[ref=[^\]]+\]: "?(\d[\d,]*)"?\s*\n\s*- paragraph.*Profile viewers', pv.read_text(encoding="utf-8", errors="ignore"), re.S)
        if not m:
            m = re.search(r"Profile viewers in the past 90 days", pv.read_text(encoding="utf-8", errors="ignore"))
            nums = re.findall(r'paragraph \[ref=[^\]]+\]: "?([\d,]+)"?', pv.read_text(encoding="utf-8", errors="ignore"))
            m4 = max((int(x.replace(",", "")) for x in nums if x.replace(",", "").isdigit()), default=0)
        else:
            m4 = int(m.group(1).replace(",", ""))

    m5 = analytics.get("impressions", 0)
    m6 = round(100 * analytics.get("engagements", 0) / m5, 2) if m5 else 0

    m7 = 0
    skills_json = ws / "skills_roadmap.json"
    if skills_json.exists():
        roadmap = json.loads(skills_json.read_text(encoding="utf-8"))
        top = roadmap.get("gaps", [])[:5]
        possessed = {s.lower() for s in subject.get("skills", [])}
        if top:
            have = sum(1 for s in top if s.get("skill", "").lower() in possessed)
            m7 = round(100 * have / max(len(top), 1), 1)

    m8 = len(read_csv(ws / "referral_targets.csv"))

    cadence_map = {"rarely": 0, "monthly": 1, "biweekly": 2, "weekly": 4, "multi_weekly": 8}
    cadence = subject.get("intake", {}).get("content_cadence", "monthly")
    m9_target = cadence_map.get(cadence, 1)

    m10 = 0
    biz = ws / "business_opportunities.md"
    if biz.exists():
        m10 = biz.read_text(encoding="utf-8").count("###") or biz.read_text(encoding="utf-8").count("- **")

    baseline = {
        "computed_at": datetime.now(timezone.utc).isoformat(),
        "subject": subject.get("name", ""),
        "metrics": {
            "M1": {"current": m1, "unit": "score_0_100"},
            "M2": {"current": m2, "unit": "count"},
            "M3": {"current": m3, "unit": "count"},
            "M4": {"current": m4, "unit": "count"},
            "M5": {"current": m5, "unit": "count"},
            "M6": {"current": m6, "unit": "percent"},
            "M7": {"current": m7, "unit": "percent"},
            "M8": {"current": m8, "unit": "count"},
            "M9": {"current": 0, "target_cadence": m9_target, "unit": "posts_per_month"},
            "M10": {"current": m10, "unit": "count"},
        },
        "definitions": metrics_def["metrics"],
    }

    out = Path(args.out) if args.out else ws / "metrics_baseline.json"
    out.write_text(json.dumps(baseline, indent=2), encoding="utf-8")
    print(f"Metrics baseline → {out}")


if __name__ == "__main__":
    main()