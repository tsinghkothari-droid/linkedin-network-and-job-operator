#!/usr/bin/env python3
"""Generate 6-month professional action plan from intake + metrics."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

MONTH_THEMES = {
    "job_search": ["Foundation", "Outreach", "Applications", "Interviews", "Negotiate", "Review"],
    "consulting_bd": ["Positioning", "Prospect list", "Outreach", "Calls", "Proposals", "Review"],
    "thought_leadership": ["Analytics baseline", "Content calendar", "Publish", "Engage", "Amplify", "Review"],
    "career_pivot": ["Skills gap", "Network bridge", "Target roles", "Apply", "Interview", "Review"],
    "network_expansion": ["Map network", "Senior targets", "Connect", "Nurture", "Intro loops", "Review"],
    "fundraising": ["Story", "Investor map", "Warm intros", "Meetings", "Follow-up", "Review"],
    "hiring": ["Employer brand", "Talent map", "Outreach", "Screen", "Close", "Review"],
}


def build_actions(goal: str, month_idx: int, metrics: dict) -> list[dict]:
    theme = MONTH_THEMES.get(goal, MONTH_THEMES["network_expansion"])[month_idx]
    actions = [
        {"type": "REVIEW", "task": f"Month {month_idx + 1} theme: {theme}", "human_gate": True},
    ]
    if month_idx == 0:
        actions.append({"type": "LEARN", "task": "Review skills roadmap — add top skill to profile", "human_gate": True})
    if month_idx == 1:
        actions.append({"type": "CONNECT", "task": "Send 5 connection requests from connection_suggestions.csv", "human_gate": True})
    if goal in ("job_search", "career_pivot") and month_idx == 2:
        actions.append({"type": "APPLY", "task": "Review top 3 job drafts — submit if ready", "human_gate": True})
    if goal in ("consulting_bd", "fundraising") and month_idx == 2:
        actions.append({"type": "RESEARCH", "task": "Pick top business opportunity — research leadership", "human_gate": True})
    if month_idx == 3:
        actions.append({"type": "NURTURE", "task": "Message 3 profile viewers or dormant connections", "human_gate": True})
    if month_idx == 4:
        actions.append({"type": "POST", "task": "Publish one post from post_drafts/", "human_gate": True})
    if month_idx == 5:
        actions.append({"type": "REVIEW", "task": "Re-run export + pipeline; compare metrics_baseline.json", "human_gate": True})

    m4 = metrics.get("M4", {}).get("current", 0)
    if m4 and month_idx == 1:
        actions.append({"type": "NURTURE", "task": f"Follow up with high-intent viewers (baseline {m4} viewers/90d)", "human_gate": True})
    return actions


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--workspace", required=True)
    parser.add_argument("--subject", required=True)
    parser.add_argument("--months", type=int, default=6)
    args = parser.parse_args()

    ws = Path(args.workspace)
    subject = json.loads(Path(args.subject).read_text(encoding="utf-8"))
    intake = subject.get("intake", {})
    goal = intake.get("primary_goal", "network_expansion")
    horizon = int(intake.get("time_horizon", 2))
    months = 3 if horizon == 1 else (12 if horizon == 3 else args.months)

    metrics = {}
    mb = ws / "metrics_baseline.json"
    if mb.exists():
        metrics = json.loads(mb.read_text(encoding="utf-8")).get("metrics", {})

    plan_json = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "subject": subject.get("name", ""),
        "primary_goal": goal,
        "horizon_months": months,
        "months": [],
    }

    lines = [
        f"# {months}-Month Professional Growth Plan — {subject.get('name', 'Professional')}",
        "",
        f"**Primary goal:** {goal.replace('_', ' ')}",
        f"**Generated:** {plan_json['generated_at'][:10]}",
        "",
        "> All actions require your approval. Agent does not auto-send or auto-post.",
        "",
    ]

    for i in range(months):
        actions = build_actions(goal, min(i, 5), metrics)
        plan_json["months"].append({"month": i + 1, "actions": actions})
        lines.append(f"## Month {i + 1}")
        for a in actions:
            lines.append(f"- [ ] **[{a['type']}]** {a['task']}")
        lines.append("")

    (ws / "action_plan_6mo.json").write_text(json.dumps(plan_json, indent=2), encoding="utf-8")
    (ws / "action_plan_6mo.md").write_text("\n".join(lines), encoding="utf-8")
    print((ws / "action_plan_6mo.md").read_text(encoding="utf-8"))


if __name__ == "__main__":
    main()