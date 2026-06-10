"""Shared job scoring and draft helpers for live and validation pipelines."""

from __future__ import annotations

import re
from datetime import datetime, timezone


def infer_skills_from_title(title: str) -> list[str]:
    title_l = title.lower()
    buckets = {
        "strategy": ["strategy", "consultant", "advisor", "advisory"],
        "product": ["product", "pm", "program"],
        "ai": ["ai", "machine learning", "data science"],
        "consulting": ["consultant", "consulting", "associate", "analyst"],
        "due_diligence": ["due diligence", "dd", "risk"],
        "govtech": ["govtech", "government", "public sector"],
        "power": ["power", "energy", "utility"],
        "finance": ["finance", "quantitative", "risk management"],
        "leadership": ["director", "head", "vp", "chief"],
    }
    found = []
    for skill, keywords in buckets.items():
        if any(k in title_l for k in keywords):
            found.append(skill.replace("_", " "))
    if not found:
        found = [w for w in re.split(r"[^\w]+", title_l) if len(w) > 3][:5]
    return found


def score_job(job: dict, profile: dict, network: list[dict] | None = None) -> dict:
    network = network or []
    resume_skills = {s.lower() for s in profile.get("skills", [])}
    target_roles = [r.lower() for r in profile.get("target_roles", [])]
    title_l = job.get("title", "").lower()

    req_skills = {s.lower() for s in job.get("required_skills", [])}
    if not req_skills:
        req_skills = {s.lower() for s in infer_skills_from_title(job.get("title", ""))}

    def stems(s: str) -> set[str]:
        parts = re.split(r"[^\w]+", s.lower())
        out = {p for p in parts if len(p) > 3}
        for p in list(out):
            if p.endswith("ing"):
                out.add(p[:-3])
            if p.endswith("ant"):
                out.add(p[:-3] + "ing")
        return out

    title_stems = stems(title_l)
    overlap = set(resume_skills & req_skills)
    for skill in resume_skills:
        if skill in title_l or stems(skill) & title_stems:
            overlap.add(skill)
    for role in target_roles:
        if stems(role) & title_stems or role in title_l:
            overlap.add(role.split()[0] if role else "")
    title_overlap = sum(
        1 for r in target_roles if r in title_l or any(w in title_l for w in r.split() if len(w) > 3)
    )
    fit_base = (len(overlap) / max(len(req_skills), 1)) * 60
    fit_title = min(40, title_overlap * 12)
    fit = min(100, int(fit_base + fit_title + (15 if overlap else 0)))

    relevance = 0
    loc = job.get("location", "").lower()
    for pref in profile.get("preferred_locations", []):
        if pref.lower() in loc or loc in pref.lower():
            relevance += 35
            break
    if any(ind in title_l or ind in job.get("company", "").lower() for ind in profile.get("target_industries", [])):
        relevance += 30
    seniority = profile.get("seniority", "").lower()
    if seniority and seniority in title_l:
        relevance += 20
    if job.get("remote"):
        relevance += 15
    relevance = min(relevance, 100)

    company = job.get("company", "").lower()
    matches = [c for c in network if c.get("company", "").lower() == company]
    if not matches:
        network_score = 0
    elif any("recruiter" in c.get("tags", []) for c in matches):
        network_score = 90
    elif any("hiring_manager" in c.get("tags", []) for c in matches):
        network_score = 75
    else:
        network_score = 50

    effort_map = {"easy_apply": 90, "external": 50, "unknown": 60}
    effort = effort_map.get(job.get("application_type", "unknown"), 60)

    total = round(0.35 * fit + 0.25 * relevance + 0.25 * network_score + 0.15 * effort, 1)

    return {
        "fit_score": fit,
        "relevance_score": relevance,
        "network_score": network_score,
        "effort_score": effort,
        "total_score": total,
    }


