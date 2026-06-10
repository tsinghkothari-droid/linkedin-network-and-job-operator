# linkedin-network-and-job-operator

Agent skill for **LinkedIn career and business intelligence** — job search, content strategy, trend spotting, opportunity finding, and network growth — with strict human-in-the-loop controls.

Works in **Cursor, Codex, and Grok**. Supports analyzing your own profile or a **client/coachee** (`subject_profile.json`).

## Who is this for?

| You are… | You get… |
|----------|----------|
| Job seeker | Scored job pipeline, referral-first outreach, application drafts (you submit) |
| Consultant / freelancer | Business opportunity detection, viewer nurture, sector targeting |
| Founder / operator | Leadership maps, hiring signals, senior connection targets |
| Content creator | Post calendar, analytics feedback loop, newsletter ideas |
| Coach / recruiter | Full pipeline on someone else's LinkedIn export (subject mode) |
| Company page admin | Multi-page content ops, follower analytics |

**Full use-case catalog:** [docs/USE_CASES.md](docs/USE_CASES.md)  
**Quick persona routing:** [docs/PERSONAS.md](docs/PERSONAS.md)  
**Generic skill plan (onboarding → intake → dashboard):** [docs/GENERIC_SKILL_PLAN.md](docs/GENERIC_SKILL_PLAN.md)

## What it does

**Phase 0:** Attach to your Chrome via Playwright CLI extension (or headed bootstrap) — you log in, agent reads visible pages.

| # | Capability | For people at large |
|---|------------|---------------------|
| 1 | **Network analysis** | Classify 1st-degree connections; referral indexes |
| 2 | **Job discovery & scoring** | Live LinkedIn Jobs + public career pages |
| 3 | **Application assistant** | Cover letters, prefill — **never auto-submit** |
| 4 | **Referral-first strategy** | Who to ask before you apply |
| 5 | **Skills intelligence** | Roadmap + which agent skills to build next |
| 6 | **Sector & business opportunities** | Trends, consulting leads, intro arbitrage |
| 7 | **Leadership intel** | Who runs target companies (sourced) |
| 8 | **Senior recommendations** | Who to connect in your industry |
| 9 | **Content & post strategy** | Ideas tuned to your audience + 2026 algorithm norms |
| 10 | **Platform exploration** | Feed, analytics, jobs, viewers, newsletters — automated snapshots |

**Also supports:** Indeed / Glassdoor / company sites via **visible browser only**; sector news via SearXNG research skill. See [USE_CASES §3](docs/USE_CASES.md#3-cross-platform--other-sites).

## Hard rules

- No private LinkedIn API scraping
- No credential or cookie storage in Git
- No CAPTCHA/rate-limit bypass
- No mass apply or mass messaging
- No Submit without your explicit approval per application
- No committing real LinkedIn exports or PII to Git

## Install

```bash
git clone https://github.com/tsinghkothari-droid/linkedin-network-and-job-operator.git \
  ~/.agents/skills/linkedin-network-and-job-operator

npm install -g @playwright/cli@latest
```

Copy `.env.example` → `.env` with `PLAYWRIGHT_MCP_EXTENSION_TOKEN` (gitignored) for extension attach.

## Quick start

### Trigger phrases

- `linkedin network analysis` · `find jobs on linkedin` · `job application assistant`
- `what should I post` · `sector opportunities` · `business opportunities`
- `senior people to connect` · `skills gap` · `/linkedin-network-and-job-operator`

### Exploration (live session)

```bat
scripts\explore_linkedin.bat
python scripts\parse_exploration.py
python scripts\run_scores_drafts_posts.py --workspace linkedin-job-workspace
```

Outputs scored jobs, application drafts, and LinkedIn post drafts (you submit and publish).

### Export-based intelligence

```bash
python scripts/parse_linkedin_export.py --input ~/Downloads/Basic_LinkedInDataExport.zip --out linkedin-job-workspace/network.json
python scripts/run_intelligence_pipeline.py --subject linkedin-job-workspace/subject_profile.json --network linkedin-job-workspace/network.json
```

### Validation (synthetic — no real data)

```bash
python scripts/validate_skill.py --workspace validation/output
```

## Documentation

| Doc | Contents |
|-----|----------|
| [USE_CASES.md](docs/USE_CASES.md) | **All use cases for people at large** |
| [PERSONAS.md](docs/PERSONAS.md) | Goal → workflow routing |
| [RESEARCH.md](docs/RESEARCH.md) | Research backing |
| [ARCHITECTURE.md](docs/ARCHITECTURE.md) | System design |
| [DISCOVERY.md](docs/DISCOVERY.md) | Tools & live exploration findings |
| [ROADMAP.md](docs/ROADMAP.md) | Implementation phases |
| [COMPANION_SKILLS.md](docs/COMPANION_SKILLS.md) | Future modular skills |

## Structure

```
SKILL.md
docs/          USE_CASES, PERSONAS, RESEARCH, ARCHITECTURE, ROADMAP, DISCOVERY
references/    privacy_rules, playwright_cli_workflow, linkedin_job_workflow
templates/     schemas, MCP config example, message templates
scripts/       parse, score, explore, attach, intelligence pipeline
validation/    sample data for safe testing
```

## Privacy

See `references/privacy_rules.md`. Keep `linkedin-job-workspace/` and `.env` local and gitignored.