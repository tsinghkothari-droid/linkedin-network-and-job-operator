#!/usr/bin/env python3
"""Generate post recommendations tuned to subject's network composition."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path


def audience_clusters(connections: list[dict]) -> list[dict]:
    clusters = Counter(
        f"{c.get('industry', 'other')}:{c.get('seniority', 'IC')}" for c in connections
    )
    total = sum(clusters.values()) or 1
    return [
        {"segment": k, "share": round(v / total, 2), "count": v}
        for k, v in clusters.most_common(5)
    ]


def main() -> None:
    parser = argparse.ArgumentParser(description="Content and post recommendations")
    parser.add_argument("--network", required=True)
    parser.add_argument("--subject", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    network = json.loads(Path(args.network).read_text(encoding="utf-8"))
    subject = json.loads(Path(args.subject).read_text(encoding="utf-8"))
    clusters = audience_clusters(network["connections"])
    pillars = subject.get("content_pillars", ["career growth"])
    name = subject.get("name", "Subject")

    ideas = []
    formats = ["7-slide carousel", "long-form text (1,400 chars)", "native video (<30s)"]

    for i, cluster in enumerate(clusters[:3]):
        industry, seniority = cluster["segment"].split(":", 1)
        pillar = pillars[i % len(pillars)]
        fmt = formats[i % len(formats)]
        ideas.append({
            "title": f"What {seniority} professionals in {industry} get wrong about {pillar}",
            "audience_cluster": cluster["segment"],
            "audience_share": f"{cluster['share']:.0%}",
            "format": fmt,
            "hook": f"After 8 years in {pillar}, I keep seeing the same mistake among {industry} leaders.",
            "depth_score_potential": "High" if "carousel" in fmt else "Medium",
            "why_network_cares": f"{cluster['count']} connections in this segment ({cluster['share']:.0%} of network)",
            "cta": f"What has been your experience with {pillar} in {industry}?",
            "avoid": "External links in post body; engagement bait",
        })

    # Timely skills angle
    ideas.append({
        "title": "Skills on the Rise 2026: what recruiters in your network actually want",
        "audience_cluster": "cross-network",
        "audience_share": "100%",
        "format": "7-slide carousel",
        "hook": "LinkedIn's 2026 skills data just dropped. Here is what matters for your next move.",
        "depth_score_potential": "High",
        "why_network_cares": "52% of professionals are job hunting; 80% feel unprepared (LinkedIn 2026)",
        "cta": "Which skill are you investing in this quarter?",
        "avoid": "Linking to external blog — keep insights native",
    })

    # Career goal angle
    if subject.get("career_goal"):
        ideas.append({
            "title": f"My playbook for: {subject['career_goal']}",
            "audience_cluster": "aspiring peers",
            "audience_share": "N/A",
            "format": "long-form text (1,600 chars)",
            "hook": f"I am actively working toward a goal: {subject['career_goal']}",
            "depth_score_potential": "High",
            "why_network_cares": "Personal narrative drives comment depth in 2026 algorithm",
            "cta": "If you have made a similar transition, what would you do differently?",
            "avoid": "Generic motivational content without specifics",
        })

    lines = [
        f"# Post Recommendations: {name}",
        "",
        "## Audience clusters",
        "",
    ]
    for c in clusters:
        lines.append(f"- **{c['segment']}**: {c['count']} connections ({c['share']:.0%})")

    lines.extend(["", "## Post ideas", ""])
    for idea in ideas:
        lines.extend([
            f"### {idea['title']}",
            f"- **Audience:** {idea['audience_cluster']} ({idea['audience_share']})",
            f"- **Format:** {idea['format']}",
            f"- **Hook:** {idea['hook']}",
            f"- **Depth Score potential:** {idea['depth_score_potential']}",
            f"- **Why this network cares:** {idea['why_network_cares']}",
            f"- **CTA:** {idea['cta']}",
            f"- **Avoid:** {idea['avoid']}",
            "",
        ])

    lines.extend([
        "## 3-week content calendar",
        "",
        "| Week | Mon | Wed | Fri |",
        "|------|-----|-----|-----|",
    ])
    for w in range(1, 4):
        idx = (w - 1) * 3
        mon = ideas[idx % len(ideas)]["title"][:40] if ideas else "—"
        wed = ideas[(idx + 1) % len(ideas)]["title"][:40] if len(ideas) > 1 else "—"
        fri = ideas[(idx + 2) % len(ideas)]["title"][:40] if len(ideas) > 2 else "—"
        lines.append(f"| {w} | {mon} | {wed} | {fri} |")

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(lines), encoding="utf-8")
    print(out.read_text(encoding="utf-8"))


if __name__ == "__main__":
    main()