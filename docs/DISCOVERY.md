# Tool & Use Case Discovery

**Date:** 2026-06-10 (updated)  
**Context:** Live LinkedIn session via extension attach + token  
**Canonical use-case catalog:** [USE_CASES.md](./USE_CASES.md) — written for **people at large**, not one profile.

**Example session signals (operator):** Strategy & Applied AI | Due Diligence | Power Sector | GovTech | India | 261 profile viewers | 2,722 post impressions | 15 admin pages | 16,861 followers | 102 newsletters

---

## 1. Tools You Can Configure Now

### A. Browser control (working today)

| Tool | Status | Configure |
|------|--------|-----------|
| **Playwright CLI** | Installed | `npm install -g @playwright/cli` |
| **Extension attach** | Working | `scripts/attach_with_token.bat` + `.env` token |
| **Playwright MCP** | Not in Cursor yet | Add to Cursor MCP config (see below) |
| **playwright-cli skills** | Optional | `playwright-cli install --skills` |

**Cursor MCP config to add** (`~/.cursor/mcp.json` or project MCP):

```json
{
  "mcpServers": {
    "playwright-extension": {
      "command": "npx",
      "args": ["@playwright/mcp@latest", "--extension"],
      "env": {
        "PLAYWRIGHT_MCP_EXTENSION_TOKEN": "<from .env — never commit>"
      }
    }
  }
}
```

### B. Installed agent skills (chain today)

| Skill | Integration use |
|-------|-----------------|
| `searxng-scrapling-research` | Leadership intel, sector news, company research |
| `draft-outreach` | Polish referral/connection messages after pipeline drafts |
| `business-intelligence` | KPI dashboards from `job_pipeline.csv`, sector scores |
| `sales-development-rep` | Outbound prospect ranking for consulting leads |
| `crm-automation` | Sync referral targets → HubSpot/Salesforce (if connected) |
| `xlsx` | Export pipelines to Excel for review |
| `docx` | Cover letters, advisory memos |
| `web-design-studio` | `application_status_dashboard.html` → polished dashboard |
| `find-skills` | Discover/install new skills as platform grows |

### C. Playwright CLI capabilities not yet used

| Command | New use case |
|---------|--------------|
| `tab-list` / `tab-select` | Compare 3 job detail tabs side-by-side |
| `video-start` / `video-stop` | Audit trail for application prefill review |
| `tracing-start` / `tracing-stop` | Debug session drops / CAPTCHA blocks |
| `show` | Visual session dashboard for human oversight |
| `highlight` | Mark form fields before user approves fill |
| `eval` | Extract structured job cards from visible DOM only |
| `screenshot` / `pdf` | Application review packets |
| `console` | Detect LinkedIn client-side errors after navigation |

**Hard rule:** `requests` / `response-body` are for debugging page loads only — never scrape hidden LinkedIn APIs.

### D. Data sources to configure

| Source | Purpose | How |
|--------|---------|-----|
| LinkedIn data export | Full network analysis | User downloads ZIP → `parse_linkedin_export.py` |
| Skills on the Rise 2026 | Macro skill weights | Already in `data/skills_on_the_rise_2026.json` |
| O*NET / CareerOneStop API | Occupation skill gaps | Free API key → `skills_intelligence.py` v2 |
| SearXNG | Leadership + sector research | `SEARXNG_URL` env var |
| Creator analytics | Post performance | Browser → `/analytics/creator/content/` |
| Profile viewers | Who's interested in you | Browser → `/me/profile-views/` |

### E. Local workspace tools (built, need wiring)

| Script | Status | Next wire-up |
|--------|--------|--------------|
| `attach_with_token.bat` | Done | Default session entry |
| `linkedin_jobs_search.bat` | Done | Fix URL encoding (done) |
| `run_intelligence_pipeline.py` | Done | Feed real export |
| `leadership_intel.py` | **Missing** | + searxng research |
| `parse_jobs_from_snapshot.py` | **Missing** | Parse YAML → `job_pipeline.csv` |
| `run_full_pipeline.py` | **Missing** | Browser + intel + jobs orchestrator |
| `explore_linkedin.bat` | **Done** | 10-surface exploration run |
| `parse_exploration.py` | **Done** | Capability + signal report |

