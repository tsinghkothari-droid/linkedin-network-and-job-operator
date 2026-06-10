#!/usr/bin/env python3
"""
Extract job fields from saved visible HTML snapshots only.
Does not fetch URLs or call private APIs.
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


def extract_from_html(html_text: str, source_url: str = "") -> dict:
    title = _first_match(html_text, [r"<h1[^>]*>([^<]+)</h1>", r'class="job-title"[^>]*>([^<]+)<'])
    company = _first_match(html_text, [r'class="company"[^>]*>([^<]+)<', r"companyName[\"']:\s*[\"']([^\"']+)"])
    location = _first_match(html_text, [r'class="location"[^>]*>([^<]+)<', r"jobLocation[\"']:\s*[\"']([^\"']+)"])
    posted = _first_match(html_text, [r"posted[^<]{0,20}([0-9]+ (?:day|week|month)s? ago)", r"datePosted[\"']:\s*[\"']([^\"']+)"])

    app_type = "unknown"
    lower = html_text.lower()
    if "easy apply" in lower:
        app_type = "easy_apply"
    elif "apply on company website" in lower or "external" in lower:
        app_type = "external"

    requirements = _extract_requirements(html_text)

    return {
        "title": _clean(title),
        "company": _clean(company),
        "location": _clean(location),
        "url": source_url,
        "posted_date": _clean(posted),
        "application_type": app_type,
        "requirements": requirements,
    }


def _first_match(text: str, patterns: list[str]) -> str:
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
        if match:
            return match.group(1).strip()
    return ""


def _extract_requirements(html_text: str) -> list[str]:
    bullets = re.findall(r"<li[^>]*>([^<]{10,200})</li>", html_text, re.IGNORECASE)
    keywords = []
    for bullet in bullets[:20]:
        cleaned = re.sub(r"\s+", " ", bullet).strip()
        if any(k in cleaned.lower() for k in ("experience", "skill", "required", "degree", "years")):
            keywords.append(cleaned)
    return keywords[:10]


def _clean(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip()


def main() -> None:
    parser = argparse.ArgumentParser(description="Extract jobs from visible HTML snapshot")
    parser.add_argument("--html", required=True, help="Path to saved HTML file")
    parser.add_argument("--url", default="", help="Source URL metadata")
    parser.add_argument("--out", required=True, help="Output JSON path")
    args = parser.parse_args()

    html_text = Path(args.html).read_text(encoding="utf-8", errors="ignore")
    job = extract_from_html(html_text, args.url)

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(job, indent=2), encoding="utf-8")
    print(json.dumps(job, indent=2))


if __name__ == "__main__":
    main()