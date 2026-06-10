#!/usr/bin/env python3
"""Run full intelligence pipeline on subject profile + network data."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


def run(script: str, args: list[str]) -> None:
    root = Path(__file__).resolve().parent
    cmd = [sys.executable, str(root / script), *args]
    print(f"\n>> {' '.join(cmd)}")
    subprocess.run(cmd, check=True)


def main() -> None:
    parser = argparse.ArgumentParser(description="Run intelligence pipeline")
    parser.add_argument("--subject", required=True, help="subject_profile.json")
    parser.add_argument("--network", required=True, help="network.json")
    parser.add_argument("--workspace", default="linkedin-job-workspace")
    args = parser.parse_args()

    ws = Path(args.workspace)
    ws.mkdir(parents=True, exist_ok=True)

    run("build_network_index.py", ["--network", args.network, "--out-dir", str(ws)])
    run("skills_intelligence.py", ["--subject", args.subject, "--out-dir", str(ws)])
    run("sector_opportunity.py", ["--network", args.network, "--subject", args.subject, "--out", str(ws / "sector_opportunities.csv")])
    run("business_opportunity.py", ["--network", args.network, "--subject", args.subject, "--out", str(ws / "business_opportunities.md")])
    run("senior_recommendations.py", ["--network", args.network, "--subject", args.subject, "--out", str(ws / "senior_targets.csv")])
    run("content_recommendations.py", ["--network", args.network, "--subject", args.subject, "--out", str(ws / "post_recommendations.md")])
    run("build_dashboard.py", ["--workspace", str(ws)])

    print(f"\nPipeline complete. Outputs in {ws}/")


if __name__ == "__main__":
    main()