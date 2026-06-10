# Companion Skills to Build

These skills extend the LinkedIn operator into a modular career intelligence suite.
Build as **modules inside** `linkedin-network-and-job-operator` first; extract when stable.

**Audience use cases:** [USE_CASES.md](./USE_CASES.md)

---

## 1. `playwright-cli-browser-ops`

**Purpose:** Reusable Chrome bootstrap and session management for any agent workflow.

**Triggers:** `launch chrome for automation`, `playwright session`, `browser ops`

**Capabilities:**
- Install/verify `@playwright/cli`
- Named persistent sessions (`linkedin-ops`, `research-ops`)
- Headed Chrome launch with gitignored profiles
- Snapshot → parse helpers
- Human-review gate templates
- Session dashboard (`playwright-cli show`)

**Why separate:** Every browser-touching skill needs the same bootstrap, privacy rules, and session naming.

---

## 2. `linkedin-skills-intelligence`

**Purpose:** Generate personalized skills roadmaps for any subject profile (not the operator).

**Triggers:** `what skills should I learn`, `skills gap analysis`, `career transition skills`

**Inputs:**
- `subject_profile.json`
- Target role(s)
- Optional: LinkedIn export skills data
- Macro: Skills on the Rise 2026 weights

**Outputs:**
- `skills_roadmap.md` — ranked skills with time horizons
- `skills_roadmap.json` — machine-readable
- `profile_skill_additions.md` — what to add to LinkedIn profile first

**Algorithm:** O*NET-style gap analysis + demand weighting + transition bridge skills.

**Meta-output:** Recommends **new agent skills** the person should create based on their career direction (e.g. "build a `fintech-pm-interview-prep` skill").

---

## 3. `linkedin-sector-scanner`

**Purpose:** Identify sectoral opportunities where the subject has network advantage.

**Triggers:** `sector opportunities`, `which industries should I target`, `sector analysis`

**Inputs:**
- Network index (industry distribution)
- Subject profile goals
- Public labor market data

**Outputs:**
- `sector_opportunities.csv` — ranked sectors
- `sector_brief.md` — narrative per top sector

**Scoring:** market growth × network access × skills fit × geography.

---

## 4. `linkedin-business-opportunity-finder`

**Purpose:** Detect business opportunities visible through the network (not just jobs).

**Triggers:** `business opportunities in my network`, `consulting opportunities`, `intro arbitrage`

**Opportunity types:**
| Type | Detection signal |
|------|------------------|
| Warm intro arbitrage | Senior connections in hiring sectors |
| Advisory gap | Expertise mismatch in network |
| Co-founder match | Founders lacking subject's skills |
| Talent placement | Recruiter concentration |
| Content monetization | Underserved audience topic |
| Sector bridge | Adjacent industry overlap |

**Outputs:** `business_opportunities.md` with actionable next steps.

---

## 5. `linkedin-leadership-intel`

**Purpose:** Find who runs organizations using public sources only.

**Triggers:** `who runs [company]`, `leadership map`, `executives at`

**Sources (in order):**
1. Company website /about
2. SEC filings (public companies)
3. Press releases
4. Browser-visible LinkedIn company page
5. Crunchbase / Wikipedia
6. Web search corroboration

**Outputs:**
- `leadership_map.csv`
- `org_cluster_leadership.csv` (batch mode)

**Fields:** company, role, person_name, source_url, confidence, in_network

**Hard rule:** Every row must have `source_url`. No guessed names.

---

## 6. `linkedin-senior-target-finder`

**Purpose:** Recommend senior people to connect with, nurture, or request intros to.

**Triggers:** `senior people to connect`, `who should I reach out to`, `referral targets`

**Tiers:**
- T1: C-suite, Founder, GP
- T2: VP, Director, Head of
- T3: Principal, Staff, Senior Manager
- T4: Recruiter, TA Leader