def rank_referral_target(company: str, network: list[dict]) -> dict | None:
    matches = [c for c in network if c.get("company", "").lower() == company.lower()]
    if not matches:
        return None

    def rank(c: dict) -> int:
        score = c.get("usefulness_score", 0)
        if "recruiter" in c.get("tags", []):
            score += 15
        if "hiring_manager" in c.get("tags", []):
            score += 10
        return score

    best = max(matches, key=rank)
    return {
        "connection_name": best["name"],
        "connection_title": best.get("title", ""),
        "relationship": "1st",
        "rank": rank(best),
        "status": "not_contacted",
    }


def draft_referral_message(job: dict, target: dict | None, profile: dict) -> str:
    if not target:
        return (
            f"No 1st-degree referral target found at {job.get('company', 'the company')}. "
            "Consider a direct application or a 2nd-degree intro after user review."
        )
    skills = ", ".join(profile.get("skills", [])[:3])
    return (
        f"Hi {target['connection_name']},\n\n"
        f"I saw the {job['title']} role at {job['company']} and it aligns with my background in "
        f"{skills}. "
        f"Would you be open to referring me or pointing me to the right hiring contact?\n\n"
        f"Thanks,\n{profile.get('name', 'Candidate')}"
    )


def draft_cover_letter(job: dict, profile: dict) -> str:
    name = profile.get("name", "Candidate")
    title = profile.get("current_title", "professional")
    skills = ", ".join(profile.get("skills", [])[:4])
    goal = profile.get("career_goal", "my next career step")
    return f"""# Application Draft: {job.get('company')} — {job.get('title')}

**Status:** DRAFT — review and submit yourself. Agent did not apply.

---

Dear Hiring Team,

I am writing to express interest in the {job.get('title')} position at {job.get('company')}. As a {title} with strengths in {skills}, this role fits {goal}.

**Why {job.get('company')}**
- The role matches my focus on {profile.get('target_industries', ['my field'])[0] if profile.get('target_industries') else 'this sector'}.
- Location/work mode ({job.get('location', 'as listed')}) aligns with my preferences.

**What I bring**
{chr(10).join(f'- {s}' for s in profile.get('skills', [])[:6])}

**Honest gaps to address in interview**
- Review the job description and add any gaps you acknowledge here before submitting.

I would welcome a conversation to discuss how I can contribute.

Best regards,
{name}

---
Job URL: {job.get('url', '')}
"""


def draft_linkedin_post(
    *,
    pillar: str,
    profile: dict,
    analytics: dict | None = None,
    post_index: int = 0,
) -> str:
    name = profile.get("name", "").split()[0] if profile.get("name") else "I"
    impressions = (analytics or {}).get("impressions", 0)
    engagements = (analytics or {}).get("engagements", 0)
    growth = (analytics or {}).get("impressions_growth_pct")

    hooks = [
        f"Three things I learned about {pillar} while working across strategy and execution:",
        f"Most {pillar} conversations on LinkedIn miss the hardest part — implementation.",
        f"If you're navigating {pillar} in India right now, this pattern keeps showing up:",
    ]
    hook = hooks[post_index % len(hooks)]

    metrics_line = ""
    if impressions:
        growth_txt = f" (+{growth}% vs last week)" if growth else ""
        metrics_line = (
            f"\n\nI've been testing ideas in public — {impressions:,} impressions and "
            f"{engagements} engagements this week{growth_txt}. "
            "Posting consistently is changing who finds my profile."
        )

    body = f"""{hook}

1/ Context — {pillar} is not a slide deck. It's trade-offs under uncertainty.

2/ Pattern — Teams that win combine domain depth with decision-ready analysis (not more data for its own sake).

3/ Applied AI — Use models to accelerate research and QA, but keep humans accountable for judgment calls.

4/ India lens — Power, GovTech, and regulated sectors need compliance-aware speed, not Silicon Valley copy-paste.

5/ Takeaway — Clarity beats volume. One sharp insight beats five generic posts.

What's the best {pillar} advice you've received this year?{metrics_line}

— {name}

#Strategy #AppliedAI #GovTech #India
"""
    return body.strip()


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()