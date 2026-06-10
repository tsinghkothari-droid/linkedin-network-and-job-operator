#!/usr/bin/env python3
"""Parse Playwright YAML job search snapshots into structured job records."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

SKIP_COMPANY = re.compile(
    r"promoted|easy apply|viewed|actively|alumni|apply|search|helpful|page \d|remote$|"
    r"are you finding|yes$|no$|^\d+ company|skip to|keyboard|navigation|"
    r"notifications|linkedin$|home$|messaging",
    re.I,
)


def _clean_company(val: str) -> str:
    val = val.strip()
    if not val or len(val) > 70 or SKIP_COMPANY.search(val):
        return ""
    return val


def parse_snapshot_yaml(text: str, source_name: str = "") -> list[dict]:
    jobs: list[dict] = []
    seen_ids: set[str] = set()

    dismiss_pat = re.compile(r'button "Dismiss (.+?) job"', re.I)
    dismisses = list(dismiss_pat.finditer(text))

    for i, dismiss in enumerate(dismisses):
        title = dismiss.group(1).strip()
        end = dismiss.end()
        start = dismisses[i - 1].end() if i > 0 else 0
        block = text[start:end]

        url_m = re.search(r"/jobs/view/(\d+)/", block)
        if not url_m:
            continue
        job_id = url_m.group(1)
        if job_id in seen_ids:
            continue
        seen_ids.add(job_id)

        company = ""
        location = ""
        url_pos = block.find(f"/jobs/view/{job_id}/")
        tail = block[url_pos:] if url_pos >= 0 else block
        for line in tail.splitlines()[:40]:
            m = re.search(r'generic \[ref=[^\]]+\]: (.+)$', line)
            if not m:
                continue
            val = m.group(1).strip()
            if not company:
                c = _clean_company(val)
                if c and c != title and not c.startswith("$"):
                    company = c
            if not location and ("India" in val or "Remote" in val or re.search(r",\s*\w+", val)):
                if "Promoted" not in val and "Apply" not in val and not val.startswith("$"):
                    location = val

        application_type = "easy_apply" if re.search(r"Easy Apply", block, re.I) else "external"
        if re.search(r"Apply on company website|Apply to .+ on company website", block, re.I):
            application_type = "external"

        remote = bool(re.search(r"\(Remote\)|\bRemote\b", block) or "(Remote)" in location)

        jobs.append({
            "job_id": job_id,
            "title": title,
            "company": company,
            "location": location,
            "url": f"https://www.linkedin.com/jobs/view/{job_id}/",
            "posted_date": "",
            "application_type": application_type,
            "remote": remote,
            "source_snapshot": source_name,
            "required_skills": [],
        })

    return jobs


def parse_snapshots_dir(snap_dir: Path) -> list[dict]:
    all_jobs: list[dict] = []
    seen: set[str] = set()
    for path in sorted(snap_dir.glob("jobs-*.yml")):
        text = path.read_text(encoding="utf-8", errors="ignore")
        for job in parse_snapshot_yaml(text, path.stem):
            if job["job_id"] not in seen:
                seen.add(job["job_id"])
                all_jobs.append(job)
    return all_jobs


def main() -> None:
    parser = argparse.ArgumentParser(description="Parse job cards from exploration YAML snapshots")
    parser.add_argument("--snap-dir", help="Directory with jobs-*.yml snapshots")
    parser.add_argument("--snapshot", help="Single snapshot file")
    parser.add_argument("--out", required=True, help="Output JSON path")
    args = parser.parse_args()

    if args.snapshot:
        jobs = parse_snapshot_yaml(
            Path(args.snapshot).read_text(encoding="utf-8", errors="ignore"),
            Path(args.snapshot).stem,
        )
    elif args.snap_dir:
        jobs = parse_snapshots_dir(Path(args.snap_dir))
    else:
        root = Path(__file__).resolve().parent.parent
        jobs = parse_snapshots_dir(root / "linkedin-job-workspace" / "exploration" / "snapshots")

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(jobs, indent=2), encoding="utf-8")
    print(f"Parsed {len(jobs)} jobs → {out}")
    for j in jobs[:10]:
        print(f"  - [{j['job_id']}] {j['title']} @ {j['company']}")


if __name__ == "__main__":
    main()