---

## 1b. Use Cases Validated by Exploration (any user)

| Use case | Evidence from snapshots | Workflow |
|----------|-------------------------|----------|
| Job applications | Live job IDs + Easy Apply in jobs search YAML | 2, 3, 4 |
| Content & posting | Creator analytics impressions/engagement | 9, 10 |
| Trend identification | 102 newsletters, notification hiring posts | 6, 10 |
| Business opportunities | Viewer clusters at hiring companies | 6, 10 |
| New people to connect | PYMK list, profile viewer names (free tier: 3) | 8, 10 |
| Multi-page ops | Company admin dashboard, 15 pages on feed | 9, 10 |

---

## 2. New Use Cases Discovered (from your live profile)

Your feed snapshot reveals opportunities beyond generic job search:

### Tier 1 — High fit (your headline + pages)

| Use case | Why now | Tools |
|----------|---------|-------|
| **GovTech & Power Sector Deal Radar** | Headline: Power Sector & GovTech | Jobs search + searxng sector news + network map |
| **Due Diligence Advisory Pipeline** | DD in headline — consulting, not just jobs | Business opp finder + senior targets + draft-outreach |
| **Applied AI Thought Leadership Engine** | 2,625 post impressions; AI in headline | content_recommendations + carousel drafts + analytics page |
| **Multi-Page Operator (15 pages)** | Leeladhar, Lumen's Clinovate, !ndia Inc | Per-page content calendar + cross-promotion map |
| **Profile Viewer Intelligence** | 258 viewers | Snapshot `/me/profile-views/` → nurture targets |
| **Asset Management Network Map** | Leeladhar page admin | Company-scoped senior targets + referral paths |

### Tier 2 — Strong extensions

| Use case | Why | Tools |
|----------|-----|-------|
| **India market job + sector scanner** | Location: India | sector_opportunity + India-specific labor data |
| **Healthcare AI crossover** | Lumen's Clinovate page | Sector bridge: GovTech → healthtech |
| **Newsletter launch operator** | Newsletter link in sidebar | Content strategist + subscriber CTA posts |
| **Group intelligence** | Groups access | Map group members → sector opportunities |
| **Event networking prep** | Events link | Pre-event connect list + talking points |
| **Second-degree referral paths** | Needs export | Network graph → warm intro chains |
| **Competitor hiring intel** | Power/govtech firms | Public company career pages + leadership intel |

### Tier 3 — Business development (not job-seeking)

| Use case | Output |
|----------|--------|
| **Consulting lead finder** | Companies posting DD/finance/strategy roles → prospect list |
| **Co-founder / advisor matching** | Founders in network lacking AI/strategy skills |
| **Intro arbitrage marketplace** | Match your network to people seeking intros |
| **LinkedIn ads brief generator** | Campaign manager prep (human approves spend) |
| **Client proposal drafts** | docx skill + company research |

---

## 3. New Skills to Develop

### Immediate extracts (from companion skills plan)

| Skill | Priority | Trigger |
|-------|----------|---------|
| `playwright-cli-browser-ops` | P0 | Shared attach/token/session scripts |
| `linkedin-leadership-intel` | P1 | `who runs [company]` |
| `linkedin-content-strategist` | P1 | `what should I post` |
| `linkedin-carousel-builder` | P1 | Generate 6–9 slide carousel copy |
| `govtech-sector-scanner` | P1 | **Tailored to you** — power/govtech/India |
| `due-diligence-prospect-finder` | P2 | DD/consulting opportunities |
| `linkedin-profile-viewer-intel` | P2 | Who viewed + nurture drafts |
| `multi-page-linkedin-operator` | P2 | 15 pages content ops |
| `linkedin-newsletter-operator` | P3 | Newsletter strategy + issues |

