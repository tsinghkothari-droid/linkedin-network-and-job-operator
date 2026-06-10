#!/usr/bin/env python3
"""Parse LinkedIn data export (ZIP or Connections.csv) into network JSON."""

from __future__ import annotations

import argparse
import csv
import json
import re
import zipfile
from datetime import datetime, timezone
from pathlib import Path


SENIORITY_PATTERNS = [
    (r"\b(ceo|cto|cfo|coo|chief)\b", "C-level"),
    (r"\b(founder|co-founder|founding)\b", "Founder"),
    (r"\b(partner|general partner|gp)\b", "Investor"),
    (r"\b(vp|vice president|svp|evp)\b", "VP"),
    (r"\b(director|head of)\b", "Director"),
    (r"\b(manager|lead|principal)\b", "Manager"),
    (r"\b(recruiter|talent acquisition|ta manager|sourcer)\b", "Recruiter"),
    (r"\b(advisor|consultant)\b", "Advisor"),
]

ROLE_TAGS = [
    ("recruiter", r"\b(recruiter|talent acquisition|sourcer|staffing)\b"),
    ("founder", r"\b(founder|co-founder|founding)\b"),
    ("investor", r"\b(investor|venture|vc|partner)\b"),
    ("operator", r"\b(operator|operations|program manager)\b"),
    ("advisor", r"\b(advisor|consultant|mentor)\b"),
    ("speaker", r"\b(speaker|author|keynote)\b"),
    ("hiring_manager", r"\b(hiring manager|engineering manager|product manager|director)\b"),
]


def infer_seniority(title: str) -> str:
    title_lower = title.lower()
    for pattern, level in SENIORITY_PATTERNS:
        if re.search(pattern, title_lower):
            return level
    return "IC"


def infer_tags(title: str) -> list[str]:
    title_lower = title.lower()
    tags = []
    for tag, pattern in ROLE_TAGS:
        if re.search(pattern, title_lower):
            tags.append(tag)
    return tags or ["peer"]


def usefulness_score(title: str, tags: list[str]) -> int:
    base = 30
    weights = {
        "recruiter": 25,
        "hiring_manager": 20,
        "founder": 20,
        "investor": 15,
        "advisor": 10,
        "operator": 10,
        "speaker": 5,
    }
    for tag in tags:
        base += weights.get(tag, 0)
    if infer_seniority(title) in {"Director", "VP", "C-level"}:
        base += 10
    return min(base, 100)


def find_connections_csv(path: Path) -> Path:
    if path.suffix.lower() == ".csv":
        return path
    with zipfile.ZipFile(path) as zf:
        for name in zf.namelist():
            if name.endswith("Connections.csv"):
                extract_dir = path.parent / ".tmp_export"
                extract_dir.mkdir(exist_ok=True)
                out = extract_dir / "Connections.csv"
                out.write_bytes(zf.read(name))
                return out
    raise FileNotFoundError("Connections.csv not found in export")


def parse_connections(csv_path: Path) -> list[dict]:
    rows: list[dict] = []
    with csv_path.open(newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            first = (row.get("First Name") or row.get("First name") or "").strip()
            last = (row.get("Last Name") or row.get("Last name") or "").strip()
            company = (row.get("Company") or "").strip()
            title = (row.get("Position") or row.get("Title") or "").strip()
            url = (row.get("URL") or row.get("Profile URL") or "").strip()
            email = (row.get("Email Address") or row.get("Email") or "").strip()
            connected = (row.get("Connected On") or "").strip()
            if not first and not last:
                continue
            tags = infer_tags(title)
            rows.append(
                {
                    "name": f"{first} {last}".strip(),
                    "company": company,
                    "title": title,
                    "profile_url": url,
                    "email": email,
                    "connected_on": connected,
                    "seniority": infer_seniority(title),
                    "tags": tags,
                    "usefulness_score": usefulness_score(title, tags),
                    "industry": infer_industry(company, title),
                }
            )
    return rows


def infer_industry(company: str, title: str) -> str:
    text = f"{company} {title}".lower()
    mapping = {
        "fintech": r"\b(fintech|bank|payments|stripe|plaid|visa|mastercard)\b",
        "saas": r"\b(saas|b2b|software|cloud|platform)\b",
        "healthcare": r"\b(health|medical|pharma|biotech|hospital)\b",
        "ecommerce": r"\b(retail|ecommerce|commerce|shopify|amazon)\b",
        "ai": r"\b(ai|machine learning|ml|llm|data science)\b",
        "consulting": r"\b(consulting|deloitte|accenture|mckinsey)\b",
    }
    for industry, pattern in mapping.items():
        if re.search(pattern, text):
            return industry
    return "other"


def main() -> None:
    parser = argparse.ArgumentParser(description="Parse LinkedIn export to network JSON")
    parser.add_argument("--input", required=True, help="ZIP export or Connections.csv")
    parser.add_argument("--out", required=True, help="Output network.json path")
    args = parser.parse_args()

    input_path = Path(args.input)
    csv_path = find_connections_csv(input_path)
    connections = parse_connections(csv_path)

    payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source": str(input_path),
        "connection_count": len(connections),
        "connections": connections,
    }

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(f"Wrote {len(connections)} connections to {out_path}")


if __name__ == "__main__":
    main()