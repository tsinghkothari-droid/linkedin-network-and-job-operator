#!/usr/bin/env python3
"""Build searchable CSV and HTML indexes from network JSON."""

from __future__ import annotations

import argparse
import csv
import html
import json
from pathlib import Path


def build_csv(connections: list[dict], out_csv: Path) -> None:
    fields = [
        "name",
        "company",
        "title",
        "industry",
        "seniority",
        "tags",
        "usefulness_score",
        "profile_url",
        "connected_on",
    ]
    with out_csv.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for c in sorted(connections, key=lambda x: -x["usefulness_score"]):
            writer.writerow(
                {
                    "name": c["name"],
                    "company": c["company"],
                    "title": c["title"],
                    "industry": c["industry"],
                    "seniority": c["seniority"],
                    "tags": ",".join(c["tags"]),
                    "usefulness_score": c["usefulness_score"],
                    "profile_url": c.get("profile_url", ""),
                    "connected_on": c.get("connected_on", ""),
                }
            )


def build_html(connections: list[dict], out_html: Path) -> None:
    rows = []
    for c in sorted(connections, key=lambda x: -x["usefulness_score"]):
        rows.append(
            "<tr>"
            f"<td>{html.escape(c['name'])}</td>"
            f"<td>{html.escape(c['company'])}</td>"
            f"<td>{html.escape(c['title'])}</td>"
            f"<td>{html.escape(c['industry'])}</td>"
            f"<td>{html.escape(c['seniority'])}</td>"
            f"<td>{html.escape(','.join(c['tags']))}</td>"
            f"<td>{c['usefulness_score']}</td>"
            "</tr>"
        )

    content = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Network Index</title>
  <style>
    body {{ font-family: system-ui, sans-serif; margin: 2rem; }}
    input {{ width: 100%; padding: 0.5rem; margin-bottom: 1rem; }}
    table {{ width: 100%; border-collapse: collapse; }}
    th, td {{ border: 1px solid #ddd; padding: 0.5rem; text-align: left; }}
    th {{ background: #f5f5f5; }}
  </style>
</head>
<body>
  <h1>LinkedIn Network Index</h1>
  <input id="search" placeholder="Search name, company, title, industry, tags..." oninput="filterRows()">
  <table id="network">
    <thead>
      <tr>
        <th>Name</th><th>Company</th><th>Title</th><th>Industry</th>
        <th>Seniority</th><th>Tags</th><th>Score</th>
      </tr>
    </thead>
    <tbody>
      {''.join(rows)}
    </tbody>
  </table>
  <script>
    function filterRows() {{
      const q = document.getElementById('search').value.toLowerCase();
      document.querySelectorAll('#network tbody tr').forEach(tr => {{
        tr.style.display = tr.innerText.toLowerCase().includes(q) ? '' : 'none';
      }});
    }}
  </script>
</body>
</html>"""
    out_html.write_text(content, encoding="utf-8")


def build_company_map(connections: list[dict], out_csv: Path) -> None:
    companies: dict[str, dict] = {}
    for c in connections:
        company = c.get("company") or "Unknown"
        entry = companies.setdefault(
            company,
            {
                "company": company,
                "connection_count": 0,
                "recruiter_count": 0,
                "hiring_manager_count": 0,
                "top_targets": [],
            },
        )
        entry["connection_count"] += 1
        tags = c.get("tags", [])
        if "recruiter" in tags:
            entry["recruiter_count"] += 1
        if "hiring_manager" in tags:
            entry["hiring_manager_count"] += 1
        if c["usefulness_score"] >= 60:
            entry["top_targets"].append(c["name"])

    fields = [
        "company",
        "connection_count",
        "recruiter_count",
        "hiring_manager_count",
        "top_targets",
        "best_referral_rank",
    ]
    with out_csv.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for company, entry in sorted(companies.items(), key=lambda x: -x[1]["connection_count"]):
            targets = entry["top_targets"][:3]
            writer.writerow(
                {
                    "company": company,
                    "connection_count": entry["connection_count"],
                    "recruiter_count": entry["recruiter_count"],
                    "hiring_manager_count": entry["hiring_manager_count"],
                    "top_targets": "; ".join(targets),
                    "best_referral_rank": 90 if entry["recruiter_count"] else (75 if targets else 0),
                }
            )


def main() -> None:
    parser = argparse.ArgumentParser(description="Build network indexes")
    parser.add_argument("--network", required=True, help="network.json path")
    parser.add_argument("--out-dir", required=True, help="Output directory")
    args = parser.parse_args()

    data = json.loads(Path(args.network).read_text(encoding="utf-8"))
    connections = data["connections"]
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    build_csv(connections, out_dir / "network_index.csv")
    build_html(connections, out_dir / "network_index.html")
    build_company_map(connections, out_dir / "company_network_map.csv")
    print(f"Indexes written to {out_dir}")


if __name__ == "__main__":
    main()