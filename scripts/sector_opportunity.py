#!/usr/bin/env python3
"""Score sectoral opportunities from network composition + subject goals."""

from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from pathlib import Path


MACRO_GROWTH = {
    "fintech": 88,
    "ai": 95,
    "saas": 82,
    "healthcare": 78,
    "consulting": 65,
    "ecommerce": 70,
    "other": 50,
}


def main() -> None:
    parser = argparse.ArgumentParser(description="Sector opportunity scanner")
    parser.add_argument("--network", required=True, help="network.json path")
    parser.add_argument("--subject", required=True, help="subject_profile.json path")
    parser.add_argument("--out", required=True, help="Output CSV path")
    args = parser.parse_args()

    network = json.loads(Path(args.network).read_text(encoding="utf-8"))
    subject = json.loads(Path(args.subject).read_text(encoding="utf-8"))

    industries = Counter(c.get("industry", "other") for c in network["connections"])
    total = sum(industries.values()) or 1
    target_inds = {i.lower() for i in subject.get("target_industries", [])}
    subject_skills = {s.lower() for s in subject.get("skills", [])}

    rows = []
    for industry, count in industries.most_common():
        network_access = min(100, int((count / total) * 200))
        growth = MACRO_GROWTH.get(industry, 50)
        skills_fit = 80 if industry in target_inds else 45
        geo_fit = 75  # placeholder; refine with location data
        interest = 90 if industry in target_inds else 55
        score = round(
            0.30 * growth + 0.25 * network_access + 0.20 * skills_fit + 0.15 * geo_fit + 0.10 * interest,
            1,
        )
        rows.append({
            "sector": industry,
            "connections": count,
            "network_access_score": network_access,
            "market_growth_score": growth,
            "skills_fit_score": skills_fit,
            "sector_score": score,
            "rationale": f"{count} connections ({count/total:.0%} of network); growth signal {growth}",
        })

    rows.sort(key=lambda x: -x["sector_score"])
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    print(f"Wrote {len(rows)} sectors to {out}")
    for r in rows[:5]:
        print(f"  {r['sector']}: {r['sector_score']}")


if __name__ == "__main__":
    main()