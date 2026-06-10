# Use Cases: LinkedIn Network & Job Operator

**Audience:** Anyone using Codex, Cursor, or Grok with this skill — job seekers, founders, consultants, creators, recruiters, coaches, and operators who want **human-in-the-loop** career and business intelligence.

**Principle:** The agent reads **visible** LinkedIn content and **your exported data**. It drafts, scores, and recommends. **You** connect, post, and apply.

---

## 1. Who This Is For

| Persona | Primary goals | Best workflows |
|---------|---------------|----------------|
| **Active job seeker** | Find roles, get referrals, apply with quality | 2 → 4 → 3 |
| **Passive job seeker** | Monitor market, stay ready, nurture network | 2, 4, 9, 10 |
| **Career changer** | Skills gap, sector pivot, new connections | 5, 6, 1, 8 |
| **Freelancer / consultant** | Clients, advisory gigs, visibility | 6, 9, 10, 4 |
| **Founder / operator** | Hires, partners, investors, thought leadership | 6, 7, 8, 9 |
| **Sales / BD** | Warm paths, account intel, timing signals | 1, 4, 7, 10 |
| **Content creator** | Posts, newsletters, audience growth | 9, 10 |
| **Recruiter / coach** | Analyze *someone else's* network (subject mode) | 1, 5, 8, 2 |
| **Company page admin** | Page growth, cross-promotion, hiring brand | 10, 9 |
| **Industry researcher** | Trends, new entrants, sector maps | 6, 7, 10 + external research |
| **Student / early career** | Skills roadmap, PYMK, first network | 5, 8, 2 |

---

## 2. Core Use Categories

### A. Job search & applications

**For people at large:** Most users want a structured path from discovery to apply — without spam or auto-submit risk.

| Use case | What the agent does | You do | Outputs |
|----------|---------------------|--------|---------|
| **Role discovery** | Search LinkedIn Jobs (logged-in or public), filter by keywords/location/recency | Confirm search criteria | `job_pipeline.csv` |
| **Job scoring** | Score fit, relevance, network overlap, application effort | Pick top N to pursue | Scored rows + dashboard |
| **Referral-first apply** | Find 1st-degree contacts at target companies; draft short referral asks | Send messages; wait or waive referral | `referral_targets.csv`, `outreach_messages.md` |
| **Application pack** | Summarize JD, gap analysis, tailored cover letter / answers | Review; fix gaps honestly | `application_drafts/` |
| **Form prefill (reviewed)** | Fill name, email, LinkedIn URL, work history in Easy Apply | Approve each field; **click Submit yourself** | Screenshots + checklist |
| **Pipeline tracking** | Status: discovered → referral_pending → draft_ready → submitted | Update status when you submit | `application_status_dashboard.html` |
| **Interview prep hook** | Pull job + company intel + leadership map for talking points | Practice and interview | Brief in workspace |

**Trigger phrases:** `find jobs on linkedin`, `job application assistant`, `referral strategy`, `score these roles`

**Workflows:** 2, 4, 3 · **Scripts:** `parse_jobs_from_snapshot.py`, `run_scores_drafts_posts.py`, `build_dashboard.py`

**Limits:** No mass apply. No Submit without per-job approval. Stop on CAPTCHA or rate limits.

---

### B. Content creation & posting

**For people at large:** LinkedIn rewards consistency and depth; most people struggle with *what* to post and *whether* it worked.

| Use case | What the agent does | You do | Outputs |
|----------|---------------------|--------|---------|
| **Post ideation** | Ideas tuned to your network clusters (industry × seniority) | Pick topics | `post_recommendations.md` |
| **Carousel / long-form drafts** | 6–9 slide outlines or 1,200–1,800 char posts (2026 algorithm norms) | Edit voice; publish | Drafts in workspace |
| **Newsletter issues** | Themes from your 100+ subscriptions + sector news | Publish newsletter | Issue outline |
| **Performance loop** | Read creator analytics (impressions, engagement, top posts) | Adjust calendar | Metrics summary |
| **Audience targeting** | Follower demographics → topic timing | Approve content plan | Audience notes |
| **Multi-page content** | Calendar across personal profile + company pages you admin | Post per page | Per-page draft folder |
| **Comment strategy** | Triage notifications; suggest thoughtful replies | Post replies | `engagement_triage.md` |
| **Repurpose** | Turn a post into carousel bullets or article outline | Publish one format | Multiple draft files |

