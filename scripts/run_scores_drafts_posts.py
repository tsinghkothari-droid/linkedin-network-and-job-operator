#!/usr/bin/env python3
"""
Scores jobs, drafts application/referral packs, and drafts LinkedIn posts.

Human-in-the-loop: nothing is submitted or published automatically.
"""

from __future__ import annotations

import argparse
import csv
import json
import subprocess
import sys
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve().parent
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))

from parse_jobs_from_snapshot import parse_snapshots_dir  # noqa: E402
from parse_analytics_from_snapshot import parse_creator_analytics  # noqa: E402
from pipeline_scoring import (  # noqa: E402
    draft_cover_letter,
    draft_linkedin_post,
    draft_referral_message,
    rank_referral_target,
    score_job,
    utc_now,
)


def load_json(path: Path, default: dict | list) -> dict | list:
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    return default


def main() -> None:
    parser = argparse.ArgumentParser(description="Score jobs, draft applications, draft posts")
    parser.add_argument("--workspace", default="linkedin-job-workspace")
    parser.add_argument("--subject", help="subject_profile.json path")
    parser.add_argument("--network", help="network.json path (optional)")
    parser.add_argument("--top-jobs", type=int, default=3, help="How many jobs get full application drafts")
    parser.add_argument("--top-posts", type=int, default=3, help="How many post drafts to generate")
    args = parser.parse_args()

    skill_root = Path(__file__).resolve().parent.parent
    workspace = Path(args.workspace)
    if not workspace.is_absolute():
        workspace = skill_root / workspace
    workspace.mkdir(parents=True, exist_ok=True)

    subject_path = Path(args.subject) if args.subject else workspace / "subject_profile.json"
    if not subject_path.exists():
        subject_path = skill_root / "templates" / "subject_profile_example.json"
    profile = load_json(subject_path, {})

    network_path = Path(args.network) if args.network else workspace / "network.json"
    network_data = load_json(network_path, {"connections": []})
    connections = network_data.get("connections", []) if isinstance(network_data, dict) else []

    snap_dir = workspace / "exploration" / "snapshots"
    jobs = parse_snapshots_dir(snap_dir) if snap_dir.exists() else []
    if not jobs:
        print("No jobs-*.yml snapshots found. Run scripts/explore_linkedin.bat first.")
        jobs = []

    analytics_path = snap_dir / "creator-analytics.yml"
    analytics = {}
    if analytics_path.exists():
        analytics = parse_creator_analytics(analytics_path.read_text(encoding="utf-8", errors="ignore"))

    drafts_dir = workspace / "application_drafts"
    posts_dir = workspace / "post_drafts"
    drafts_dir.mkdir(parents=True, exist_ok=True)
    posts_dir.mkdir(parents=True, exist_ok=True)

    pipeline_rows = []
    referral_rows = []
    outreach_sections = []
    score_sections = []

    for job in jobs:
        scores = score_job(job, profile, connections)
        target = rank_referral_target(job.get("company", ""), connections)
        referral_msg = draft_referral_message(job, target, profile)

        row = {
            "job_id": job["job_id"],
            "title": job["title"],
            "company": job.get("company", ""),
            "location": job.get("location", ""),
            "url": job.get("url", ""),
            "posted_date": job.get("posted_date", ""),
            "application_type": job.get("application_type", "unknown"),
            **scores,
            "status": "draft_ready" if scores["total_score"] >= 50 else "discovered",
            "referral_target": target["connection_name"] if target else "",
            "notes": f"source={job.get('source_snapshot', '')}",
            "created_at": utc_now(),
            "updated_at": utc_now(),
        }
        pipeline_rows.append(row)

        if target:
            referral_rows.append({
                "company": job.get("company", ""),
                "job_id": job["job_id"],
                "connection_name": target["connection_name"],
                "connection_title": target["connection_title"],
                "relationship": target["relationship"],
                "rank": target["rank"],
                "status": target["status"],
                "message_draft_path": f"application_drafts/{job['job_id']}_referral.txt",
                "last_updated": utc_now(),
            })

        outreach_sections.append(f"## {job.get('company', '')} — {job['title']}\n\n{referral_msg}\n")

    pipeline_rows.sort(key=lambda r: float(r.get("total_score", 0)), reverse=True)

    for row in pipeline_rows:
        score_sections.append(
            f"### {row['title']} @ {row.get('company', '?')}\n"
            f"- **Total:** {row['total_score']} | Fit {row['fit_score']} | "
            f"Relevance {row['relevance_score']} | Network {row['network_score']} | "
            f"Effort {row['effort_score']}\n"
            f"- **URL:** {row.get('url', '')}\n"
        )

    if pipeline_rows:
        fields = list(pipeline_rows[0].keys())
        with (workspace / "job_pipeline.csv").open("w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fields)
            writer.writeheader()
            writer.writerows(pipeline_rows)

    if referral_rows:
        with (workspace / "referral_targets.csv").open("w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=list(referral_rows[0].keys()))
            writer.writeheader()
            writer.writerows(referral_rows)

    (workspace / "outreach_messages.md").write_text(
        "# Referral message drafts\n\n**Not sent automatically.**\n\n" + "\n".join(outreach_sections),
        encoding="utf-8",
    )

    for job in pipeline_rows[: args.top_jobs]:
        jid = job["job_id"]
        full_job = next((j for j in jobs if j["job_id"] == jid), job)
        (drafts_dir / f"{jid}_cover_letter.md").write_text(
            draft_cover_letter(full_job, profile), encoding="utf-8"
        )
        target = rank_referral_target(full_job.get("company", ""), connections)
        (drafts_dir / f"{jid}_referral.txt").write_text(
            draft_referral_message(full_job, target, profile), encoding="utf-8"
        )

    pillars = profile.get("content_pillars", ["career growth", "strategy", "applied AI"])
    post_sections = ["# LinkedIn post drafts", "", "**Review and publish yourself.**", ""]
    for i in range(args.top_posts):
        pillar = pillars[i % len(pillars)]
        body = draft_linkedin_post(
            pillar=pillar,
            profile=profile,
            analytics=analytics if i == 0 else None,
            post_index=i,
        )
        fname = f"post_{i + 1}_{pillar.replace(' ', '_')[:20]}.md"
        (posts_dir / fname).write_text(body, encoding="utf-8")
        post_sections.extend([f"## Draft {i + 1}: {pillar}", "", "```", body, "```", ""])

    (workspace / "post_drafts.md").write_text("\n".join(post_sections), encoding="utf-8")

    report = [
        "# Scores, Drafts & Posts Report",
        "",
        f"**Subject:** {profile.get('name', 'Unknown')}",
        f"**Jobs parsed:** {len(jobs)}",
        f"**Application drafts:** top {min(args.top_jobs, len(pipeline_rows))}",
        f"**Post drafts:** {args.top_posts}",
        "",
        "## Analytics (from creator snapshot)",
        "",
        json.dumps(analytics, indent=2) if analytics else "_No creator-analytics.yml found_",
        "",
        "## Job scores (ranked)",
        "",
        *score_sections,
        "",
        "## Outputs",
        "",
        f"- `{workspace / 'job_pipeline.csv'}`",
        f"- `{workspace / 'outreach_messages.md'}`",
        f"- `{workspace / 'post_drafts.md'}`",
        f"- `{drafts_dir}/`",
        f"- `{posts_dir}/`",
        "",
        "**You must:** review drafts, send messages, and publish posts yourself.",
    ]
    report_path = workspace / "scores_drafts_posts_report.md"
    report_path.write_text("\n".join(report), encoding="utf-8")

    if pipeline_rows:
        subprocess.run(
            [sys.executable, str(skill_root / "scripts" / "build_dashboard.py"), "--workspace", str(workspace)],
            check=False,
        )

    print(report_path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    main()