#!/usr/bin/env python3
"""Generate skills roadmap for a subject profile (may differ from operator)."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def load_macro_weights(data_dir: Path) -> dict[str, int]:
    macro = json.loads((data_dir / "skills_on_the_rise_2026.json").read_text(encoding="utf-8"))
    weights: dict[str, int] = {}
    for cluster in macro["clusters"]:
        for item in cluster["skills"]:
            weights[item["skill"].lower()] = item["demand_weight"]
    return weights


def required_skills_for_roles(macro_path: Path, roles: list[str]) -> list[str]:
    macro = json.loads(macro_path.read_text(encoding="utf-8"))
    req = macro.get("role_skill_requirements", {})
    skills: list[str] = []
    for role in roles:
        skills.extend(req.get(role, []))
    # dedupe preserve order
    seen = set()
    out = []
    for s in skills:
        key = s.lower()
        if key not in seen:
            seen.add(key)
            out.append(s)
    return out


def recommend_agent_skills(subject: dict) -> list[dict]:
    """Meta-recommendation: new agent skills the subject should build."""
    recs = []
    targets = [r.lower() for r in subject.get("target_roles", [])]
    industries = [i.lower() for i in subject.get("target_industries", [])]

    if any("product" in r for r in targets) and "fintech" in industries:
        recs.append({
            "skill_name": "fintech-pm-interview-prep",
            "reason": "Subject targets fintech PM roles — dedicated interview prep skill",
            "triggers": ["fintech pm interview", "payments product interview"],
        })
    if subject.get("career_goal", "").lower().find("transition") >= 0:
        recs.append({
            "skill_name": "career-transition-operator",
            "reason": "Explicit career transition goal detected",
            "triggers": ["career pivot plan", "transition roadmap"],
        })
    if subject.get("content_pillars"):
        recs.append({
            "skill_name": "linkedin-carousel-builder",
            "reason": "Content pillars defined — carousel format dominates 2026 algorithm",
            "triggers": ["build linkedin carousel", "create slide post"],
        })
    if any("engineer" in r or "developer" in r for r in targets):
        recs.append({
            "skill_name": "technical-portfolio-reviewer",
            "reason": "Technical target roles benefit from portfolio review skill",
            "triggers": ["review my github", "engineering portfolio"],
        })
    return recs


def main() -> None:
    parser = argparse.ArgumentParser(description="Skills intelligence for subject profile")
    parser.add_argument("--subject", required=True, help="subject_profile.json path")
    parser.add_argument("--out-dir", required=True, help="Output directory")
    args = parser.parse_args()

    skill_root = Path(__file__).resolve().parent.parent
    data_dir = skill_root / "data"
    subject = json.loads(Path(args.subject).read_text(encoding="utf-8"))
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    possessed = {s.lower() for s in subject.get("skills", [])}
    target_roles = subject.get("target_roles", [])
    required = required_skills_for_roles(data_dir / "skills_on_the_rise_2026.json", target_roles)
    macro_weights = load_macro_weights(data_dir)

    gaps = []
    for skill in required:
        key = skill.lower()
        if key not in possessed:
            demand = macro_weights.get(key, 70)
            gaps.append({
                "skill": skill,
                "demand_weight": demand,
                "priority_score": demand,
                "horizon": "immediate" if demand >= 90 else ("medium" if demand >= 80 else "stretch"),
            })

    gaps.sort(key=lambda x: -x["priority_score"])
    agent_skills = recommend_agent_skills(subject)

    payload = {
        "subject": subject.get("name"),
        "target_roles": target_roles,
        "gaps": gaps[:15],
        "recommended_agent_skills": agent_skills,
    }
    (out_dir / "skills_roadmap.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")

    lines = [
        f"# Skills Roadmap: {subject.get('name', 'Subject')}",
        "",
        f"**Career goal:** {subject.get('career_goal', 'Not specified')}",
        f"**Target roles:** {', '.join(target_roles)}",
        "",
        "## Top skills to build",
        "",
    ]
    for i, g in enumerate(gaps[:10], 1):
        lines.append(f"{i}. **{g['skill']}** — priority {g['priority_score']}, horizon: {g['horizon']}")

    lines.extend(["", "## Add to LinkedIn profile first", ""])
    for g in gaps[:5]:
        lines.append(f"- {g['skill']}")

    lines.extend(["", "## Recommended new agent skills to create", ""])
    for r in agent_skills:
        lines.append(f"### `{r['skill_name']}`")
        lines.append(f"- **Why:** {r['reason']}")
        lines.append(f"- **Triggers:** {', '.join(r['triggers'])}")
        lines.append("")

    (out_dir / "skills_roadmap.md").write_text("\n".join(lines), encoding="utf-8")
    (out_dir / "recommended_agent_skills.md").write_text(
        "\n".join(
            f"## {r['skill_name']}\n{r['reason']}\nTriggers: {', '.join(r['triggers'])}\n"
            for r in agent_skills
        ) or "No agent skill recommendations for this profile.",
        encoding="utf-8",
    )
    print((out_dir / "skills_roadmap.md").read_text(encoding="utf-8"))


if __name__ == "__main__":
    main()