**Trigger phrases:** `what should I post`, `content strategy`, `linkedin carousel`, `newsletter ideas`

**Workflows:** 9, 10 · **Scripts:** `content_recommendations.py`, `parse_exploration.py` (analytics pages)

**Limits:** Agent never auto-publishes, never engagement-pods, never buys fake views.

---

### C. Trend & signal identification

**For people at large:** Spot what is changing in an industry before it is obvious in job titles alone.

| Use case | What the agent does | You do | Outputs |
|----------|---------------------|--------|---------|
| **Skills on the rise** | Weight macro skills (e.g. Skills on the Rise 2026) vs your profile | Learn or add to profile | `skills_roadmap.md` |
| **Feed & notification signals** | Hiring posts, job-change congrats, promoted content patterns | Act on high-signal items | Signal digest |
| **Newsletter / subscription scan** | Map what 50–100 newsletters you follow are discussing | Write timely commentary | `newsletter_intel.md` |
| **Sector heat map** | Score sectors by growth × your network access × skills fit | Target sectors | `sector_opportunities.csv` |
| **Company hiring pulses** | Jobs posted last 7 days in sector + geography | Prioritize employers | Job pipeline slice |
| **Profile viewer intent** | "19 viewers at companies with open roles", "7 senior leaders same function" | Nurture or apply | Viewer analytics summary |
| **External news** | SearXNG scrape on sector keywords (govtech, AI, etc.) | Validate sources | Research report `.md` |

**Trigger phrases:** `sector opportunities`, `skills gap`, `what's trending in [industry]`, `hiring signals`

**Workflows:** 5, 6, 10 + `searxng-scrapling-research` skill

**Limits:** Trends are probabilistic; always cite sources for external claims.

---

### D. Business opportunity identification

**For people at large:** Not everyone is job-hunting — many want clients, advisory work, partnerships, or deal flow.

| Use case | What the agent does | You do | Outputs |
|----------|---------------------|--------|---------|
| **Consulting lead finder** | Companies posting strategy/ops/DD roles → prospect list | Outreach | `business_opportunities.md` |
| **Warm intro arbitrage** | Match network seniors to people asking for intros | Make intro (double opt-in) | Intro drafts |
| **Advisory / fractional fit** | Founders in network lacking your skill area | Offer office hours | Target list |
| **Co-founder / partner match** | Skill complementarity in network graph | Start conversation | Ranked matches |
| **Talent placement** | Recruiter-heavy clusters in network | Refer candidates | Cluster map |
| **Event / group commercial ops** | Pre-event connect list from attendee companies | Attend prepared | Event prep brief |
| **RFP / gov tender awareness** | Public tender pages + sector news (external) | Bid or partner | Tender watch list |
| **Investor / analyst sourcing** | Leadership map + hiring in portfolio companies | Research calls | `leadership_map.csv` |

**Trigger phrases:** `business opportunities in my network`, `consulting leads`, `who should I partner with`

**Workflows:** 6, 7, 1, 4 · **Scripts:** `business_opportunity.py`, `sector_opportunity.py`, `senior_recommendations.py`

---

### E. Network growth & “who’s new in the industry”

**For people at large:** Discover who to connect with — new entrants, rising voices, hiring managers, and dormant ties.

