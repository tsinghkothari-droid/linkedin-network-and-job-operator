#!/usr/bin/env python3
"""Rank senior people to connect with, nurture, or request intros."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

TIER_SCORES = {
    "C-level": 100, "Founder": 98, "Investor": 95, "VP": 90,
    "Director": 85, "Recruiter": 88, "Manager": 70, "Advisor": 75, "IC": 40,
}


def main() -> None:
    parser = argparse.ArgumentParser(description="Senior people recommendations")
    parser.add_argument("--network", required=True)
    parser.add_argument("--subject", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    network = json.loads(Path(args.network).read_text(encoding="utf-8"))
    subject = json.loads(Path(args.subject).read_text(encoding="utf-8"))
    target_inds = {i.lower() for i in subject.get("target_industries", [])}

    rows = []
    for c in network["connections"]:
        seniority = c.get("seniority", "IC")
        industry = c.get("industry", "other")
        tier = TIER_SCORES.get(seniority, 40)
        industry_match = 100 if industry in target_inds else 50
        proximity = 100  # 1st degree from export
        role_rel = c.get("usefulness_score", 30)
        engagement = 60 if c.get("tags") else 40
        rank = round(
            0.25 * tier + 0.25 * industry_match + 0.20 * proximity + 0.15 * role_rel + 0.15 * engagement,
            1,
        )
        action = "nurture" if rank >= 75 else ("connect" if rank >= 55 else "follow")
        rows.append({
            "name": c["name"],
            "company": c.get("company", ""),
            "title": c.get("title", ""),
            "seniority": seniority,
            "industry": industry,
            "rank": rank,
            "recommended_action": action,
            "rationale": f"{seniority} in {industry}; usefulness {c.get('usefulness_score', 0)}",
        })

    rows.sort(key=lambda x: -x["rank"])
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows[:20])

    print(f"Top senior targets written to {out}")
    for r in rows[:5]:
        print(f"  {r['rank']} — {r['name']} ({r['recommended_action']})")


if __name__ == "__main__":
    main()