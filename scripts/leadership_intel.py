#!/usr/bin/env python3
"""Research company leadership via SearXNG (optional) + network cross-reference."""

from __future__ import annotations

import argparse
import csv
import json
import os
import re
import urllib.parse
import urllib.request
from pathlib import Path

ROLE_PATTERNS = [
    (re.compile(r"\bCEO\b[^|]{0,40}?([A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,2})", re.I), "CEO"),
    (re.compile(r"\bChief Executive Officer\b[^|]{0,40}?([A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,2})", re.I), "CEO"),
    (re.compile(r"\bCTO\b[^|]{0,40}?([A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,2})", re.I), "CTO"),
    (re.compile(r"\bCFO\b[^|]{0,40}?([A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,2})", re.I), "CFO"),
]


def load_companies(path: Path, limit: int) -> list[dict]:
    if not path.exists():
        return []
    with path.open(newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    rows.sort(key=lambda r: int(r.get("connection_count") or 0), reverse=True)
    return rows[:limit]


def searxng_search(base_url: str, query: str, timeout: int = 12) -> list[dict]:
    url = base_url.rstrip("/") + "/search?" + urllib.parse.urlencode(
        {"q": query, "format": "json", "categories": "general"}
    )
    req = urllib.request.Request(url, headers={"User-Agent": "linkedin-network-and-job-operator/1.0"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        data = json.loads(resp.read().decode("utf-8", errors="ignore"))
    return data.get("results", [])


def extract_leaders(text: str) -> list[tuple[str, str]]:
    found: list[tuple[str, str]] = []
    for pattern, role in ROLE_PATTERNS:
        for match in pattern.finditer(text):
            name = match.group(1).strip()
            if len(name.split()) >= 2 and name.lower() not in ("the company", "our team"):
                found.append((role, name))
    return found


def research_company(company: str, searx_url: str | None) -> list[dict]:
    rows: list[dict] = []
    query = f"{company} CEO leadership team 2026"
    if not searx_url:
        rows.append({
            "company": company,
            "role": "CEO",
            "name": "",
            "source_url": "",
            "confidence": "pending",
            "notes": f"Set SEARXNG_URL or run searxng-scrapling-research for: {query}",
        })
        return rows

    try:
        results = searxng_search(searx_url, query)
    except Exception as exc:
        rows.append({
            "company": company,
            "role": "CEO",
            "name": "",
            "source_url": "",
            "confidence": "error",
            "notes": f"SearXNG query failed: {exc}",
        })
        return rows

    seen: set[tuple[str, str]] = set()
    for hit in results[:8]:
        blob = " ".join(filter(None, [hit.get("title", ""), hit.get("content", "")]))
        source = hit.get("url", "")
        for role, name in extract_leaders(blob):
            key = (role, name)
            if key in seen:
                continue
            seen.add(key)
            rows.append({
                "company": company,
                "role": role,
                "name": name,
                "source_url": source,
                "confidence": "medium" if source else "low",
                "notes": "Parsed from public search snippet — verify before outreach",
            })

    if not rows:
        top = results[0] if results else {}
        rows.append({
            "company": company,
            "role": "CEO",
            "name": "",
            "source_url": top.get("url", ""),
            "confidence": "low",
            "notes": "No named leader in snippets — review source manually",
        })
    return rows


def main() -> None:
    parser = argparse.ArgumentParser(description="Company leadership research")
    parser.add_argument("--workspace", required=True)
    parser.add_argument("--companies", help="company_network_map.csv override")
    parser.add_argument("--limit", type=int, default=5)
    parser.add_argument("--out")
    args = parser.parse_args()

    ws = Path(args.workspace)
    companies_csv = Path(args.companies) if args.companies else ws / "company_network_map.csv"
    out = Path(args.out) if args.out else ws / "leadership_map.csv"

    searx_url = os.environ.get("SEARXNG_URL", "").strip() or None
    companies = load_companies(companies_csv, args.limit)

    rows: list[dict] = []
    for entry in companies:
        company = entry.get("company", "").strip()
        if not company:
            continue
        rows.extend(research_company(company, searx_url))

    fields = ["company", "role", "name", "source_url", "confidence", "notes"]
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)

    named = sum(1 for r in rows if r.get("name"))
    print(f"Leadership map → {out} ({named} named rows, {len(rows)} total)")


if __name__ == "__main__":
    main()