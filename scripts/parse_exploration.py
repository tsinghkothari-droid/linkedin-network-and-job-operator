#!/usr/bin/env python3
"""Parse exploration YAML snapshots and summarize discoverable capabilities."""

from __future__ import annotations

import json
import re
from pathlib import Path


def extract_lines(path: Path) -> list[str]:
    if not path.exists():
        return []
    return path.read_text(encoding="utf-8", errors="ignore").splitlines()


def find_patterns(lines: list[str], patterns: list[str]) -> list[str]:
    hits = []
    for line in lines:
        lower = line.lower()
        for p in patterns:
            if p in lower:
                hits.append(line.strip())
                break
    return hits[:30]


def extract_jobs(lines: list[str]) -> list[dict]:
    jobs = []
    for i, line in enumerate(lines):
        if "/jobs/view/" in line and "url:" in line.lower():
            m = re.search(r"/jobs/view/(\d+)", line)
            if m:
                jobs.append({"job_id": m.group(1), "context": line.strip()[:200]})
        if "Easy Apply" in line:
            jobs.append({"signal": "easy_apply", "context": line.strip()[:120]})
        if "Dismiss" in line and "job" in line.lower():
            title = re.search(r'Dismiss (.+?) job', line, re.I)
            if title:
                jobs.append({"title_hint": title.group(1).strip()})
    # dedupe title hints
    seen = set()
    out = []
    for j in jobs:
        key = json.dumps(j, sort_keys=True)
        if key not in seen:
            seen.add(key)
            out.append(j)
    return out[:25]


def main() -> None:
    root = Path(__file__).resolve().parent.parent
    snap_dir = root / "linkedin-job-workspace" / "exploration" / "snapshots"
    out_dir = root / "linkedin-job-workspace" / "exploration"
    out_dir.mkdir(parents=True, exist_ok=True)

    pages = {}
    all_capabilities = []

    page_signals = {
        "feed": ["start a post", "profile viewers", "post impressions", "my pages", "newsletter", "groups", "events", "advertise"],
        "network": ["invitation", "connect", "follow", "people you may know", "manage my network"],
        "profile-views": ["viewed your profile", "viewer", "private mode", "who's viewed"],
        "creator-analytics": ["impression", "engagement", "followers", "demographic", "analytics"],
        "jobs-govtech": ["easy apply", "jobs search", "dismiss", "/jobs/view/"],
        "jobs-ai-strategy": ["easy apply", "jobs search", "dismiss", "/jobs/view/"],
        "company-leeladhar": ["employees", "about", "follow", "visit website", "affiliated"],
        "audience-analytics": ["follower", "audience", "demographic", "industry", "location"],
        "newsletters": ["newsletter", "subscribe", "edition", "published"],
        "notifications": ["notification", "commented", "reacted", "mentioned", "job alert"],
    }

    for name, signals in page_signals.items():
        lines = extract_lines(snap_dir / f"{name}.yml")
        if not lines:
            pages[name] = {"status": "missing", "signals": []}
            continue
        hits = find_patterns(lines, signals)
        entry = {"status": "ok", "line_count": len(lines), "signals": hits[:15]}
        if "jobs" in name:
            entry["jobs"] = extract_jobs(lines)
        pages[name] = entry

        # capability inference
        if name == "feed" and any("profile viewers" in h.lower() for h in hits):
            all_capabilities.append({
                "capability": "profile_viewer_nurture",
                "page": name,
                "action": "Parse viewer list, draft nurture messages",
                "priority": "high",
            })
        if name == "creator-analytics":
            all_capabilities.append({
                "capability": "content_performance_loop",
                "page": name,
                "action": "Track impressions/engagement, tune post recommendations",
                "priority": "high",
            })
        if name == "network":
            all_capabilities.append({
                "capability": "connection_growth",
                "page": name,
                "action": "Rank PYMK, draft connect requests by sector fit",
                "priority": "medium",
            })
        if "jobs" in name:
            all_capabilities.append({
                "capability": "live_job_pipeline",
                "page": name,
                "action": "Parse job cards → score → referral match",
                "priority": "high",
            })
        if name == "company-leeladhar":
            all_capabilities.append({
                "capability": "company_intel",
                "page": name,
                "action": "Employee/about snapshot + leadership cross-ref",
                "priority": "medium",
            })
        if name == "notifications":
            all_capabilities.append({
                "capability": "engagement_triage",
                "page": name,
                "action": "Prioritize replies, job alerts, mentions",
                "priority": "medium",
            })
        if name == "audience-analytics":
            all_capabilities.append({
                "capability": "audience_targeting",
                "page": name,
                "action": "Follower demographics → tune post topics and timing",
                "priority": "high",
            })
        if name == "newsletters":
            all_capabilities.append({
                "capability": "newsletter_intel",
                "page": name,
                "action": "Map 102 subscriptions → sector commentary opportunities",
                "priority": "medium",
            })

    # unique capabilities
    report_lines = [
        "# LinkedIn Exploration Report",
        "",
        "## Pages captured",
        "",
    ]
    for name, data in pages.items():
        report_lines.append(f"### {name}")
        report_lines.append(f"- Status: {data.get('status')}")
        if data.get("line_count"):
            report_lines.append(f"- Snapshot lines: {data['line_count']}")
        if data.get("jobs"):
            report_lines.append(f"- Job signals: {len(data['jobs'])}")
        for s in data.get("signals", [])[:5]:
            report_lines.append(f"- `{s[:100]}`")
        report_lines.append("")

    report_lines.extend(["## New capabilities discovered", ""])
    for c in all_capabilities:
        report_lines.append(f"### {c['capability']} ({c['priority']})")
        report_lines.append(f"- **Page:** {c['page']}")
        report_lines.append(f"- **Action:** {c['action']}")
        report_lines.append("")

    report_lines.extend([
        "## Automation surfaces (safe, visible only)",
        "",
        "| Surface | What agent can do | Human gate |",
        "|---------|-------------------|------------|",
        "| Feed | Read stats, draft posts | You publish |",
        "| Profile viewers | List viewers, draft messages | You send |",
        "| Creator analytics | Read metrics, adjust calendar | You approve topics |",
        "| Jobs search | Score jobs, draft apply materials | You submit |",
        "| My Network | Rank connections, draft invites | You send |",
        "| Company pages | Intel, content drafts for 15 pages | You publish |",
        "| Notifications | Triage, suggest replies | You reply |",
        "| Groups/Events/Newsletters | Discovery (next exploration) | You act |",
        "",
    ])

    report_path = out_dir / "exploration_report.md"
    report_path.write_text("\n".join(report_lines), encoding="utf-8")
    (out_dir / "exploration.json").write_text(json.dumps({"pages": pages, "capabilities": all_capabilities}, indent=2), encoding="utf-8")
    print(report_path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    main()