| Use case | What the agent does | You do | Outputs |
|----------|---------------------|--------|---------|
| **PYMK ranking** | Score People You May Know by sector fit + mutual connections | Send connect requests | Ranked PYMK list |
| **Invitation triage** | Accept/ignore recommendations with rationale | Click Accept/Ignore | Decision log |
| **Senior target list** | Rank T1–T4 leaders aligned to your goals | Connect or nurture | `senior_targets.csv` |
| **Profile viewer nurture** | Recent viewers (named or blurred titles) → draft messages | Send | `outreach_messages.md` |
| **Job-change congrats** | Notifications: new roles at target companies | Short congrats → conversation | Message drafts |
| **Second-degree paths** | Export-based graph: friend-of-friend to hiring manager | Ask for intro | Path report |
| **Industry newcomer scan** | Follow suggestions, new voices in newsletters/groups | Follow selectively | New voices CSV |
| **Dormant tie revival** | Connections at target companies you have not spoken to | Re-engage | Reconnect drafts |
| **Alumni / geo clusters** | School and city clusters in export | Event or bulk nurture | Cluster index |

**Trigger phrases:** `senior people to connect`, `who viewed my profile`, `grow my network in [sector]`

**Workflows:** 1, 8, 10, 4 · **Exploration pages:** network, profile-views, notifications

**Limits:** No mass connection automation. No scraping private member lists.

---

### F. Skills & career development

| Use case | What the agent does | You do | Outputs |
|----------|---------------------|--------|---------|
| **Skills gap analysis** | Target role vs current skills | Study / certify | `skills_roadmap.md` |
| **Profile skill additions** | What to add to LinkedIn profile first | Edit profile | `profile_skill_additions.md` |
| **Agent skill recommendations** | Suggests new Codex skills to build for your career | Install skills | `recommended_agent_skills.md` |
| **Transition bridges** | Bridge skills for career pivots | Plan learning | Roadmap JSON |
| **Interview skill packs** | Companion skills (e.g. sector interview prep) | Practice | Linked from roadmap |

**Workflows:** 5 · **Coach mode:** run on `subject_profile.json` for clients.

---

### G. Company & brand operations (multi-page)

For users who admin one or more LinkedIn company pages:

| Use case | What the agent does | You do | Outputs |
|----------|---------------------|--------|---------|
| **Page performance** | Follower count, admin analytics snapshot | Invest in growth | Page metrics |
| **Cross-promotion map** | Personal ↔ company page content calendar | Publish | Calendar `.md` |
| **Hiring brand** | Job posts + employee advocacy drafts | Approve posts | Draft posts |
| **Competitor page watch** | Public company page snapshots | Adjust positioning | Competitor notes |

**Workflows:** 10, 9 · **Exploration:** company admin URLs, creator analytics

---

## 3. Cross-Platform & Other Sites

LinkedIn is the **primary** surface. This skill extends to other sites **only through visible browser content or public research** — same privacy rules apply.

| Site / source | Use case | How |
|---------------|----------|-----|
| **LinkedIn** | Jobs, network, analytics, pages, newsletters, groups, events | Playwright CLI extension attach or export ZIP |
| **Company career pages** | Roles not on LinkedIn; culture research | `goto` public URL → snapshot |
| **Indeed / Glassdoor / Naukri / Monster** | Wider job market compare | Public search pages only; extract visible cards |
| **Google Jobs** | Aggregated view of openings | Public search → snapshot |
| **Government job portals** | Public sector roles (country-specific) | Public listings only |
| **SearXNG / web search** | Leadership, sector news, tenders, company research | `searxng-scrapling-research` skill |
| **News sites / annual reports** | Validate business opportunities | Research skill → cite URLs |
| **Crunchbase / public filings** | Funding, leadership (public pages) | Browser or research skill |
| **Twitter/X, Substack** | Cross-post drafts (not auto-publish) | Draft in workspace for manual copy |
| **Excel / Word** | Pipeline and memos for stakeholders | `xlsx`, `docx` companion skills |
| **CRM (HubSpot, etc.)** | Sync referral targets | `crm-automation` skill (optional) |

**Not in scope:** Private APIs, credential sharing, scraping logged-in sessions on third-party sites without user-visible browser, or bypassing paywalls.

