#!/usr/bin/env python3
"""Build fixed-layout intelligence dashboard HTML for any user."""

from __future__ import annotations

import argparse
import csv
import html
import json
from pathlib import Path


def read_csv(path: Path) -> list[dict]:
    if not path.exists():
        return []
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def md_excerpt(path: Path, max_lines: int = 40) -> str:
    if not path.exists():
        return "_Not available yet._"
    lines = path.read_text(encoding="utf-8", errors="ignore").splitlines()[:max_lines]
    return "\n".join(lines)


def table_from_rows(rows: list[dict], columns: list[str] | None = None) -> str:
    if not rows:
        return "<p class='muted'>No data yet.</p>"
    cols = columns or list(rows[0].keys())
    head = "".join(f"<th>{html.escape(c)}</th>" for c in cols)
    body = []
    for r in rows:
        body.append("<tr>" + "".join(f"<td>{html.escape(str(r.get(c, '')))}</td>" for c in cols) + "</tr>")
    return f"<table><thead><tr>{head}</tr></thead><tbody>{''.join(body)}</tbody></table>"


def metric_rows(baseline: dict, definitions: list[dict]) -> list[dict]:
    metrics = baseline.get("metrics", {})
    rows = []
    for d in definitions:
        mid = d["id"]
        cur = metrics.get(mid, {}).get("current", "—")
        target = d.get("target_value") or d.get("target_delta") or d.get("target_delta_pct", "—")
        gap = "—"
        if isinstance(cur, (int, float)) and isinstance(target, (int, float)):
            gap = round(target - cur, 1) if d.get("unit") != "percent" else f"+{target}%"
        rows.append({
            "Metric": d["name"],
            "Current": cur,
            "6mo Target": target,
            "Gap": gap,
            "Next action": (d.get("actions") or [""])[0],
        })
    return rows


def should_show_jobs(subject: dict) -> bool:
    goal = subject.get("intake", {}).get("primary_goal", "")
    return goal in ("job_search", "career_pivot")


