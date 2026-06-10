#!/usr/bin/env python3
"""Merge intake responses into subject_profile.json for generic pipeline."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

GOAL_TO_CAREER = {
    "job_search": "Land a new role aligned with my skills and target industries",
    "consulting_bd": "Grow consulting and client revenue through my network",
    "thought_leadership": "Build visibility and authority in my field",
    "career_pivot": "Transition to a new industry or function",
    "network_expansion": "Expand strategic professional relationships",
    "fundraising": "Connect with investors and partners",
    "hiring": "Build a team and employer brand",
}

SENIORITY_MAP = {
    "ic": "Senior",
    "manager": "Manager",
    "director_plus": "Director",
    "founder": "Founder",
    "advisor": "Advisor",
}

CADENCE_PILLARS = {
    "rarely": [],
    "monthly": ["industry insight"],
    "biweekly": ["industry insight", "career lesson"],
    "weekly": ["industry insight", "career lesson", "behind the scenes"],
    "multi_weekly": ["industry insight", "career lesson", "behind the scenes", "commentary"],
}

GOAL_BASE_ROLES = {
    "job_search": ["Product Management", "Strategy", "Operations"],
    "consulting_bd": ["Consulting", "Business Development", "Advisory"],
    "thought_leadership": ["Thought Leadership", "Advisory", "Speaking"],
    "career_pivot": ["Transition Role", "Cross-functional Lead", "Program Management"],
    "network_expansion": ["Partnerships", "Business Development", "Community"],
    "fundraising": ["Fundraising", "Investor Relations", "Partnerships"],
    "hiring": ["Talent Acquisition", "People Operations", "Employer Brand"],
}

SENIORITY_ROLE_OVERRIDES = {
    "ic": ["Senior IC", "Staff", "Principal"],
    "manager": ["Manager", "Senior Manager", "Team Lead"],
    "director_plus": ["Director", "Senior Director", "VP"],
    "founder": ["Founder", "Co-founder", "CEO"],
    "advisor": ["Advisor", "Board Member", "Consultant"],
}


def target_roles_for(goal: str, seniority: str, explicit: list[str] | None) -> list[str]:
    if explicit:
        return explicit
    seniority_roles = SENIORITY_ROLE_OVERRIDES.get(seniority, [])
    if goal in ("job_search", "career_pivot") and seniority_roles:
        return seniority_roles
    return GOAL_BASE_ROLES.get(goal, GOAL_BASE_ROLES["network_expansion"])


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--intake", required=True)
    parser.add_argument("--profile-source", help="Optional Profile.csv or subject stub JSON")
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    intake = json.loads(Path(args.intake).read_text(encoding="utf-8"))
    answers = intake.get("answers", intake)

    name = answers.get("name", "Professional")
    title = answers.get("current_title", "Professional")
    skills = answers.get("skills", ["communication", "strategy"])

    if args.profile_source and Path(args.profile_source).exists():
        src = Path(args.profile_source)
        if src.suffix == ".json":
            stub = json.loads(src.read_text(encoding="utf-8"))
            name = stub.get("name", name)
            title = stub.get("current_title", title)
            skills = stub.get("skills", skills)

    industries = answers.get("industry_focus", ["tech"])
    if isinstance(industries, str):
        industries = [industries]

    geo = answers.get("geo_focus", "country")
    locations = ["remote"] if geo == "global_remote" else [answers.get("city", geo)]

    goal_key = answers.get("primary_goal", "network_expansion")
    cadence = answers.get("content_cadence", "monthly")
    seniority_path = answers.get("seniority_path", "manager")

    profile = {
        "name": name,
        "mode": "subject",
        "current_title": title,
        "seniority": SENIORITY_MAP.get(seniority_path, "Manager"),
        "skills": skills,
        "target_roles": target_roles_for(
            goal_key,
            seniority_path,
            answers.get("target_roles"),
        ),
        "target_industries": industries,
        "preferred_locations": locations,
        "years_experience": answers.get("years_experience", 5),
        "visa_needs": answers.get("visa_needs", "none"),
        "career_goal": GOAL_TO_CAREER.get(goal_key, GOAL_TO_CAREER["network_expansion"]),
        "content_pillars": CADENCE_PILLARS.get(cadence, ["industry insight"]),
        "intake": {
            "primary_goal": goal_key,
            "time_horizon": answers.get("time_horizon", 2),
            "geo_focus": geo,
            "industry_focus": industries,
            "seniority_path": answers.get("seniority_path", "manager"),
            "outreach_style": answers.get("outreach_style", 3),
            "content_cadence": cadence,
        },
    }

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(profile, indent=2), encoding="utf-8")
    print(f"Wrote {out}")


if __name__ == "__main__":
    main()