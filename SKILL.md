---
name: linkedin-network-and-job-operator
description: >
  End-to-end LinkedIn career and business operator for people at large: job search and
  applications (referral-first, human submit), content creation and posting strategy,
  trend and hiring signal identification, business opportunity detection, industry
  newcomer discovery, network growth, skills roadmaps, leadership intel, and cross-site
  job research (visible browser only). Launch Chrome via playwright-cli extension attach.
  Supports coach/recruiter subject mode. Trigger with "linkedin network analysis",
  "find jobs", "job application assistant", "what should I post", "sector opportunities",
  "business opportunities", "senior people to connect", "skills gap", or
  "/linkedin-network-and-job-operator". Human review required for all sends and submits.
  Never scrapes private APIs or auto-submits applications.
---

# LinkedIn Network and Job Operator

Operate on **your** LinkedIn data and browser session with human-in-the-loop control.
Use exported LinkedIn data, public job pages, and visible browser content only.

**Use cases for people at large:** Read `docs/USE_CASES.md` (jobs, content, trends, business opps, new connections, other sites).
**Persona routing:** `docs/PERSONAS.md`
**Generic skill plan (public GitHub):** `docs/GENERIC_SKILL_PLAN.md`

## Generic Run Order (Any User)

**Do not skip gates.** Each phase requires user confirmation.

| Phase | What | Reference |
|-------|------|-----------|
| **A** | Install Playwright + attach **trusted browser** + LinkedIn login | `references/onboarding_playwright.md` |
| **B** | Guide user to **request & download** LinkedIn data export | `references/linkedin_data_export_guide.md` |
| **C** | Ask **≤7 intake questions** (MCQ + sliders) **before synthesis** | `references/intake_flow.md`, `templates/intake_questions.json` |
| **D** | Synthesize: network, jobs, connections, business opps, content, skills | `scripts/run_generic_pipeline.py` |
| **E** | Deliver **Intelligence Dashboard** + **6-month action plan** | `build_intelligence_dashboard.py`, `generate_action_plan.py` |

After Phase C (Phases D–E in one command):

```bash
python scripts/run_generic_pipeline.py \
  --workspace linkedin-job-workspace \
  --intake linkedin-job-workspace/intake_responses.json \
  --export path/to/linkedin_export.zip
```

Optional flags: `--network` (skip export parse), `--skip-live` (no snapshot scoring), `--with-explore` (Windows: run `explore_linkedin.bat` first).

Phase A gate (browser):

```bash
python scripts/verify_browser_session.py --workspace linkedin-job-workspace
```

## Hard Rules (Non-Negotiable)

Read `references/privacy_rules.md` before any workflow. Never:

- Scrape private LinkedIn APIs or hidden POST endpoints
- Store passwords, cookies, session tokens, or 2FA codes
- Bypass CAPTCHA, rate limits, or anti-bot systems
- Mass-apply to jobs
- Click final Submit/Apply without explicit per-application approval
- Commit full LinkedIn exports, contact lists, emails, or messages to Git

**Browser automation:** **Playwright CLI first** (`playwright-cli -s=linkedin-ops`), MCP as fallback. Headed Chrome only. Pause before any irreversible action.

Read `docs/RESEARCH.md` for full research backing. Read `references/playwright_cli_workflow.md` before browser work.

---

## Phase 0: Launch Chrome (Start Here)

Every end-to-end run begins with browser bootstrap:

```powershell
# Windows
.\scripts\bootstrap_chrome.ps1
```

```bash
# macOS/Linux
bash scripts/bootstrap_chrome.sh
```

1. Headed Chrome opens LinkedIn feed
2. **User logs in manually** (never automate credentials)
3. User confirms: `LinkedIn session ready`
4. Agent uses CLI for snapshots/navigation:

```bash
playwright-cli -s=linkedin-ops snapshot
playwright-cli -s=linkedin-ops goto "https://www.linkedin.com/jobs/"
playwright-cli -s=linkedin-ops show   # visual session dashboard
```

Install if missing: `npm install -g @playwright/cli@latest`

---

## Subject vs Operator Profile

This skill can analyze **a different person** than you (coach/recruiter mode).