def should_show_content(subject: dict) -> bool:
    return subject.get("intake", {}).get("content_cadence", "monthly") != "rarely"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--workspace", required=True)
    parser.add_argument("--subject", help="subject_profile.json")
    args = parser.parse_args()

    root = Path(__file__).resolve().parent.parent
    ws = Path(args.workspace)
    subject_path = Path(args.subject) if args.subject else ws / "subject_profile.json"
    subject = {}
    if subject_path.exists():
        subject = json.loads(subject_path.read_text(encoding="utf-8"))

    summary = {}
    if (ws / "synthesis_summary.json").exists():
        summary = json.loads((ws / "synthesis_summary.json").read_text(encoding="utf-8"))

    baseline = {}
    if (ws / "metrics_baseline.json").exists():
        baseline = json.loads((ws / "metrics_baseline.json").read_text(encoding="utf-8"))

    defs = json.loads((root / "templates" / "growth_metrics.json").read_text(encoding="utf-8"))["metrics"]

    strengths = summary.get("strengths", ["Strong network export parsed", "Clear primary goal from intake"])
    gaps = summary.get("gaps", ["Add live exploration for viewer metrics", "Increase senior access in target sectors"])
    priority = summary.get("priority_week", "Review connection_suggestions.csv — send 3 nurture messages")

    connections = read_csv(ws / "connection_suggestions.csv") or read_csv(ws / "senior_targets.csv")
    jobs = read_csv(ws / "job_pipeline.csv")
    sectors = read_csv(ws / "sector_opportunities.csv")

    name = html.escape(subject.get("name", "Professional"))
    goal = html.escape(subject.get("intake", {}).get("primary_goal", "network").replace("_", " "))

    sections = []

    sections.append(f"""
    <section id="executive">
      <h2>Executive Summary</h2>
      <p class="lede">Intelligence dashboard for <strong>{name}</strong> — goal: <strong>{goal}</strong></p>
      <div class="grid three">
        <div class="card"><h3>Strengths</h3><ul>{''.join(f'<li>{html.escape(s)}</li>' for s in strengths)}</ul></div>
        <div class="card"><h3>Gaps</h3><ul>{''.join(f'<li>{html.escape(g)}</li>' for g in gaps)}</ul></div>
        <div class="card"><h3>This week</h3><p>{html.escape(priority)}</p></div>
      </div>
    </section>
    """)

    sections.append(f"""
    <section id="metrics">
      <h2>Professional Growth Metrics</h2>
      {table_from_rows(metric_rows(baseline, defs), ["Metric", "Current", "6mo Target", "Gap", "Next action"])}
    </section>
    """)

    ind_lines = []
    for s in sectors[:8]:
        ind_lines.append(f"<li><strong>{html.escape(s.get('industry', ''))}</strong> — score {html.escape(s.get('score', ''))}</li>")
    sections.append(f"""
    <section id="network">
      <h2>Network Intelligence</h2>
      <p>Full index: <a href="network_index.html">network_index.html</a> (local file)</p>
      <h3>Top sectors</h3>
      <ul>{''.join(ind_lines) or '<li>Run pipeline with network export</li>'}</ul>
    </section>
    """)

    conn_cols = ["name", "company", "title", "rank", "suggested_action", "draft_note"]
    if connections and "suggested_action" not in connections[0]:
        conn_cols = ["name", "company", "title", "rank", "recommended_action", "rationale"]
    sections.append(f"""
    <section id="connections">
      <h2>Suggested Connections</h2>
      <p class="muted">Draft notes are starting points — personalize before sending.</p>
      {table_from_rows(connections[:15], [c for c in conn_cols if connections and c in connections[0]])}
    </section>
    """)

    if should_show_jobs(subject):
        sections.append(f"""
    <section id="jobs">
      <h2>Job Pipeline</h2>
      {table_from_rows(jobs[:15], ["title", "company", "total_score", "fit_score", "status", "url"])}
    </section>
    """)

    sections.append(f"""
    <section id="business">
      <h2>Business Opportunities</h2>
      <pre class="md">{html.escape(md_excerpt(ws / 'business_opportunities.md', 35))}</pre>
    </section>
    """)

    if should_show_content(subject):
        sections.append(f"""
    <section id="content">
      <h2>Content &amp; Visibility</h2>
      <pre class="md">{html.escape(md_excerpt(ws / 'post_recommendations.md', 25))}</pre>
      <h3>Ready drafts</h3>
      <pre class="md">{html.escape(md_excerpt(ws / 'post_drafts.md', 30))}</pre>
    </section>
    """)

    sections.append(f"""
    <section id="skills">
      <h2>Skills &amp; Learning</h2>
      <pre class="md">{html.escape(md_excerpt(ws / 'skills_roadmap.md', 35))}</pre>
    </section>
    """)

    sections.append(f"""
    <section id="plan">
      <h2>6-Month Action Plan</h2>
      <pre class="md">{html.escape(md_excerpt(ws / 'action_plan_6mo.md', 50))}</pre>
    </section>
    """)

    sections.append("""
    <section id="gates">
      <h2>Your Controls</h2>
      <ul>
        <li>Agent never auto-submits job applications</li>
        <li>Agent never auto-sends messages or connection requests</li>
        <li>Agent never auto-publishes posts</li>
        <li>Your LinkedIn export and workspace stay local (gitignored)</li>
        <li>You approve every CONNECT, NURTURE, APPLY, POST action</li>
      </ul>
    </section>
    """)

    doc = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Intelligence Dashboard — {name}</title>
  <style>
    :root {{
      --bg: #f8f9fb; --card: #fff; --text: #1a1d21; --muted: #5c6570;
      --border: #e2e6eb; --accent: #0a66c2; --accent-soft: #e8f4fc;
    }}
    * {{ box-sizing: border-box; }}
    body {{ font-family: "Segoe UI", system-ui, sans-serif; margin: 0; background: var(--bg); color: var(--text); line-height: 1.5; }}
    header {{ background: var(--card); border-bottom: 1px solid var(--border); padding: 1.5rem 2rem; }}
    header h1 {{ margin: 0; font-size: 1.35rem; font-weight: 600; }}
    header p {{ margin: 0.35rem 0 0; color: var(--muted); font-size: 0.9rem; }}
    main {{ max-width: 1100px; margin: 0 auto; padding: 1.5rem 2rem 3rem; }}
    section {{ background: var(--card); border: 1px solid var(--border); border-radius: 8px; padding: 1.25rem 1.5rem; margin-bottom: 1.25rem; }}
    h2 {{ margin: 0 0 1rem; font-size: 1.1rem; font-weight: 600; }}
    h3 {{ margin: 1rem 0 0.5rem; font-size: 0.95rem; }}
    .lede {{ color: var(--muted); margin-bottom: 1rem; }}
    .grid.three {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1rem; }}
    .card {{ background: var(--accent-soft); border-radius: 6px; padding: 1rem; }}
    .card h3 {{ margin-top: 0; font-size: 0.85rem; text-transform: uppercase; letter-spacing: 0.04em; color: var(--muted); }}
    .card ul {{ margin: 0; padding-left: 1.1rem; }}
    table {{ width: 100%; border-collapse: collapse; font-size: 0.88rem; }}
    th, td {{ border: 1px solid var(--border); padding: 0.5rem 0.65rem; text-align: left; vertical-align: top; }}
    th {{ background: #f0f3f6; font-weight: 600; }}
    .muted {{ color: var(--muted); font-size: 0.88rem; }}
    pre.md {{ white-space: pre-wrap; font-family: inherit; font-size: 0.85rem; background: #f6f8fa; padding: 1rem; border-radius: 6px; overflow-x: auto; }}
    a {{ color: var(--accent); }}
  </style>
</head>
<body>
  <header>
    <h1>LinkedIn Intelligence Dashboard</h1>
    <p>{name} · Human-in-the-loop · No auto-submit</p>
  </header>
  <main>
    {''.join(sections)}
  </main>
</body>
</html>"""

    out = ws / "intelligence_dashboard.html"
    out.write_text(doc, encoding="utf-8")
    print(f"Intelligence dashboard → {out}")


if __name__ == "__main__":
    main()