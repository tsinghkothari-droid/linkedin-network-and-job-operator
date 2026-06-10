#!/usr/bin/env python3
"""Rank connection suggestions from network + intake preferences."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

SENIORITY_SCORE = {
    "C-level": 100, "Founder": 98, "Investor": 95, "VP": 90, "Director": 85,
    "Recruiter": 88, "Advisor": 75, "Manager": 70, "IC": 45,
}


def draft_note(name: str, subject: dict, outreach: int) -> str:
    first = name.split()[0] if name else "there"
    pillar = (subject.get("content_pillars") or ["your work"])[0]
    if outreach <= 2:
        return f"Hi {first} — we share interests in {pillar}. Would value staying connected."
    return (
        f"Hi {first}, I noticed your work in {subject.get('target_industries', ['the industry'])[0]}. "
        f"I'm focused on {pillar} and would enjoy connecting."
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--network", required=True)
    parser.add_argument("--subject", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--limit", type=int, default=15)
    args = parser.parse_args()

    network = json.loads(Path(args.network).read_text(encoding="utf-8"))
    subject = json.loads(Path(args.subject).read_text(encoding="utf-8"))
    target_inds = {i.lower() for i in subject.get("target_industries", [])}
    outreach = int(subject.get("intake", {}).get("outreach_style", 3))

    rows = []
    for c in network.get("connections", []):
        industry = (c.get("industry") or "other").lower()
        seniority = c.get("seniority", "IC")
        tier = SENIORITY_SCORE.get(seniority, 45)
        ind_match = 100 if industry in target_inds else 40
        usefulness = c.get("usefulness_score", 30)
        rank = round(0.35 * tier + 0.30 * ind_match + 0.35 * usefulness, 1)
        action = "nurture" if rank >= 75 else ("connect" if rank >= 55 else "follow")
        rows.append({
            "name": c.get("name", ""),
            "company": c.get("company", ""),
            "title": c.get("title", ""),
            "seniority": seniority,
            "industry": industry,
            "rank": rank,
            "suggested_action": action,
            "draft_note": draft_note(c.get("name", ""), subject, outreach),
            "profile_url": c.get("profile_url", ""),
        })

    rows.sort(key=lambda x: -x["rank"])
    rows = rows[: args.limit]

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    if rows:
        with out.open("w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
            writer.writeheader()
            writer.writerows(rows)
    print(f"Wrote {len(rows)} connection suggestions → {out}")


if __name__ == "__main__":
    main()