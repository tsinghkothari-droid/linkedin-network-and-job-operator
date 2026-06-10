#!/usr/bin/env python3
"""Detect business opportunities from network structure."""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser(description="Business opportunity finder")
    parser.add_argument("--network", required=True)
    parser.add_argument("--subject", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    network = json.loads(Path(args.network).read_text(encoding="utf-8"))
    subject = json.loads(Path(args.subject).read_text(encoding="utf-8"))
    connections = network["connections"]

    by_company: dict[str, list] = defaultdict(list)
    recruiters = []
    founders = []
    hiring_managers = []

    for c in connections:
        by_company[c.get("company", "Unknown")].append(c)
        tags = c.get("tags", [])
        if "recruiter" in tags:
            recruiters.append(c)
        if "founder" in tags:
            founders.append(c)
        if "hiring_manager" in tags:
            hiring_managers.append(c)

    opps = []

    if len(recruiters) >= 2:
        opps.append({
            "type": "talent_placement",
            "title": "Referral-side pipeline via recruiter concentration",
            "detail": f"{len(recruiters)} recruiter connections — warm path to multiple reqs",
            "next_step": "Ask top 2 recruiters about open roles matching subject skills",
        })

    if founders:
        subject_skills = set(s.lower() for s in subject.get("skills", []))
        for f in founders[:3]:
            opps.append({
                "type": "co-founder_advisory",
                "title": f"Advisory opportunity with {f['name']} at {f['company']}",
                "detail": f"Founder connection; subject skills: {', '.join(list(subject_skills)[:3])}",
                "next_step": f"Offer office hours or GTM/product advisory to {f['name']}",
            })

    dense_sectors = sorted(by_company.items(), key=lambda x: -len(x[1]))[:3]
    for company, people in dense_sectors:
        seniors = [p for p in people if p.get("usefulness_score", 0) >= 70]
        if seniors:
            opps.append({
                "type": "warm_intro_arbitrage",
                "title": f"Intro hub at {company}",
                "detail": f"{len(people)} connections, {len(seniors)} high-value targets",
                "next_step": f"Map intro paths through {seniors[0]['name']}",
            })

    if subject.get("content_pillars"):
        opps.append({
            "type": "thought_leadership",
            "title": "Content monetization via underserved network topics",
            "detail": f"Pillars: {', '.join(subject['content_pillars'])}",
            "next_step": "Run content_recommendations.py for post calendar",
        })

    lines = [f"# Business Opportunities: {subject.get('name', 'Subject')}", ""]
    for o in opps:
        lines.extend([
            f"## {o['title']}",
            f"- **Type:** {o['type']}",
            f"- **Detail:** {o['detail']}",
            f"- **Next step:** {o['next_step']}",
            "",
        ])

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(lines), encoding="utf-8")
    print(out.read_text(encoding="utf-8"))


if __name__ == "__main__":
    main()