---

## 4. Human-in-the-Loop Matrix

| Action | Agent | Human |
|--------|-------|-------|
| Read feed, jobs, analytics | ✅ | — |
| Score & rank | ✅ | Approves priorities |
| Draft posts, messages, applications | ✅ | Edits & sends |
| Connect / Accept invite | — | ✅ always |
| Publish post / article / newsletter | — | ✅ always |
| Submit job application | — | ✅ always |
| Send InMail / email | — | ✅ always |
| Pay for Premium / ads | — | ✅ always |
| Export LinkedIn data | — | ✅ (user downloads ZIP) |
| Login / 2FA | — | ✅ always |

---

## 5. Typical Journeys (End-to-End)

### Journey 1: “I need a job in 90 days”

```
Export ZIP → Network index → Skills roadmap → Job search (browser) →
Score pipeline → Referral-first top 10 → Application drafts →
You submit → Dashboard tracks status
```

### Journey 2: “I want visibility in my industry”

```
Creator analytics snapshot → Post recommendations → 3-week calendar →
You publish weekly → Re-read analytics → Tune topics
```

### Journey 3: “I want consulting clients”

```
Sector opportunities → Business opp finder → Senior targets →
Leadership intel on prospects → Draft outreach → You send
```

### Journey 4: “Who should I know in GovTech?”

```
Exploration (jobs + newsletters + network PYMK) → Sector scanner →
New voices list → Connect drafts → You connect
```

### Journey 5: “Coach analyzing a client”

```
subject_profile.json (not operator) → Full pipeline on their export →
Deliver roadmap + job list + post plan → Client acts
```

---

## 6. Exploration Surfaces (Workflow 10)

Automated multi-page capture for discovery:

```bat
scripts\explore_linkedin.bat
python scripts\parse_exploration.py
```

| Page | Unlocks |
|------|---------|
| Feed | Stats, pages, groups, events entry points |
| Network | PYMK, invitations, viewer blur cards |
| Profile views | Viewer analytics, company clusters, nurture |
| Creator analytics | Impressions, engagement, top posts |
| Audience analytics | Follower demographics |
| Jobs search | Live job cards → pipeline |
| Company page | Admin metrics, follower growth |
| Newsletters | Subscription intel, create newsletter |
| Notifications | Hiring posts, job changes, mentions |

---

## 7. Maturity: What Works Today vs Planned

| Capability | Status |
|------------|--------|
| Network export parse & index | ✅ Shipped |
| Skills / sector / business / content / senior intel | ✅ Shipped |
| Playwright extension attach + exploration | ✅ Shipped |
| Job pipeline from live snapshots | ✅ `parse_jobs_from_snapshot.py` |
| Scores + application + post drafts | ✅ `run_scores_drafts_posts.py` |
| Viewer nurture parser | 🔜 `parse_viewers_from_snapshot.py` |
| Leadership intel + SearXNG | 🔜 `leadership_intel.py` |
| Full orchestrator | 🔜 `run_full_pipeline.py` |
| Cross-site job compare (Indeed etc.) | 📋 Documented; build per locale |
| Cursor Playwright MCP | 📋 Template in `templates/cursor-mcp-playwright.example.json` |

---

## 8. What We Will Not Build

- Auto-apply or auto-message at scale  
- LinkedIn Voyager / private API scraping  
- Credential or cookie storage in Git  
- Engagement pods or fake engagement  
- Scraping DMs or InMail without user navigating there  

See `references/privacy_rules.md`.

---

## 9. Related Docs

- [RESEARCH.md](./RESEARCH.md) — evidence behind workflows  
- [ARCHITECTURE.md](./ARCHITECTURE.md) — system design  
- [DISCOVERY.md](./DISCOVERY.md) — tools and live-session findings  
- [ROADMAP.md](./ROADMAP.md) — build phases  
- [COMPANION_SKILLS.md](./COMPANION_SKILLS.md) — modular skills to extract