**Outputs:**
- `senior_targets.csv` — ranked with rationale
- `connect_drafts.md` — connection request templates
- `nurture_plan.md` — existing connections to re-engage

---

## 7. `linkedin-content-strategist`

**Purpose:** Recommend posts that will interest the subject's specific network.

**Triggers:** `what should I post`, `linkedin content strategy`, `post ideas for my network`

**Inputs:**
- Network composition (industry/seniority clusters)
- Subject content pillars
- Skills on the Rise timely angles
- 2026 algorithm constraints

**Outputs:**
- `post_recommendations.md` — 9+ ideas with format, hook, audience cluster
- `content_calendar.csv` — 3-week schedule
- `post_drafts/` — 3 ready-to-edit drafts

**Algorithm constraints:**
- No external links in post body
- Favor carousels (6–9 slides) and long-form text
- Depth Score optimization (dwell time, comment depth)
- No engagement bait patterns

---

## 8. `linkedin-job-application-assistant` (existing, extract later)

Already partially implemented as Workflows 2–4. Extract when job pipeline stabilizes.

---

## 9. `linkedin-profile-viewer-intel`

**Purpose:** Parse profile viewer analytics → nurture and hiring-intent targets.

**Triggers:** `who viewed my profile`, `nurture profile viewers`

**Use case:** [USE_CASES §E](./USE_CASES.md#e-network-growth--whos-new-in-the-industry)

---

## 10. `linkedin-creator-analytics-reader`

**Purpose:** Impressions, engagement, audience demographics → content calendar feedback.

**Triggers:** `how are my posts doing`, `content performance`

**Use case:** [USE_CASES §B](./USE_CASES.md#b-content-creation--posting)

---

## 11. `multi-page-linkedin-operator`

**Purpose:** Content calendars across personal + company pages user admins.

**Triggers:** `manage my linkedin pages`, `company page content`

**Use case:** [USE_CASES §G](./USE_CASES.md#g-company--brand-operations-multi-page)

---

## 12. `cross-site-job-scanner`

**Purpose:** Compare visible job listings on Indeed, Glassdoor, Naukri, company sites (no private APIs).

**Triggers:** `search jobs on indeed`, `compare job boards`

**Use case:** [USE_CASES §3](./USE_CASES.md#3-cross-platform--other-sites)

**Depends on:** `playwright-cli-browser-ops`

---

## 13. `govtech-sector-scanner` (example vertical)

**Purpose:** Template for vertical scanners — power, govtech, healthtech, etc.

**Triggers:** `govtech opportunities`, `power sector jobs india`

**Use case:** [USE_CASES §C/D](./USE_CASES.md#c-trend--signal-identification)

---

## Build Order (recommended)

```
1. playwright-cli-browser-ops     ← shared foundation
2. linkedin-skills-intelligence   ← high user value
3. linkedin-content-strategist    ← differentiator
4. linkedin-leadership-intel      ← needs web research
5. linkedin-senior-target-finder    ← builds on network index
6. linkedin-sector-scanner          ← macro + network
7. linkedin-business-opportunity-finder ← combines 5+6
8. linkedin-job-application-assistant ← already started
9. linkedin-profile-viewer-intel       ← exploration validated
10. linkedin-creator-analytics-reader  ← exploration validated
11. cross-site-job-scanner             ← USE_CASES cross-platform
```

## Meta-Skill Recommendation Engine

When analyzing a subject with a **different work profile**, also recommend **new agent skills they should create**:

| Subject profile pattern | Suggested skill to build |
|------------------------|--------------------------|
| Career pivot (engineering → PM) | `pm-transition-interview-prep` |
| Freelance consultant | `client-proposal-generator` |
| Founder hiring | `startup-hiring-pipeline` |
| Sales → CS leader | `customer-success-playbook` |
| India → US job search | `us-visa-job-filter` |
| Content creator | `linkedin-carousel-builder` |

Output in `recommended_agent_skills.md` with trigger phrases and scope for each.