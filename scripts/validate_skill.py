#!/usr/bin/env python3
"""
Validate skill on 3 sample jobs.
Produces scores, referral targets, draft messages, and checklists.
Does NOT submit anything.
"""

from __future__ import annotations

import argparse
import csv
import json
from datetime import datetime, timezone
from pathlib import Path


def score_job(job: dict, profile: dict, network: list[dict]) -> dict:
    resume_skills = set(s.lower() for s in profile.get("skills", []))
    req_skills = set(s.lower() for s in job.get("required_skills", []))
    overlap = resume_skills & req_skills
    fit = min(100, int((len(overlap) / max(len(req_skills), 1)) * 80 + 20))

    relevance = 0
    if job.get("location", "").lower() in profile.get("preferred_locations", []):
        relevance += 30
    if job.get("industry", "").lower() in profile.get("target_industries", []):
        relevance += 30
    if job.get("seniority", "").lower() in profile.get("seniority", "").lower():
        relevance += 25
    relevance = min(relevance, 100)

    company = job["company"].lower()
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
        "connection_title": best["title"],
        "relationship": "1st",
        "rank": rank(best),
        "status": "not_contacted",
    }


def draft_referral_message(job: dict, target: dict | None, profile: dict) -> str:
    if not target:
        return "No referral target in network. Consider applying directly after user review."
    return (
        f"Hi {target['connection_name']},\n\n"
        f"I saw the {job['title']} role at {job['company']} and it aligns with my background in "
        f"{', '.join(profile.get('skills', [])[:3])}. "
        f"Would you be open to referring me or pointing me to the right hiring contact?\n\n"
        f"Thanks,\n{profile.get('name', 'Candidate')}"
    )


def application_checklist(job: dict) -> list[str]:
    return [
        f"Job summary reviewed: {job['title']} at {job['company']}",
        "Resume gaps acknowledged",
        "Cover letter / answers drafted",
        "Referral outreach drafted (not sent automatically)",
        "Form fields not prefilled in validation mode",
        "USER APPROVAL REQUIRED — no submission performed",
    ]


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate linkedin-network-and-job-operator skill")
    parser.add_argument("--workspace", required=True, help="Validation output directory")
    parser.add_argument("--data-dir", default=None, help="Sample data directory")
    args = parser.parse_args()

    skill_root = Path(__file__).resolve().parent.parent
    data_dir = Path(args.data_dir) if args.data_dir else skill_root / "validation" / "sample_data"
    out_dir = Path(args.workspace)
    out_dir.mkdir(parents=True, exist_ok=True)
    drafts_dir = out_dir / "application_drafts"
    drafts_dir.mkdir(exist_ok=True)

    network = json.loads((data_dir / "network.json").read_text(encoding="utf-8"))["connections"]
    profile = json.loads((data_dir / "profile.json").read_text(encoding="utf-8"))
    jobs = json.loads((skill_root / "validation" / "sample_jobs.json").read_text(encoding="utf-8"))

    pipeline_rows = []
    referral_rows = []
    outreach_sections = []
    report_sections = []

    for job in jobs:
        scores = score_job(job, profile, network)
        target = rank_referral_target(job["company"], network)
        message = draft_referral_message(job, target, profile)
        checklist = application_checklist(job)

        job_id = job["job_id"]
        pipeline_rows.append(
            {
                "job_id": job_id,
                "title": job["title"],
                "company": job["company"],
                "location": job.get("location", ""),
                "url": job.get("url", ""),
                "posted_date": job.get("posted_date", ""),
                "application_type": job.get("application_type", "unknown"),
                **scores,
                "status": "draft_ready",
                "referral_target": target["connection_name"] if target else "",
                "notes": "Validation run — no submission",
                "created_at": datetime.now(timezone.utc).isoformat(),
                "updated_at": datetime.now(timezone.utc).isoformat(),
            }
        )

        if target:
            referral_rows.append(
                {
                    "company": job["company"],
                    "job_id": job_id,
                    "connection_name": target["connection_name"],
                    "connection_title": target["connection_title"],
                    "relationship": target["relationship"],
                    "rank": target["rank"],
                    "status": target["status"],
                    "message_draft_path": f"application_drafts/{job_id}_referral.txt",
                    "last_updated": datetime.now(timezone.utc).isoformat(),
                }
            )
            (drafts_dir / f"{job_id}_referral.txt").write_text(message, encoding="utf-8")

        outreach_sections.append(f"## {job['company']} — {job['title']}\n\n{message}\n")
        report_sections.append(
            f"### {job['title']} @ {job['company']}\n"
            f"- **Total score:** {scores['total_score']}\n"
            f"- **Fit:** {scores['fit_score']} | **Relevance:** {scores['relevance_score']} | "
            f"**Network:** {scores['network_score']} | **Effort:** {scores['effort_score']}\n"
            f"- **Referral target:** {(target or {}).get('connection_name', 'None')}\n"
            f"- **Checklist:**\n"
            + "\n".join(f"  - {item}" for item in checklist)
            + "\n"
        )

    pipeline_fields = list(pipeline_rows[0].keys()) if pipeline_rows else []
    with (out_dir / "job_pipeline.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=pipeline_fields)
        writer.writeheader()
        writer.writerows(pipeline_rows)

    if referral_rows:
        with (out_dir / "referral_targets.csv").open("w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=list(referral_rows[0].keys()))
            writer.writeheader()
            writer.writerows(referral_rows)

    (out_dir / "outreach_messages.md").write_text("\n".join(outreach_sections), encoding="utf-8")
    (out_dir / "validation_report.md").write_text(
        "# Validation Report (3 Sample Jobs)\n\n"
        "**No applications submitted.**\n\n"
        + "\n".join(report_sections),
        encoding="utf-8",
    )

    # Reuse company map builder
    import subprocess
    import sys

    network_path = data_dir / "network.json"
    subprocess.run(
        [sys.executable, str(skill_root / "scripts" / "build_network_index.py"),
         "--network", str(network_path), "--out-dir", str(out_dir)],
        check=True,
    )
    subprocess.run(
        [sys.executable, str(skill_root / "scripts" / "build_dashboard.py"),
         "--workspace", str(out_dir)],
        check=True,
    )

    print((out_dir / "validation_report.md").read_text(encoding="utf-8"))


if __name__ == "__main__":
    main()