# Privacy and Compliance Rules

These rules apply to every invocation of the LinkedIn Network and Job Operator skill.

## Data Sources (Allowed)

| Source | Use |
|--------|-----|
| LinkedIn data export (user-provided ZIP/CSV) | Network analysis, company mapping |
| User resume/profile (user-provided) | Job fit scoring, application drafts |
| Public job listing pages | Job discovery, requirement extraction |
| Visible browser content (logged-in session) | Job search, form prefill with approval |
| Generated indexes and pipelines | Local workspace only |

## Data Sources (Forbidden)

| Source | Reason |
|--------|--------|
| LinkedIn private/internal APIs | Terms of service, legal risk |
| Hidden POST/XHR endpoints | Scraping, not user-visible content |
| Third-party LinkedIn scrapers | Credential exposure, ToS violation |
| Other users' private messages or emails | Privacy violation |
| Purchased contact lists | Consent and accuracy issues |

## Credential and Session Handling

**Never store, log, or commit:**

- Passwords
- Cookies
- Session tokens
- OAuth tokens
- 2FA codes
- Browser storage dumps

**Allowed:**

- User confirms they are already logged in (isolated Playwright session only)
- Playwright reads visible DOM text only
- Session exists only in gitignored `.playwright-profiles/`; agent does not persist credentials

**Forbidden (personal browser):**

- Reusing personal Chrome user-data directories or Gmail-signed-in profiles
- Attaching Playwright to the operator's everyday Chrome via extension
- Loading saved cookie/state files from real accounts into the repo

## Git and Version Control

### Safe to commit

- Skill definition (`SKILL.md`)
- Reference docs and templates
- Helper scripts
- Sample/synthetic validation data
- `.gitignore` rules

### Never commit

- Full LinkedIn data export ZIP
- `Connections.csv` with real names/emails
- `network.json` with real contact data
- `job_pipeline.csv` with real application history
- `outreach_messages.md` with sent messages to real people
- `application_drafts/` with real personal info
- Screenshots of LinkedIn pages with PII

### Required `.gitignore` entries

```
linkedin-job-workspace/
validation/output/
*.zip
Connections.csv
Profile.csv
network.json
job_pipeline.csv
company_network_map.csv
referral_targets.csv
outreach_messages.md
application_drafts/
application_status_dashboard.html
network_index.*
```

## Application Submission

| Action | Allowed |
|--------|---------|
| Draft cover letter | Yes |
| Prefill name, email, LinkedIn URL | Yes, with user review |
| Click Submit / Apply | **No** — user only |
| Mass apply to 10+ jobs | **No** |
| Auto-send connection requests | **No** — user reviews each message |

## Rate Limits and Anti-Bot

- Pause if CAPTCHA, "unusual activity", or login challenge appears
- Do not retry aggressively
- Do not use headless bulk scraping
- Limit browser navigation to what a human would do in one session
- Ask user to continue manually when blocked

## PII Minimization in Outputs

When generating reports for the user:

- Use full names only in local workspace files
- In chat summaries, prefer "Connection at [Company]" unless user requests names
- Redact emails in any output that might be shared or committed
- Sample validation data must use fictional names only

## Retention

- Workspace data stays local unless user explicitly moves it
- Do not upload exports to cloud storage or GitHub
- Delete temporary HTML snapshots after extraction

## Audit Checklist

Before any workflow completes, verify:

- [ ] No credentials written to disk
- [ ] No private API calls made
- [ ] No Submit button clicked
- [ ] Output files are in gitignored paths
- [ ] User approved any browser form fills
- [ ] Sample mode used fictional data only