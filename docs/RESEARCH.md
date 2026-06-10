# Research: LinkedIn Network & Career Intelligence Platform

**Date:** 2026-06-10  
**Status:** Research complete → implementation starting  
**Repo:** [linkedin-network-and-job-operator](https://github.com/tsinghkothari-droid/linkedin-network-and-job-operator)

---

## 1. Executive Summary

The user wants to evolve the existing skill from a job-application assistant into a **full-stack career intelligence operator** that:

1. **Starts at browser launch** — Chrome controlled via `playwright-cli` (not MCP-first)
2. Runs **end-to-end** from session bootstrap through network analysis, job discovery, referrals, applications, and content strategy
3. Supports **analyzing a different person's profile** than the operator (consultant/recruiter/coach mode)
4. Produces deep intelligence outputs:
   - Skills to build (personalized, not generic lists)
   - Sectoral opportunities
   - Business opportunities visible through the network
   - Leadership mapping (who runs organizations)
   - Senior people recommendations on LinkedIn
   - Post recommendations tuned to what would interest *their* network

All of this must respect the existing hard rules: no private API scraping, no credential storage, human review before irreversible actions.

---

## 2. Browser Control: Playwright CLI vs MCP

### Finding

Microsoft shipped **`playwright-cli`** (`@playwright/cli`) as a token-efficient browser automation layer designed specifically for coding agents. It uses a **daemon architecture** with persistent browser processes, ref-based snapshots, and named sessions.

| Dimension | Playwright CLI | Playwright MCP |
|-----------|----------------|----------------|
| Integration | Shell commands from agent | Tool calls with JSON schemas |
| Token cost | Lower (concise snapshots) | Higher (full tool schemas + trees) |
| Default mode | Headless | Headed |
| Session persistence | `--persistent`, named `-s=session` | Depends on MCP server config |
| Best for | Step-by-step workflows in coding agents | Exploratory long-running loops |

**Recommendation:** Make **Playwright CLI the primary control plane** for this skill. Keep MCP as fallback when CLI is unavailable. Use **headed Chrome** (`--browser=chrome --headed`) so the user can see and intervene (login, CAPTCHA, review).

### Bootstrap sequence (researched)

```bash
# Install once
npm install -g @playwright/cli@latest
playwright-cli install --skills   # optional: agent skill for CLI itself

# Per-workspace session (persistent profile on disk, NOT committed)
playwright-cli -s=linkedin-ops open https://www.linkedin.com/feed/ \
  --browser=chrome --headed --persistent

# Human logs in manually if needed, then agent continues
playwright-cli -s=linkedin-ops snapshot
playwright-cli -s=linkedin-ops goto "https://www.linkedin.com/jobs/"
playwright-cli -s=linkedin-ops snapshot --filename=jobs-page.yml
```

### Session safety (aligned with privacy rules)

- Use `--persistent` with a **local gitignored profile path** (e.g. `.playwright-profiles/linkedin-ops/`)
- **Do NOT** run `state-save` containing cookies into the repo
- **Do NOT** automate login — user logs in manually in headed Chrome
- On CAPTCHA → stop and hand back to user
- Use `playwright-cli show` for visual session monitoring

Sources:
- [Playwright CLI docs](https://playwright.dev/docs/getting-started-cli)
- [Playwright Agent CLI introduction](https://playwright.dev/agent-cli/introduction)
- [Playwright CLI GitHub](https://github.com/microsoft/playwright-cli)

---

## 3. Skills Intelligence: What to Build for a Person

### Data sources (public / user-provided)

| Source | Use |
|--------|-----|
| LinkedIn Skills on the Rise 2026 | Macro skill demand baseline |
| LinkedIn Economic Graph / Labor Market Report 2026 | Sector hiring, AI literacy growth |
| O*NET / CareerOneStop Skills Gap API | Occupation-to-occupation skill deltas |
| User export (`Profile.csv`, `Positions.csv`, `Skills.csv`) | Ground truth for subject |
| Target roles (user-defined) | Destination occupation |
| Visible job postings (browser) | Market-specific requirement extraction |

### LinkedIn Skills on the Rise 2026 (macro trends)

Fastest-growing skill clusters globally:

1. **Leadership & People Management** — cross-functional collaboration, team management, mentorship
2. **Business & Revenue Growth** — GTM strategy, business development
3. **Technical & Strategic AI** — prompt engineering, LLMs, AI business strategy
4. **Risk & Compliance** — GRC, governance

Key stat: employers increasingly prioritize **demonstrated skills** over degrees and linear career paths.

Source: [LinkedIn Skills on the Rise 2026](https://news.linkedin.com/2026/Skills-on-the-rise-2026)

### Skills gap methodology (recommended)

Use a **three-layer model**:

```
Layer 1: Current skills     ← LinkedIn export + profile JSON
Layer 2: Target role skills ← O*NET / job posting extraction
Layer 3: Adjacent skills    ← "bridge skills" for career pivots
```

**Gap score** per skill:
```
priority = demand_weight × gap_size × transition_relevance
```

Where:
- `demand_weight` = frequency in target job postings + Skills-on-the-Rise boost
- `gap_size` = not present in subject profile
- `transition_relevance` = how often the skill appears on shortest paths between current and target occupation (O*NET Job Zone transitions)

**Output:** `skills_roadmap.json` + `skills_roadmap.md` with:
- Top 10 skills to acquire (ranked)
- Suggested learning resources (LinkedIn Learning, public courses)
- Estimated time-to-competency bands
- Which skills to add to LinkedIn profile first (recruiter visibility)

Sources:
- [O*NET Skills Gap API](https://www.careeronestop.org/Developers/WebAPI/SkillsGaps/get-skills-gaps-between-two-occupations.aspx)
- [O*NET Job Zone Transitions](https://www.onetcenter.org/reports/Job_Zone_Transition.html)
- [Lightcast/O*NET skills mapping](https://lightcast.io/resources/blog/onet-skills-lightcast-skills)

### "Different work profile than mine" mode

Introduce two profile concepts:

| Profile | Purpose |
|---------|---------|
| `operator_profile.json` | You (the person running the agent) |
| `subject_profile.json` | The person being analyzed (client, friend, alternate career self) |

All scoring, skills gaps, post recommendations, and job fit run against **subject_profile**. Network data comes from **subject's LinkedIn export** or visible browser session. Operator profile is only used when comparing "what I could intro" vs "what they need."

---

## 4. Sectoral & Business Opportunity Intelligence

### Sectoral opportunity framework

Combine **top-down** and **bottom-up** signals:

**Top-down (public research)**
- LinkedIn Economic Graph labor reports (hiring by sector, AI job growth)
- LinkedIn Jobs on the Rise 2026 (25 fastest-growing US roles)
- Government/industry reports for target geography

**Bottom-up (network-derived)**
- Industry distribution of subject's connections
- Seniority concentration by sector
- Company growth signals (hiring posts, funding news from public web)
- Gap analysis: sectors where subject has network access but no current presence

**Opportunity score per sector:**
```
sector_score = (
  0.30 × market_growth_signal +
  0.25 × network_access_score +
  0.20 × skills_fit_score +
  0.15 × geographic_fit +
  0.10 × subject_interest_match
)
```

### Business opportunity types to detect

| Type | Signal | Example output |
|------|--------|----------------|
| **Warm intro arbitrage** | Subject connected to decision-makers in growing sector | "Intro to 3 fintech founders hiring PMs" |
| **Consulting/advisory gap** | Many junior contacts, few seniors in sector subject knows | "Advisory opportunity in healthtech compliance" |
| **Co-founder/partner match** | Founders in network lacking skills subject has | "2 founders need GTM help" |
| **Talent placement** | Recruiters + hiring managers concentrated | "Referral-side business in AI infra" |
| **Content/thought leadership** | Underserved topic in network's feed interests | "Post series on X — high engagement potential" |
| **Sector transition bridge** | Adjacent industry overlap | "Move from SaaS → fintech via payments network" |

Sources:
- [LinkedIn Labor Market Report 2026](https://economicgraph.linkedin.com/research/labor-market-report-2026)
- [LinkedIn Workforce Report Jan 2026](https://economicgraph.linkedin.com/resources/linkedin-workforce-report-january-2026)

Key 2026 labor market facts:
- US jobs requiring AI literacy grew **70% YoY**
- **1.3M** new AI-enabled jobs emerged globally in 2 years
- Hiring down 20–35% in advanced economies vs pre-pandemic
- **52%** of people job hunting in 2026; **80%** feel unprepared

---

## 5. Leadership Intelligence: Who Runs Organizations

### Public-source hierarchy (use in order)

1. **Company website** — About / Leadership / Team pages
2. **SEC filings** (10-K, DEF 14A) — named executives for public companies
3. **Press releases** — appointment announcements
4. **LinkedIn company page** — visible employee list (browser snapshot, not API)
5. **Crunchbase / Wikipedia** — leadership for startups (public profiles)
6. **Industry publications** — trade press executive coverage

### Workflow

```
Input: company name(s) or sector
  → Web search: "[company] CEO CFO leadership team 2026"
  → Browser: company /about page snapshot
  → Cross-reference with subject's network (company_network_map.csv)
  → Output: leadership_map.csv
```

**Output schema:**
```
company,role,person_name,source_url,confidence,linkedin_url_if_public,in_network(yes/no)
```

### Group / org cluster analysis

For "group of organisations" (e.g. portfolio companies, industry association members):
- Accept a CSV of company names
- Batch leadership lookup via web research + browser
- Produce `org_cluster_leadership.csv`
- Highlight where subject has 1st-degree paths to leadership

**Hard rule:** Only use publicly visible information. Do not scrape LinkedIn's internal search API.

---

## 6. Senior People Recommendations on LinkedIn

### Who qualifies as "senior" for recommendations

| Tier | Criteria | Use case |
|------|----------|----------|
| T1 | C-suite, Founder, GP, Board | Strategic intros, advisory |
| T2 | VP, Director, Head of | Hiring influence, referrals |
| T3 | Principal, Staff, Senior Manager | Peer credibility, warm paths |
| T4 | Recruiter, TA Leader | Direct pipeline access |

### Ranking model

```
senior_target_score = (
  0.25 × seniority_tier +
  0.25 × industry_match +
  0.20 × network_proximity +
  0.15 × role_relevance +
  0.15 × engagement_likelihood
)
```

**network_proximity:**
- 1st degree = 100
- 2nd degree with mutual = 60
- No path but same industry event/company alumni = 30

**engagement_likelihood** (inferred from public signals):
- Recent posts about hiring/growth
- Active commenter in subject's topic area
- Shared groups/school (from export metadata)

### Output types

1. **Connect recommendations** — people subject should request to connect with (and why)
2. **Nurture recommendations** — existing connections to re-engage
3. **Intro recommendations** — paths through mutual connections
4. **Follow recommendations** — senior voices to follow for sector intelligence (public profiles only)

---

## 7. Content Strategy & Post Recommendations

### LinkedIn algorithm 2026 (research summary)

The 2026 algorithm prioritizes **Depth Score** over vanity metrics:

| Signal | Weight | Implication |
|--------|--------|-------------|
| Dwell time | Primary | Longer-value content wins |
| Comment depth | High | Multi-reply threads boost reach |
| Saves | High | Reference-quality content |
| Private shares | High | DM shares = strong signal |
| External links | **~60% reach penalty** | Keep content native |
| Engagement bait | **Suppressed** | No "comment YES" patterns |
| Engagement pods | **Shadowban risk** | Never automate reciprocal engagement |

**Best formats 2026:**
1. Document carousels (6–9 slides) — highest dwell
2. Native video (<30s, captioned)
3. Long-form text (1,200–1,800 chars)
4. LinkedIn newsletters (bypasses feed algorithm for subscribers)

Sources:
- [LinkedIn Algorithm 2026 Guide (Digital Applied)](https://www.digitalapplied.com/blog/linkedin-algorithm-2026-engagement-strategy-guide)
- [LinkedIn Content Playbook 2026](https://www.linkedin.com/pulse/linkedin-content-has-changed-heres-2026-playbook-anas-hidaoui-fayme)

### Network-interest modeling

To recommend posts that interest **their** network (not generic viral content):

1. **Analyze connection composition** — industries, seniority, roles from export
2. **Infer audience clusters** — e.g. "42% fintech operators, 18% recruiters, 15% founders"
3. **Map topic pillars** — 2–3 themes at intersection of subject expertise + audience demand
4. **Cross-reference Skills on the Rise** — timely skill angles
5. **Generate post calendar** — 3–5 posts/week with format mix

**Per-post output:**
```markdown
## Post Idea: [Title]
- **Audience cluster:** Fintech operators (38% of network)
- **Format:** 7-slide carousel
- **Hook:** [first line]
- **Depth Score potential:** High (framework + data)
- **Why this network cares:** [specific reason]
- **CTA:** Open question to drive comment depth
- **Avoid:** External links in post body
```

### Post topic sources

| Source | Topics generated |
|--------|------------------|
| Subject's skills + gaps | "What I learned transitioning to X" |
| Sector opportunities | "3 trends in [sector] hiring" |
| Network composition | "What [role] professionals get wrong about [topic]" |
| Job market data | "Skills on the Rise: what recruiters actually want" |
| Leadership intel | "What [Company]'s new direction means for [role]" |

---

## 8. Companion Skills to Build

See `docs/COMPANION_SKILLS.md` for full spec. Summary:

| Skill | Purpose |
|-------|---------|
| `linkedin-skills-intelligence` | Skills gap + roadmap for any subject profile |
| `linkedin-sector-scanner` | Sectoral opportunity scoring from network + public data |
| `linkedin-leadership-intel` | Who runs orgs — public source aggregation |
| `linkedin-senior-target-finder` | Rank senior people to connect/nurture |
| `linkedin-content-strategist` | Post recommendations for subject's network |
| `playwright-cli-browser-ops` | Reusable Chrome bootstrap (shared dependency) |

These can be **modules within this skill** initially, then extracted as standalone skills once stable.

---

## 9. End-to-End Flow (Target State)

```
┌─────────────────────────────────────────────────────────────┐
│ PHASE 0: BOOTSTRAP                                          │
│ playwright-cli -s=linkedin-ops open linkedin.com --headed   │
│ User logs in → agent verifies feed visible → snapshot       │
└──────────────────────────┬──────────────────────────────────┘
                           ▼
┌─────────────────────────────────────────────────────────────┐
│ PHASE 1: INTAKE                                             │
│ subject_profile.json + export ZIP + target goals            │
│ "Analyze for someone else" vs "Analyze for me"              │
└──────────────────────────┬──────────────────────────────────┘
                           ▼
┌─────────────────────────────────────────────────────────────┐
│ PHASE 2: NETWORK INTELLIGENCE (Workflow 1)                  │
│ Parse export → classify → index → company map               │
└──────────────────────────┬──────────────────────────────────┘
                           ▼
┌─────────────────────────────────────────────────────────────┐
│ PHASE 3: DEEP INTELLIGENCE (Workflows 5–9)                  │
│ Skills roadmap | Sector opps | Business opps | Leadership   │
│ Senior targets | Post recommendations                       │
└──────────────────────────┬──────────────────────────────────┘
                           ▼
┌─────────────────────────────────────────────────────────────┐
│ PHASE 4: JOB PIPELINE (Workflows 2–4)                       │
│ Browser job search → score → referral-first → drafts        │
└──────────────────────────┬──────────────────────────────────┘
                           ▼
┌─────────────────────────────────────────────────────────────┐
│ PHASE 5: HUMAN REVIEW & ACTION                              │
│ Dashboard HTML | outreach drafts | application checklists   │
│ User submits / sends / posts manually                       │
└─────────────────────────────────────────────────────────────┘
```

---

## 10. Risk Register

| Risk | Mitigation |
|------|------------|
| LinkedIn ToS violation | Visible content + export only; no hidden APIs |
| Account restriction | Rate-limit navigation; headed mode; human login |
| PII leak to GitHub | Strict .gitignore; workspace-local outputs |
| Stale leadership data | Source URL + confidence + date on every row |
| Generic post advice | Always tie to network composition data |
| Wrong person analyzed | Explicit subject_profile.json confirmation step |
| Cookie persistence | Gitignore `.playwright-profiles/`; never state-save to repo |

---

## 11. Implementation Phases

See `docs/ROADMAP.md`. Phase 1 (this commit) delivers:
- Research docs on GitHub
- Playwright CLI bootstrap scripts
- Subject profile intake
- Skills intelligence script (O*NET-style gap logic)
- Sector/opportunity scanner stub
- Leadership lookup via web search
- Post recommendation generator
- Updated SKILL.md with workflows 5–9

---

## References

1. [Playwright CLI Getting Started](https://playwright.dev/docs/getting-started-cli)
2. [Playwright Agent CLI](https://playwright.dev/agent-cli/introduction)
3. [LinkedIn Skills on the Rise 2026](https://news.linkedin.com/2026/Skills-on-the-rise-2026)
4. [LinkedIn Labor Market Report 2026](https://economicgraph.linkedin.com/research/labor-market-report-2026)
5. [LinkedIn Algorithm 2026](https://www.digitalapplied.com/blog/linkedin-algorithm-2026-engagement-strategy-guide)
6. [O*NET Skills Gap API](https://www.careeronestop.org/Developers/WebAPI/SkillsGaps/get-skills-gaps-between-two-occupations.aspx)
7. [O*NET Job Zone Transitions](https://www.onetcenter.org/reports/Job_Zone_Transition.html)
8. [CareerOneStop Skills API](https://www.careeronestop.org/Developers/WebAPI/Skills/)