| File | Purpose |
|------|---------|
| `subject_profile.json` | Person being analyzed (skills, goals, targets) |
| `operator_profile.json` | Optional — who is running the agent |

Copy schema from `templates/subject_profile_schema.json`. Confirm subject name with user before running pipeline.

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
├── network_index.csv
├── skills_roadmap.md / .json
├── recommended_agent_skills.md
├── sector_opportunities.csv
├── business_opportunities.md
├── leadership_map.csv
├── senior_targets.csv
├── post_recommendations.md
├── snapshots/
└── screenshots/
```

Copy schemas from `templates/`. Never commit workspace files to Git.

### One-command intelligence pipeline

```bash
python scripts/run_generic_pipeline.py \
  --workspace linkedin-job-workspace \
  --intake linkedin-job-workspace/intake_responses.json \
  --export path/to/linkedin_export.zip
```

Legacy module-only orchestrator (no intake/dashboard): `scripts/run_intelligence_pipeline.py`

### Scores, drafts & posts (live session)

After `explore_linkedin.bat`:

```bash
python scripts/run_scores_drafts_posts.py --workspace linkedin-job-workspace
```

Produces: `job_pipeline.csv` (scores), `application_drafts/` (cover letters + referrals), `post_drafts/` (ready-to-review posts), `scores_drafts_posts_report.md`. **You publish and submit.**

---

## Workflow Selection

| User intent | Workflow | Reference |
|-------------|----------|-----------|
| "launch chrome", "start linkedin session" | 0: Browser Bootstrap | `references/playwright_cli_workflow.md` |
| "analyze my network", "who should I reach out to" | 1: Network Analysis | below |
| "find jobs", "search roles at X" | 2: Job Discovery | `references/linkedin_job_workflow.md` |
| "help me apply", "draft cover letter for this job" | 3: Job Application Assistant | `references/linkedin_job_workflow.md` |
| "referral first", "who do I know at X" | 4: Referral-first Strategy | below |
| "what skills should I learn", "skills gap" | 5: Skills Intelligence | below |
| "sector opportunities", "which industries" | 6: Sector & Business Opps | below |
| "who runs [company]", "leadership map" | 7: Leadership Intelligence | below |
| "senior people to connect", "who to reach out to" | 8: Senior Recommendations | below |
| "what should I post", "content strategy" | 9: Post Recommendations | below |
| "explore linkedin", "what else can you do" | 10: Platform Exploration | `scripts/explore_linkedin.bat` |
| "business opportunities", "consulting leads" | 6: Sector & Business Opps | below |
| "who viewed my profile", "nurture viewers" | 10 + 4 | `docs/USE_CASES.md` §E |
| "trending in [sector]", "hiring signals" | 5, 6, 10 + research | `docs/USE_CASES.md` §C |

**Full run order:** 0 → intake → 1 → 5 → 6 → 7 → 8 → 9 → 10 → 2 → 4 → 3

### Personas (quick)

| Persona | Primary workflows |
|---------|-------------------|
| Job seeker | 2, 4, 3 |
| Content creator | 9, 10 |
| Consultant / BD | 6, 4, 10 |
| Founder | 6, 7, 8, 9 |
| Career changer | 5, 6, 1, 2 |
| Coach (subject mode) | 1, 5–9 on `subject_profile.json` |

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

## Workflow 5: Skills Intelligence

Analyze **subject** (not operator) skills gaps and recommend new agent skills to build.

```bash
python scripts/skills_intelligence.py \
  --subject linkedin-job-workspace/subject_profile.json \
  --out-dir linkedin-job-workspace
