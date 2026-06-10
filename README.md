# linkedin-network-and-job-operator

Codex/Cursor agent skill for LinkedIn network analysis, job discovery, referral-first outreach, and application assistance — with strict human-in-the-loop controls.

## What it does

1. **Network Analysis** — Classify connections from your LinkedIn export; build searchable indexes.
2. **Job Discovery** — Score jobs from public pages or visible browser content.
3. **Application Assistant** — Draft cover letters, compare resume fit, prefill forms (never submit).
4. **Referral-first Strategy** — Rank referral targets and draft outreach messages.

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