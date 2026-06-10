---
name: linkedin-network-and-job-operator
description: >
  Analyze LinkedIn network exports, discover jobs, draft outreach, and assist with
  job applications using exported data, public job pages, and human-reviewed browser
  automation only. Trigger with "linkedin network analysis", "find jobs on linkedin",
  "job application assistant", "referral strategy", "linkedin job operator", or
  "/linkedin-network-and-job-operator". Never scrapes private APIs, stores credentials,
  bypasses anti-bot systems, or submits applications without explicit approval.
---

# LinkedIn Network and Job Operator

Operate on **your** LinkedIn data and browser session with human-in-the-loop control.
Use exported LinkedIn data, public job pages, and visible browser content only.

## Hard Rules (Non-Negotiable)

Read `references/privacy_rules.md` before any workflow. Never:

- Scrape private LinkedIn APIs or hidden POST endpoints
- Store passwords, cookies, session tokens, or 2FA codes
- Bypass CAPTCHA, rate limits, or anti-bot systems
- Mass-apply to jobs
- Click final Submit/Apply without explicit per-application approval
- Commit full LinkedIn exports, contact lists, emails, or messages to Git

**Browser automation:** Playwright MCP only for visible content the user is already logged into. Pause before any irreversible action.

---

## Workspace Layout

All outputs go under a local workspace (default: `./linkedin-job-workspace/`):

```
linkedin-job-workspace/
├── job_pipeline.csv
├── company_network_map.csv
├── referral_targets.csv
├── outreach_messages.md
├── application_status_dashboard.html
├── application_drafts/
├── network_index.html
└── network_index.csv
```

Copy schemas from `templates/`. Never commit workspace files to Git.

---

## Workflow Selection

| User intent | Workflow | Reference |
|-------------|----------|-----------|
| "analyze my network", "who should I reach out to" | 1: Network Analysis | below |
| "find jobs", "search roles at X" | 2: Job Discovery | `references/linkedin_job_workflow.md` |
| "help me apply", "draft cover letter for this job" | 3: Job Application Assistant | `references/linkedin_job_workflow.md` |
| "referral first", "who do I know at X" | 4: Referral-first Strategy | below |

Run workflows in order when starting fresh: 1 → 2 → 4 → 3.

---

## Workflow 1: Network Analysis

### Input

- LinkedIn data export ZIP/CSV (`Connections.csv`, `Profile.csv`, optional `Positions.csv`)
- Or pre-built `network.json` from `scripts/parse_linkedin_export.py`

### Steps

1. **Ingest export**
   ```bash
   python scripts/parse_linkedin_export.py --input <export.zip|Connections.csv> --out linkedin-job-workspace/network.json
   ```

2. **Classify each connection** by:
   - Industry (infer from company + title keywords)
   - Company
   - Seniority (IC / Manager / Director / VP / C-level / Founder / Investor)
   - Usefulness score (0–100): recruiter, hiring manager, founder, investor, operator, advisor, speaker, alumni, peer

3. **Build indexes**
   ```bash
   python scripts/build_network_index.py --network linkedin-job-workspace/network.json --out-dir linkedin-job-workspace
   ```
   Produces `network_index.csv` and `network_index.html` (searchable).

4. **Identify high-value targets** — tag connections as:
   - `speaker`, `advisor`, `recruiter`, `founder`, `investor`, `operator`, `hiring_manager`

5. **Draft outreach templates** — append to `outreach_messages.md` using patterns from `templates/referral_message_templates.md`.

### Output summary

Report: total connections, top industries, top companies, count by seniority, top 10 referral targets by usefulness.

---

## Workflow 2: Job Discovery

### Input

- Target role, location, industry, salary preference, seniority, visa/work constraints
- Optional: company list

### Steps

1. Confirm search criteria with user.
2. **Browser path (preferred for logged-in session):**
   - Use Playwright MCP to navigate LinkedIn Jobs or public company career pages
   - Read **visible page content only** — job title, company, location, URL, posted date, requirements, application type (Easy Apply / external / email)
   - Run `scripts/extract_visible_jobs.py` if saving HTML snapshot locally
   - **Stop** if CAPTCHA, login wall, or rate-limit warning appears; ask user to resolve manually

3. **Public path (no login):**
   - Open public job listing URLs or company career pages
   - Extract same fields from visible HTML

4. **Score each job** (0–100) using:
   - `fit_score`: role match vs user profile/resume
   - `relevance_score`: industry, location, seniority alignment
   - `network_score`: connections at company (from Workflow 1)
   - `effort_score`: inverse of application complexity (Easy Apply = higher)
   - `total_score`: weighted average (fit 35%, relevance 25%, network 25%, effort 15%)

