#!/usr/bin/env python3
"""
Generic LinkedIn intelligence pipeline (Phases B–E).

Prerequisites:
  Phase A: browser verified (exploration snapshots or verify_browser_session.py)
  Phase C: intake_responses.json → subject_profile.json
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve().parent
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))


def run(script: str, args: list[str], check: bool = True) -> None:
    cmd = [sys.executable, str(_SCRIPT_DIR / script), *args]
    print(f"\n>> {' '.join(cmd)}")
    subprocess.run(cmd, check=check)


def write_data_status(ws: Path, export_ok: bool, network_ok: bool, browser_ok: bool) -> None:
    status = {
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "export_parsed": export_ok,
        "network_available": network_ok,
        "browser_snapshots": browser_ok,
        "mode": "full" if network_ok else ("live_only" if browser_ok else "intake_only"),
    }
    (ws / "data_status.json").write_text(json.dumps(status, indent=2), encoding="utf-8")


def write_synthesis_summary(ws: Path, subject: dict, connection_count: int) -> None:
    goal = subject.get("intake", {}).get("primary_goal", "network_expansion")
    summary = {
        "strengths": [
            f"Intake goal defined: {goal.replace('_', ' ')}",
            f"Network connections indexed: {connection_count}",
            "Pipeline modules executed",
        ],
        "gaps": [
            "Increase senior access in target industries" if connection_count else "Upload LinkedIn export for full network graph",
            "Run monthly refresh to update metrics",
        ],
        "priority_week": (
            "Review connection_suggestions.csv and send 3 personalized messages"
            if goal != "job_search"
            else "Review job_pipeline.csv top 3 and draft referral outreach"
        ),
    }
    (ws / "synthesis_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Generic LinkedIn intelligence pipeline")
    parser.add_argument("--workspace", default="linkedin-job-workspace")
    parser.add_argument("--intake", help="intake_responses.json")
    parser.add_argument("--export", help="LinkedIn export ZIP to parse")
    parser.add_argument("--network", help="network.json (skip parse)")
    parser.add_argument("--subject", help="subject_profile.json")
    parser.add_argument("--skip-live", action="store_true", help="Skip scores/drafts from snapshots")
    parser.add_argument("--with-explore", action="store_true", help="Run explore_linkedin.bat first (Windows)")
    args = parser.parse_args()

    root = _SCRIPT_DIR.parent
    ws = Path(args.workspace)
    if not ws.is_absolute():
        ws = root / ws
    ws.mkdir(parents=True, exist_ok=True)

    intake_path = Path(args.intake) if args.intake else ws / "intake_responses.json"
    subject_path = Path(args.subject) if args.subject else ws / "subject_profile.json"
    network_path = Path(args.network) if args.network else ws / "network.json"

    if args.with_explore:
        bat = root / "scripts" / "explore_linkedin.bat"
        if bat.exists():
            subprocess.run(["cmd", "/c", str(bat)], cwd=root, check=False)

    browser_verify = subprocess.run(
        [sys.executable, str(_SCRIPT_DIR / "verify_browser_session.py"), "--workspace", str(ws)],
        check=False,
    )
    browser_ok = browser_verify.returncode == 0

    export_ok = False
    if args.export:
        run("check_export_ready.py", ["--input", args.export], check=False)
        run("parse_linkedin_export.py", ["--input", args.export, "--out", str(network_path)])
        export_ok = network_path.exists()

    if intake_path.exists():
        run("intake_to_profile.py", ["--intake", str(intake_path), "--out", str(subject_path)])
    elif not subject_path.exists():
        example = root / "templates" / "subject_profile_example.json"
        if example.exists():
            subject_path.write_text(example.read_text(encoding="utf-8"), encoding="utf-8")
            print(f"Using example subject profile: {subject_path}")

    if not browser_ok:
        browser_ok = (ws / "exploration" / "snapshots" / "feed.yml").exists()
    network_ok = network_path.exists()

    write_data_status(ws, export_ok, network_ok, browser_ok)

    if network_ok:
        subject = json.loads(subject_path.read_text(encoding="utf-8"))
        network = json.loads(network_path.read_text(encoding="utf-8"))
        conn_count = len(network.get("connections", []))

        run("build_network_index.py", ["--network", str(network_path), "--out-dir", str(ws)])
        run("skills_intelligence.py", ["--subject", str(subject_path), "--out-dir", str(ws)])
        run("sector_opportunity.py", ["--network", str(network_path), "--subject", str(subject_path), "--out", str(ws / "sector_opportunities.csv")])
        run("business_opportunity.py", ["--network", str(network_path), "--subject", str(subject_path), "--out", str(ws / "business_opportunities.md")])
        run("senior_recommendations.py", ["--network", str(network_path), "--subject", str(subject_path), "--out", str(ws / "senior_targets.csv")])
        run("content_recommendations.py", ["--network", str(network_path), "--subject", str(subject_path), "--out", str(ws / "post_recommendations.md")])
        run("connection_suggestions.py", ["--network", str(network_path), "--subject", str(subject_path), "--out", str(ws / "connection_suggestions.csv")])
        run("leadership_intel.py", ["--workspace", str(ws)], check=False)
        write_synthesis_summary(ws, subject, conn_count)
    else:
        print("\n⚠ No network.json — running live-only modules where possible.")
        write_synthesis_summary(ws, json.loads(subject_path.read_text(encoding="utf-8")) if subject_path.exists() else {}, 0)

    if not args.skip_live and (ws / "exploration" / "snapshots").exists():
        run("run_scores_drafts_posts.py", ["--workspace", str(ws), "--subject", str(subject_path)], check=False)

    if subject_path.exists():
        run("compute_metrics_baseline.py", ["--workspace", str(ws), "--subject", str(subject_path)])
        run("generate_action_plan.py", ["--workspace", str(ws), "--subject", str(subject_path)])
        run("build_intelligence_dashboard.py", ["--workspace", str(ws), "--subject", str(subject_path)])
        run("build_dashboard.py", ["--workspace", str(ws)], check=False)

    print(f"\n✓ Generic pipeline complete → {ws}/")
    print(f"  Open: {ws / 'intelligence_dashboard.html'}")


if __name__ == "__main__":
    main()