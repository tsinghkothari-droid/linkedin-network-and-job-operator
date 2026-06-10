#!/usr/bin/env python3
"""Generate application_status_dashboard.html from workspace CSVs."""

from __future__ import annotations

import argparse
import csv
import html
from pathlib import Path


def read_csv(path: Path) -> list[dict]:
    if not path.exists():
        return []
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def main() -> None:
    parser = argparse.ArgumentParser(description="Build application status dashboard")
    parser.add_argument("--workspace", required=True, help="Workspace directory")
    args = parser.parse_args()

    workspace = Path(args.workspace)
    jobs = read_csv(workspace / "job_pipeline.csv")
    referrals = read_csv(workspace / "referral_targets.csv")

    job_rows = []
    for j in jobs:
        job_rows.append(
            "<tr>"
            f"<td>{html.escape(j.get('company', ''))}</td>"
            f"<td>{html.escape(j.get('title', ''))}</td>"
            f"<td>{html.escape(j.get('total_score', ''))}</td>"
            f"<td>{html.escape(j.get('status', ''))}</td>"
            f"<td>{html.escape(j.get('referral_target', ''))}</td>"
            f"<td><a href=\"{html.escape(j.get('url', ''))}\">Job</a></td>"
            "</tr>"
        )

    referral_rows = []
    for r in referrals:
        referral_rows.append(
            "<tr>"
            f"<td>{html.escape(r.get('company', ''))}</td>"
            f"<td>{html.escape(r.get('connection_name', ''))}</td>"
            f"<td>{html.escape(r.get('status', ''))}</td>"
            f"<td>{html.escape(r.get('rank', ''))}</td>"
            "</tr>"
        )

    content = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Application Status Dashboard</title>
  <style>
    body {{ font-family: system-ui, sans-serif; margin: 2rem; color: #111; }}
    h1, h2 {{ margin-bottom: 0.5rem; }}
    table {{ width: 100%; border-collapse: collapse; margin-bottom: 2rem; }}
    th, td {{ border: 1px solid #ddd; padding: 0.5rem; text-align: left; }}
    th {{ background: #f0f4f8; }}
    .note {{ color: #555; font-size: 0.9rem; }}
  </style>
</head>
<body>
  <h1>Application Status Dashboard</h1>
  <p class="note">Human review required before any submission. No auto-submit enabled.</p>

  <h2>Job Pipeline ({len(jobs)})</h2>
  <table>
    <thead>
      <tr><th>Company</th><th>Role</th><th>Score</th><th>Status</th><th>Referral Target</th><th>Link</th></tr>
    </thead>
    <tbody>{''.join(job_rows) if job_rows else '<tr><td colspan="6">No jobs yet</td></tr>'}</tbody>
  </table>

  <h2>Referral Targets ({len(referrals)})</h2>
  <table>
    <thead>
      <tr><th>Company</th><th>Connection</th><th>Status</th><th>Rank</th></tr>
    </thead>
    <tbody>{''.join(referral_rows) if referral_rows else '<tr><td colspan="4">No referrals yet</td></tr>'}</tbody>
  </table>
</body>
</html>"""

    out = workspace / "application_status_dashboard.html"
    out.write_text(content, encoding="utf-8")
    print(f"Dashboard written to {out}")


if __name__ == "__main__":
    main()