5. Append rows to `job_pipeline.csv` using `templates/job_pipeline_schema.csv`.

### Scoring rubric

| Dimension | High (80+) | Medium (50–79) | Low (<50) |
|-----------|------------|----------------|-----------|
| Fit | 80%+ requirement match | 50–79% match | <50% match |
| Network | 2+ strong connections | 1 connection | None |
| Effort | Easy Apply, <5 fields | Standard form | Custom essays + assessments |

---

## Workflow 3: Job Application Assistant

For each job in `job_pipeline.csv` with status `discovered` or `referral_pending`:

1. **Summarize** the job (role, team, requirements, nice-to-haves).
2. **Compare** to user resume/profile — list matches and gaps.
3. **Identify missing requirements** — honest gap analysis, suggest framing not fabrication.
4. **Draft** tailored cover letter or application answers → `application_drafts/<company>_<role>.md`
5. **Find connections** at company via `company_network_map.csv`.
6. **Draft referral message** if Workflow 4 not yet done.
7. **Prefill** application fields where safe (name, email, LinkedIn URL, work history) via browser — **never submit**.
8. **Stop before Submit** — present checklist:

```
Application Checklist: [Company] — [Role]
- [ ] Job summary reviewed
- [ ] Resume gaps acknowledged
- [ ] Cover letter / answers drafted
- [ ] Referral outreach sent (if applicable)
- [ ] Form fields prefilled
- [ ] USER APPROVAL REQUIRED — click Submit yourself
```

Update `job_pipeline.csv` status to `draft_ready`. Set `submitted` only when user confirms.

---

## Workflow 4: Referral-first Strategy

Run **before** applying when `network_score` > 0.

1. Search `network_index.csv` / `company_network_map.csv` for company matches.
2. **Rank referral targets** by:
   - Relationship strength (1st degree > 2nd)
   - Seniority relevance to hiring
   - Recency of interaction
   - Role (recruiter > hiring manager > peer > alumni)
3. Write top 3 to `referral_targets.csv`.
4. Draft short referral messages → `outreach_messages.md` using `templates/referral_message_templates.md`.
5. Track status per target: `not_contacted` → `contacted` → `replied` → `referred` → `applied`.

**Rule:** Do not apply until user chooses — either wait for referral response or explicitly waive referral.

---

## Browser Automation (Playwright MCP)

Use only when user has an active logged-in session.

### Allowed actions

- Navigate to job search or job detail URLs user provides
- Read visible text from current page
- Fill form fields user approved
- Take snapshot for extraction

### Forbidden actions

- Automated login or credential entry
- Solving CAPTCHA
- Clicking Submit / Apply / Send without explicit approval
- Bulk navigation across many profiles (rate-limit risk)

### Human-review gate

Before any form fill or message send:

```
ACTION PENDING REVIEW
- Page: [URL]
- Action: [fill field X / draft message Y]
- Approve? (yes/no)
```

If user says no, log and skip.

---

## Dashboard

After updating pipelines, regenerate:

```bash
python scripts/build_dashboard.py --workspace linkedin-job-workspace
```

Opens `application_status_dashboard.html` with job scores, referral status, and draft links.

---

## Validation Mode

When user asks to validate or test the skill:

1. Use `validation/sample_data/` — never real LinkedIn exports.
2. Process exactly 3 sample jobs from `validation/sample_jobs.json`.
3. Output for each job:
   - Job score breakdown
   - Best referral target
   - Draft referral message
   - Application checklist (no submission)
4. Run:
   ```bash
   python scripts/validate_skill.py --workspace validation/output
   ```

---

## Integration with Other Skills

- **draft-outreach**: Use for polishing referral messages after this skill drafts the first version.
- **xlsx**: Use if user wants pipeline data in Excel format.

---

## Quick Start

```
User: "Analyze my LinkedIn export and find senior PM roles in fintech"

Agent:
1. Run Workflow 1 on export path user provides
2. Run Workflow 2 with role=Senior Product Manager, industry=fintech
3. Run Workflow 4 for top-scored companies
4. Present top 5 jobs with scores, referral targets, draft messages
5. Ask which jobs to prepare applications for (Workflow 3)
```

---

## References

- Privacy and compliance: `references/privacy_rules.md`
- Detailed job workflow: `references/linkedin_job_workflow.md`
- Pipeline CSV schema: `templates/job_pipeline_schema.csv`
- Message templates: `templates/referral_message_templates.md`