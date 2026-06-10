# Generic LinkedIn Intelligence Skill — Product Plan

**Status:** Plan (implementation roadmap)  
**Repo:** Public GitHub skill — anyone can install and run locally  
**Principle:** Human-in-the-loop. Agent reads **your** export + **your** trusted browser. You connect, download, approve, and act.

---

## 1. Vision

Turn `linkedin-network-and-job-operator` into a **generic career intelligence skill** that any professional can use to:

1. Connect LinkedIn through a **browser they trust** (Playwright extension attach)
2. **Request and ingest** their LinkedIn data export
3. Answer **≤7 intake questions** (MCQ + sliders) so synthesis matches their goals
4. **Synthesize** network, jobs, content, opportunities, and connections
5. Receive a **standardized Intelligence Dashboard** with **6-month action insights** tied to measurable growth metrics

No private APIs. No auto-apply. No credentials in Git. All PII stays in a local gitignored workspace.

---

## 2. Canonical User Journey

```
┌─────────────────────────────────────────────────────────────────┐
│ PHASE A — TRUSTED BROWSER SETUP (Playwright + LinkedIn)         │
│ Install playwright-cli → extension token → attach Chrome        │
│ User logs in manually in their own browser                      │
└────────────────────────────┬────────────────────────────────────┘
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│ PHASE B — DATA EXPORT (user-owned download)                     │
│ Agent guides: Settings → Data Privacy → Request archive         │
│ User downloads ZIP when ready → places in workspace             │
└────────────────────────────┬────────────────────────────────────┘
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│ PHASE C — INTAKE (≤7 questions, MCQ + sliders)                  │
│ Agent asks BEFORE synthesis; writes intake_responses.json        │
└────────────────────────────┬────────────────────────────────────┘
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│ PHASE D — SYNTHESIS PIPELINE                                    │
│ Parse export → explore live session → score → recommend         │
└────────────────────────────┬────────────────────────────────────┘
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│ PHASE E — INTELLIGENCE DASHBOARD + 6-MONTH ACTION PLAN          │
│ Fixed layout; metrics; prioritized actions with human gates     │
└─────────────────────────────────────────────────────────────────┘
```

**Entry trigger (any user):** `/linkedin-network-and-job-operator` or `linkedin career intelligence`

---

## 3. Phase A — Trusted Browser Setup

### What the agent says (first run)

> We'll connect to LinkedIn using **your** Chrome browser via the official Playwright extension. I never see your password. You stay logged in; I only read pages you can already see.

### Steps (documented in `references/onboarding_playwright.md`)