### Meta-skills recommended for your profile

| Skill | Reason |
|-------|--------|
| `govtech-pm-interview-prep` | If pursuing product roles in govtech |
| `power-sector-deal-research` | Sector-specific research automation |
| `ai-dd-memo-writer` | Due diligence memo drafts (docx) |
| `india-legal-govtech-job-filter` | India location + visa/work constraints |
| `linkedin-creator-analytics-reader` | Parse analytics pages → content feedback loop |

---

## 4. Recommended Configuration Stack

```
┌─────────────────────────────────────────────────────────────┐
│ ENTRY: attach_with_token.bat  OR  Playwright MCP extension  │
└──────────────────────────┬──────────────────────────────────┘
                           ▼
┌─────────────────────────────────────────────────────────────┐
│ BROWSER WORKFLOWS (visible content only)                    │
│  feed · jobs · network · profile-views · analytics · pages  │
└──────────────────────────┬──────────────────────────────────┘
                           ▼
┌──────────────────────┐  ┌──────────────────────────────────┐
│ LinkedIn export ZIP  │  │ searxng-scrapling-research       │
│ parse → network.json │  │ leadership · sector news         │
└──────────┬───────────┘  └──────────────┬───────────────────┘
           └──────────────┬──────────────┘
                          ▼
┌─────────────────────────────────────────────────────────────┐
│ INTELLIGENCE PIPELINE                                       │
│ skills · sectors · business opps · seniors · posts · jobs   │
└──────────────────────────┬──────────────────────────────────┘
                           ▼
┌─────────────────────────────────────────────────────────────┐
│ OUTPUT SKILLS                                               │
│ draft-outreach · docx · xlsx · business-intelligence        │
└─────────────────────────────────────────────────────────────┘
```

---

## 5. Priority Build Plan (next 2 weeks)

| Week | Build | Use case unlocked |
|------|-------|-------------------|
| **W1** | `parse_jobs_from_snapshot.py` + live job scoring | Real jobs from browser → pipeline |
| **W1** | `leadership_intel.py` + searxng | Who runs target companies |
| **W1** | Cursor MCP playwright-extension config | Agent-native browser in Cursor |
| **W2** | `govtech-sector-scanner` module | Power/govtech/India opportunities |
| **W2** | Profile viewers + analytics snapshot parsers | Nurture + content feedback |
| **W2** | `multi-page-content-operator` | 15 pages calendar |
| **W2** | Full `run_full_pipeline.py` orchestrator | One command end-to-end |

---

## 6. What NOT to build

| Avoid | Reason |
|-------|--------|
| LinkedIn Voyager API scraping | ToS + privacy rules |
| Auto-send messages / applies | Human review required |
| Cookie/token export to Git | Security |
| Engagement pod automation | Algorithm penalty + ToS |
| Mass connection requests | Account risk |

---

## 7. Immediate next actions (pick one)

1. **Configure Playwright MCP in Cursor** — agent-native browser tools
2. **Parse live jobs** from last `jobs-search.yml` snapshot → score pipeline
3. **GovTech deal radar** — search jobs + news for power sector India
4. **Profile viewers intel** — snapshot `/me/profile-views/` → nurture list
5. **Content engine** — carousel draft on "Applied AI in Due Diligence" for your 2,625-impression audience
6. **LinkedIn export** — upload ZIP for full network intelligence (highest leverage)

---

## References

- [USE_CASES.md](./USE_CASES.md) — full catalog for people at large
- [PERSONAS.md](./PERSONAS.md) — goal → workflow routing
- [COMPANION_SKILLS.md](./COMPANION_SKILLS.md)
- [ROADMAP.md](./ROADMAP.md)
- [RESEARCH.md](./RESEARCH.md)
- [Playwright Extension README](https://github.com/microsoft/playwright/blob/main/packages/extension/README.md)