```

Outputs: `skills_roadmap.md`, `skills_roadmap.json`, `recommended_agent_skills.md`

Uses LinkedIn Skills on the Rise 2026 weights (`data/skills_on_the_rise_2026.json`) + target role requirements.

---

## Workflow 6: Sector & Business Opportunities

```bash
python scripts/sector_opportunity.py --network ... --subject ... --out linkedin-job-workspace/sector_opportunities.csv
python scripts/business_opportunity.py --network ... --subject ... --out linkedin-job-workspace/business_opportunities.md
```

Sector score = market growth × network access × skills fit. Business opps: intro arbitrage, advisory, co-founder match, talent placement, thought leadership.

---

## Workflow 7: Leadership Intelligence

For each company (user-provided list or top sector companies):

1. **Web search** (use `searxng-scrapling-research` if available): `"[Company] CEO leadership team 2026"`
2. **Browser:** `playwright-cli -s=linkedin-ops goto` company About page → snapshot
3. Cross-reference with `company_network_map.csv`
4. Output `leadership_map.csv` with `source_url` + `confidence` on every row

**Never guess names.** Every leadership row needs a public source.

---

## Workflow 8: Senior People Recommendations

```bash
python scripts/senior_recommendations.py \
  --network linkedin-job-workspace/network.json \
  --subject linkedin-job-workspace/subject_profile.json \
  --out linkedin-job-workspace/senior_targets.csv
```

Ranks T1–T4 seniority tiers. Actions: `connect`, `nurture`, `follow`. Combine with `templates/referral_message_templates.md` for outreach drafts.

---

## Workflow 9: Content & Post Strategy

```bash
python scripts/content_recommendations.py \
  --network linkedin-job-workspace/network.json \
  --subject linkedin-job-workspace/subject_profile.json \
  --out linkedin-job-workspace/post_recommendations.md
```

Generates post ideas tuned to **subject's network clusters** (industry × seniority). Follows 2026 algorithm rules:
- Favor carousels (6–9 slides) and long-form text (1,200–1,800 chars)
- No external links in post body
- No engagement bait
- Depth Score optimization (dwell time, comment depth)

User reviews and posts manually — agent never auto-publishes.

---

## Workflow 10: Platform Exploration

Discover what LinkedIn surfaces are available in the user's live session and capture snapshots for parsers.

```bat
scripts\explore_linkedin.bat
python scripts\parse_exploration.py
```

**Pages:** feed, network, profile-views analytics, creator + audience analytics, jobs (keyword searches), company admin, newsletters, notifications.

**Outputs:** `linkedin-job-workspace/exploration/snapshots/*.yml`, `exploration_report.md`

**Unlocks for people at large:**

| Surface | Use |
|---------|-----|
| Jobs search | Live job pipeline |
| Profile viewers | Nurture + hiring-intent clusters |
| Creator analytics | Content performance loop |
| Newsletters | Trend intel + launch operator |
| Network PYMK | Industry newcomer connections |
| Notifications | Hiring posts, job changes, mentions |
| Company admin | Multi-page brand ops |

**Cross-site:** For Indeed, Glassdoor, Naukri, or company career pages — same Playwright session, visible content only. See `docs/USE_CASES.md` §3.

---

## Browser Automation (Playwright CLI + MCP fallback)

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

## Quick Start (End-to-End)

```
User: "Analyze this person's network, find opportunities, and help with jobs"

Agent:
0. bootstrap_chrome.ps1 → user logs in → "LinkedIn session ready"
1. Intake subject_profile.json (confirm correct person)
2. Parse LinkedIn export → network.json (Workflow 1)
3. run_intelligence_pipeline.py (Workflows 5–9)
4. Web research for leadership of top companies (Workflow 7)
5. Browser job search via playwright-cli snapshots (Workflow 2)
6. Referral-first for top jobs (Workflow 4)
7. Application drafts, stop before Submit (Workflow 3)
8. Present dashboard + all intelligence outputs
```

---

## References

- **Use cases (people at large):** `docs/USE_CASES.md`
- **Persona entry points:** `docs/PERSONAS.md`
- Research (read first): `docs/RESEARCH.md`
- Architecture: `docs/ARCHITECTURE.md`
- Discovery & tools: `docs/DISCOVERY.md`
- Roadmap: `docs/ROADMAP.md`
- Companion skills to build: `docs/COMPANION_SKILLS.md`
- Playwright CLI: `references/playwright_cli_workflow.md`
- Privacy and compliance: `references/privacy_rules.md`
- Detailed job workflow: `references/linkedin_job_workflow.md`
- Subject profile schema: `templates/subject_profile_schema.json`
- Pipeline CSV schema: `templates/job_pipeline_schema.csv`
- Message templates: `templates/referral_message_templates.md`