| Step | User action | Agent action |
|------|-------------|--------------|
| A1 | Install Node.js (if missing) | Detect OS; print install link |
| A2 | `npm install -g @playwright/cli@latest` | Verify `playwright-cli --version` |
| A3 | Install [Playwright MCP Chrome extension](https://github.com/microsoft/playwright/tree/main/packages/extension) | Link to extension |
| A4 | Copy extension token → `.env` (gitignored) | Never commit token |
| A5 | Open Chrome (profile you trust) | Run `attach_with_token.bat` or equivalent |
| A6 | Log in to LinkedIn manually | Wait for user: **"LinkedIn session ready"** |
| A7 | Smoke test | `goto feed` → snapshot → detach |

### Acceptance criteria

- Feed snapshot shows user's name/headline
- Session detaches cleanly (no 10h background attach)
- Works on Windows/macOS/Linux (bash + ps1 scripts)

### Deliverables (build)

- [ ] `references/onboarding_playwright.md` — universal setup guide
- [ ] `scripts/verify_browser_session.py` — confirms logged-in feed
- [ ] `.env.example` with `PLAYWRIGHT_MCP_EXTENSION_TOKEN=`
- [ ] Optional: Cursor MCP template (`templates/cursor-mcp-playwright.example.json`)

---

## 4. Phase B — LinkedIn Data Export

### What the agent says

> LinkedIn lets you download **your** data. This unlocks full network analysis (connections, positions, skills). I'll guide you; you download the file to your machine.

### Guided flow

1. Agent sends checklist:
   - LinkedIn → **Settings & Privacy** → **Data Privacy** → **Get a copy of your data**
   - Select **Want something in particular?** → at minimum: **Connections**, **Profile**, **Positions** (optional: Skills, Invitations)
   - Request archive → wait for email (often 24h–10 days)
2. User confirms: **"Export downloaded"** and provides path (e.g. `~/Downloads/Basic_LinkedInDataExport.zip`)
3. Agent runs:
   ```bash
   python scripts/parse_linkedin_export.py --input <path> --out linkedin-job-workspace/network.json
   python scripts/build_network_index.py --network linkedin-job-workspace/network.json --out-dir linkedin-job-workspace
   ```
4. Agent reports: connection count, top industries, data freshness — **no PII in Git**

### Fallback (no export yet)

- Live exploration only (`explore_linkedin.bat`) — limited network graph, still useful for jobs/content/viewers
- Dashboard shows **"Export pending"** banner with completion estimate

### Deliverables (build)

- [ ] `references/linkedin_data_export_guide.md` — screenshots-style steps, all locales
- [ ] `scripts/check_export_ready.py` — validates ZIP structure before parse
- [ ] Workspace flag: `data_status.json` (`export_pending` | `export_parsed`)

---

## 5. Phase C — Intake (≤7 Questions)

**Rule:** Ask **before** synthesis. Store answers in `linkedin-job-workspace/intake_responses.json`. Map to `subject_profile.json` + pipeline weights.

### Question set (fixed — 7 max)

| # | ID | Type | Question | Options / Scale |
|---|-----|------|----------|-----------------|
| 1 | `primary_goal` | **MCQ** (single) | What is your **primary** goal for the next 6 months? | Job search · Consulting & clients · Thought leadership · Career pivot · Network expansion · Fundraising / investors · Hiring / talent |
| 2 | `time_horizon` | **Slider** 1–3 | How far ahead should the action plan optimize? | 1 = 3 months · 2 = 6 months · 3 = 12 months |
| 3 | `geo_focus` | **MCQ** (single) | Primary geography for opportunities | My country only · Region · Global remote · Specific city (free text follow-up) |
| 4 | `industry_focus` | **MCQ** (multi, max 3) | Which industries matter most? | Tech · Finance · Healthcare · Gov / Public · Energy · Consulting · Consumer · Other (text) |
| 5 | `seniority_path` | **MCQ** (single) | Target seniority trajectory | IC expert · Manager · Director+ · Founder · Board / advisor |
| 6 | `outreach_style` | **Slider** 1–5 | How aggressive should connection/outreach suggestions be? | 1 = warm intros only · 5 = include thoughtful cold outreach |
| 7 | `content_cadence` | **MCQ** (single) | How often will you publish on LinkedIn? | Rarely · Monthly · Bi-weekly · Weekly · Multiple per week |

### Agent behavior

- Present questions in chat (or form if UI exists later)
- Do **not** start synthesis until all 7 answered or user explicitly skips (defaults documented)
- Write `intake_responses.json` + generate `subject_profile.json` from export headline + intake

### Weight mapping (how intake steers synthesis)

| Intake field | Pipeline effect |
|--------------|-----------------|
| `primary_goal` | Rank jobs vs business opps vs content vs connections |
| `time_horizon` | Action plan length; job recency window |
| `geo_focus` | Location scoring; sector news locale |
| `industry_focus` | Sector scanner weights; PYMK sector filter |
| `seniority_path` | Senior target tiers; job seniority match |
| `outreach_style` | Cold vs warm templates; connection count per month |
| `content_cadence` | Number of post drafts; calendar density |

### Deliverables (build)

- [ ] `templates/intake_questions.json` — machine-readable question schema
- [ ] `scripts/intake_to_profile.py` — intake + export → `subject_profile.json`
- [ ] `references/intake_flow.md` — agent script for asking questions

---

## 6. Phase D — Synthesis Pipeline

Single orchestrator: `scripts/run_generic_pipeline.py` (new)

### Inputs

| Input | Required | Source |
|-------|----------|--------|
| `intake_responses.json` | Yes | Phase C |
| `subject_profile.json` | Yes | Phase C + export |
| `network.json` | Preferred | Phase B export |
| Exploration snapshots | Optional | Phase A live session |

### Modules (existing + new)

| Module | Script | Output |
|--------|--------|--------|
| Network index | `build_network_index.py` | `network_index.csv/html` |
| Skills intelligence | `skills_intelligence.py` | `skills_roadmap.md` |
| Sector opportunities | `sector_opportunity.py` | `sector_opportunities.csv` |
| Business opportunities | `business_opportunity.py` | `business_opportunities.md` |
| Senior / connection targets | `senior_recommendations.py` | `senior_targets.csv`, `connection_suggestions.csv` |
| Content strategy | `content_recommendations.py` | `post_recommendations.md` |
| Live jobs | `parse_jobs_from_snapshot.py` + scoring | `job_pipeline.csv` |
| Scores & drafts | `run_scores_drafts_posts.py` | drafts (optional) |
| Leadership intel | `leadership_intel.py` (planned) | `leadership_map.csv` |
| Exploration | `explore_linkedin.bat` | snapshots |

### Synthesis outputs (generic person)

1. **Connection suggestions** — ranked PYMK-style targets from network gaps + sector fit  
2. **Business opportunities** — consulting, intros, advisory, partnerships  
3. **Job pipeline** — if `primary_goal` includes job search  
4. **Content plan** — if `content_cadence` ≥ monthly  
5. **Skills roadmap** — gaps vs target roles  
6. **Referral map** — companies × connections  
7. **6-month action backlog** — see Phase E  

---

## 7. Phase E — Intelligence Dashboard (Fixed Format)

### Design goals

- **Same layout for every user** — comparable sections, comparable metrics  
- **Action-oriented** — every chart/table links to a human-gated action  
- **6-month horizon** — default from intake `time_horizon`  
- **Local HTML** — `intelligence_dashboard.html` in gitignored workspace  
- **Optional export** — xlsx/docx via companion skills  

### Dashboard sections (fixed order)

| # | Section | Data source | User sees |
|---|---------|-------------|-----------|
| 1 | **Executive summary** | All modules | 3 strengths, 3 gaps, top priority this week |
| 2 | **Growth metrics scorecard** | See §8 | Current vs target vs 6-month goal |
| 3 | **Network intelligence** | Export | Connections by industry/seniority; referral heatmap |
| 4 | **Connection suggestions** | senior_targets + PYMK | Top 15 people to connect/nurture + draft note |
| 5 | **Job pipeline** | job_pipeline.csv | Scored roles (if job goal) |
| 6 | **Business opportunities** | business_opportunities.md | Top 10 opps with next action |
| 7 | **Content & visibility** | analytics + post recs | Cadence plan + draft posts |
| 8 | **Skills & learning** | skills_roadmap | Top 5 skills to add |
| 9 | **6-month action plan** | Synthesizer | Month-by-month checklist |
| 10 | **Human gates** | Static | What agent will never auto-do |

### Generator

```bash
python scripts/build_intelligence_dashboard.py \
  --workspace linkedin-job-workspace \
  --intake linkedin-job-workspace/intake_responses.json
```

Extends `build_dashboard.py` with full intelligence layout + metrics scorecard.

---

## 8. Professional Growth Metrics (Scorecard)

Metrics are **normalized 0–100** where possible. Baseline from export + live snapshots; targets from intake.

| Metric ID | Name | Baseline source | Why it matters | 6-month target (default) |
|-----------|------|-----------------|----------------|--------------------------|
| `M1` | **Network relevance** | % connections in target industries | Quality > quantity | +15 pts |
| `M2` | **Senior access** | Count of Director+ in target sectors | Opportunities flow through seniors | +10 relationships |
| `M3` | **Referral readiness** | Companies with 1st-degree contacts | Warm job/BD paths | +20 companies mapped |
| `M4` | **Profile visibility** | Profile viewers / 90d (live) | Inbound interest | +30% viewers |
| `M5` | **Content reach** | Impressions / 7d (live) | Thought leadership | +50% impressions |
| `M6` | **Engagement depth** | Engagements ÷ impressions | Algorithm + trust | ≥3% rate |
| `M7` | **Skills market fit** | Skills roadmap coverage % | Employability | 80% top-5 skills addressed |
| `M8` | **Pipeline velocity** | Jobs/opps moved to `contacted` | Execution | 12 meaningful outreach/month |
| `M9` | **Posting consistency** | Posts per month vs intake cadence | Visibility habit | Match stated cadence |
| `M10` | **Opportunity funnel** | BD opps → meetings booked (user-reported) | Business growth | User sets in intake |

Dashboard shows: **Current · Target · Gap · Next action** per metric.

---

## 9. Six-Month Action Plan Format

Stored as `action_plan_6mo.md` + JSON for dashboard.

### Structure

```markdown
# 6-Month Professional Growth Plan — [Name]

**Primary goal:** [from intake]
**Generated:** [date]
**Review cadence:** Monthly (user + agent)

## Month 1 — Foundation
- [ ] Metric focus: M1 Network relevance, M7 Skills
- [ ] Actions (human-gated): ...

## Month 2 — Outreach
...

## Month 6 — Review & reset
- [ ] Re-run export + exploration
- [ ] Compare scorecard to baseline
```

### Action types (always human-gated)

| Action type | Example |
|-------------|---------|
| `CONNECT` | Send connection request to [name] |
| `NURTURE` | Message profile viewer [name] |
| `APPLY` | Submit application for [job] after draft review |
| `POST` | Publish draft post #2 |
| `LEARN` | Complete skill module [X] |
| `RESEARCH` | Leadership intel on [company] |
| `INTRO` | Request intro via [mutual] |

---

## 10. Public GitHub Skill Structure (Target)

```
linkedin-network-and-job-operator/
├── SKILL.md                      # Agent entry — phases A→E
├── README.md                     # Human install guide
├── docs/
│   ├── GENERIC_SKILL_PLAN.md     # This document
│   ├── USE_CASES.md
│   ├── PERSONAS.md
│   └── ...
├── references/
│   ├── onboarding_playwright.md  # NEW — Phase A
│   ├── linkedin_data_export_guide.md  # NEW — Phase B
│   ├── intake_flow.md            # NEW — Phase C
│   └── privacy_rules.md
├── templates/
│   ├── intake_questions.json     # NEW
│   ├── growth_metrics.json       # NEW
│   ├── dashboard_layout.json     # NEW
│   └── subject_profile_schema.json
└── scripts/
    ├── verify_browser_session.py     # NEW
    ├── check_export_ready.py         # NEW
    ├── intake_to_profile.py          # NEW
    ├── run_generic_pipeline.py       # NEW — orchestrator
    └── build_intelligence_dashboard.py  # NEW
```

---

## 11. Implementation Phases

| Phase | Scope | Est. | Depends on |
|-------|-------|------|------------|
| **G1** | Onboarding docs + verify_browser_session | 1 week | — |
| **G2** | Export guide + check_export_ready | 3 days | — |
| **G3** | Intake schema + intake_to_profile + agent flow in SKILL.md | 1 week | G2 |
| **G4** | run_generic_pipeline orchestrator | 1 week | G3 |
| **G5** | growth_metrics.json + action plan generator | 1 week | G4 |
| **G6** | build_intelligence_dashboard.html (fixed layout) | 2 weeks | G5 |
| **G7** | connection_suggestions.csv module | 1 week | G4 |
| **G8** | End-to-end test with synthetic + one live user | 1 week | G6 |
| **G9** | README polish + GitHub template repo | 3 days | G8 |

**Total:** ~8–10 weeks to full generic v1.

### Already shipped (reuse)

- Playwright attach scripts  
- `explore_linkedin.bat` + parsers  
- `run_scores_drafts_posts.py`  
- Network parse + intelligence modules  
- USE_CASES / PERSONAS docs  

---

## 12. Agent SKILL.md Rewrite (Outline)

Replace "Phase 0 bootstrap only" with:

1. **Onboarding gate** — don't proceed without browser verified  
2. **Export gate** — explain limitation if no export; proceed with live-only mode  
3. **Intake gate** — 7 questions mandatory before synthesis  
4. **Synthesis** — `run_generic_pipeline.py`  
5. **Dashboard** — open `intelligence_dashboard.html`; walk user through top 5 actions  
6. **Monthly refresh** — re-explore + update metrics (user-initiated)  

---

## 13. Success Criteria (Generic v1)

| Criterion | Target |
|-----------|--------|
| Any user can complete Phase A in <15 min | Setup doc + verify script |
| Export path works for standard LinkedIn ZIP | parse + validate |
| Intake ≤7 questions before synthesis | Enforced in SKILL.md |
| Dashboard renders with ≥8 sections | Fixed layout |
| 6-month plan has ≥3 actions/month | Generator |
| Zero PII in GitHub repo | audit |
| Connection + business opp suggestions | ≥10 each when export present |

---

## 14. Out of Scope (v1)

- Hosted SaaS / cloud dashboard  
- LinkedIn OAuth app  
- Auto-send messages or auto-apply  
- Mobile LinkedIn app automation  
- Guaranteed MCQ UI in Cursor (chat-based MCQ is v1; form UI v2)  

---

## 15. Next Build Step

**Start G1 + G3 in parallel:**

1. Add `templates/intake_questions.json` + `references/intake_flow.md`  
2. Add `scripts/intake_to_profile.py`  
3. Rewrite SKILL.md Phase A–C gates  
4. Stub `build_intelligence_dashboard.py` with scorecard + placeholder sections  

---

## Related docs

- [USE_CASES.md](./USE_CASES.md)  
- [ROADMAP.md](./ROADMAP.md)  
- [ARCHITECTURE.md](./ARCHITECTURE.md)  
- [PERSONAS.md](./PERSONAS.md)