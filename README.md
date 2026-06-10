# linkedin-network-and-job-operator

Codex/Cursor agent skill for LinkedIn network analysis, job discovery, referral-first outreach, and application assistance — with strict human-in-the-loop controls.

## What it does

**Phase 0:** Launch headed Chrome via `playwright-cli` — you log in, agent controls browser with human review.

1. **Network Analysis** — Classify connections from LinkedIn export; build searchable indexes.
2. **Skills Intelligence** — Personalized skills roadmap + recommend new agent skills to build.
3. **Sector & Business Opportunities** — Score sectors and detect intro/advisory/co-founder opportunities.
4. **Leadership Intel** — Who runs organizations (public sources + browser).
5. **Senior Recommendations** — Rank senior people to connect, nurture, or intro through.
6. **Post Strategy** — Content ideas tuned to what would interest *their* network (2026 algorithm).
7. **Job Discovery** — Score jobs from browser-visible content.
8. **Referral-first Strategy** — Rank referral targets and draft outreach.
9. **Application Assistant** — Draft cover letters, prefill forms (never submit).

Supports analyzing a **different person's profile** than yours (coach/recruiter mode).

## Research & docs

- [RESEARCH.md](docs/RESEARCH.md) — full research backing
- [ARCHITECTURE.md](docs/ARCHITECTURE.md) — system design
- [ROADMAP.md](docs/ROADMAP.md) — implementation phases
- [COMPANION_SKILLS.md](docs/COMPANION_SKILLS.md) — future skills to extract

## Hard rules

- No private LinkedIn API scraping
- No credential or cookie storage
- No CAPTCHA/rate-limit bypass
- No mass apply
- No Submit without your explicit approval per application
- No committing real LinkedIn exports or PII to Git

## Install

### Cursor / Codex (user skills)

Clone into your agents skills folder:

```bash
git clone https://github.com/tsinghkothari-droid/linkedin-network-and-job-operator.git \
  ~/.agents/skills/linkedin-network-and-job-operator
```

Or copy `SKILL.md` and supporting files to `.agents/skills/linkedin-network-and-job-operator/`.

### Grok

Also available at `~/.grok/skills/linkedin-network-and-job-operator/`.

## Usage

Trigger phrases:

- `linkedin network analysis`
- `find jobs on linkedin`
- `job application assistant`
- `referral strategy`
- `/linkedin-network-and-job-operator`

### Quick validation (synthetic data)

```bash
cd ~/.agents/skills/linkedin-network-and-job-operator
python scripts/validate_skill.py --workspace validation/output
```

Outputs job scores, referral targets, draft messages, and checklists for 3 sample jobs. **Nothing is submitted.**

### Real workflow

1. Export LinkedIn data (Settings → Data Privacy → Get a copy of your data).
2. Parse export:
   ```bash
   python scripts/parse_linkedin_export.py --input ~/Downloads/linkedin_export.zip --out linkedin-job-workspace/network.json
   ```
3. Build indexes:
   ```bash
   python scripts/build_network_index.py --network linkedin-job-workspace/network.json --out-dir linkedin-job-workspace
   ```
4. Use Playwright MCP with your logged-in browser for job search (human review required).
5. Review drafts in `linkedin-job-workspace/` and submit applications yourself.

## Structure

```
SKILL.md
references/
  privacy_rules.md
  linkedin_job_workflow.md
templates/
  job_pipeline_schema.csv
  referral_message_templates.md
scripts/
  parse_linkedin_export.py
  build_network_index.py
  extract_visible_jobs.py
  build_dashboard.py
  validate_skill.py
validation/
  sample_jobs.json
  sample_data/
```

## Privacy

See `references/privacy_rules.md`. Keep `linkedin-job-workspace/` local and gitignored.