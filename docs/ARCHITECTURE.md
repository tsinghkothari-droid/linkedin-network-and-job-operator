# Architecture: End-to-End LinkedIn Operator

## System Overview

```
┌──────────────────────────────────────────────────────────────────┐
│                        AGENT (Cursor/Codex/Grok)                 │
│  SKILL.md orchestrates workflows; human approval gates           │
└────────────┬───────────────────────────────┬─────────────────────┘
             │                               │
             ▼                               ▼
┌────────────────────────┐    ┌──────────────────────────────────┐
│   PLAYWRIGHT CLI        │    │   PYTHON INTELLIGENCE PIPELINE   │
│   (Chrome, headed)      │    │   parse → score → generate       │
│   scripts/bootstrap_*   │    │   scripts/*.py                   │
└────────────┬───────────┘    └──────────────┬───────────────────┘
             │                               │
             ▼                               ▼
┌────────────────────────┐    ┌──────────────────────────────────┐
│   BROWSER SESSION       │    │   LOCAL WORKSPACE (gitignored)   │
│   .playwright-profiles/ │    │   linkedin-job-workspace/        │
│   linkedin-ops session  │    │   subject_profile.json           │
└────────────────────────┘    └──────────────────────────────────┘
             │                               │
             └───────────────┬───────────────┘
                             ▼
              ┌──────────────────────────────────┐
              │   PUBLIC WEB RESEARCH            │
              │   SearXNG / web search for       │
              │   leadership, sector news        │
              └──────────────────────────────────┘
```

## Control Plane: Playwright CLI

### Why CLI-first

- Token-efficient for coding agents (per Microsoft docs)
- Persistent named sessions survive across agent turns
- Headed Chrome lets user login, solve CAPTCHA, review actions
- Snapshots written to `.playwright-cli/` as YAML with element refs

### Session contract

| Setting | Value |
|---------|-------|
| Session name | `linkedin-ops` |
| Browser | `chrome` |
| Mode | `--headed` |
| Persistence | `--persistent` with gitignored profile dir |
| Entry URL | `https://www.linkedin.com/feed/` |

### Bootstrap script

`scripts/bootstrap_chrome.ps1` (Windows) / `scripts/bootstrap_chrome.sh` (Unix):

1. Verify `playwright-cli` installed
2. Create `.playwright-profiles/linkedin-ops/` (gitignored)
3. Open LinkedIn feed in headed Chrome
4. Print instructions for manual login
5. Wait for user confirmation before agent proceeds

### Agent browser commands (approved actions)

```bash
# Read visible content
playwright-cli -s=linkedin-ops snapshot --filename=workspace/snapshots/jobs.yml
playwright-cli -s=linkedin-ops goto "https://www.linkedin.com/jobs/search/?keywords=..."

# Human-reviewed form fill (never Submit)
playwright-cli -s=linkedin-ops fill e42 "Draft answer text"
playwright-cli -s=linkedin-ops screenshot --filename=workspace/screenshots/prefill-review.png

# Session management
playwright-cli -s=linkedin-ops show    # visual dashboard
playwright-cli -s=linkedin-ops close   # end session
```

### Forbidden CLI operations

- `state-save` to repo paths
- `cookie-set` / credential injection
- Automated login flows
- Clicking Submit/Apply/Send without user approval

## Data Plane: Profiles

### Two-profile model

```json
// subject_profile.json — person being analyzed
{
  "name": "Alex Chen",
  "mode": "subject",
  "current_title": "Product Manager",
  "target_roles": ["Senior Product Manager", "Director of Product"],
  "target_industries": ["fintech", "saas"],
  "skills": ["product management", "payments", "SQL"],
  "location": "Remote US",
  "seniority": "Senior",
  "career_goal": "Move into fintech leadership",
  "content_pillars": ["product strategy", "payments", "career growth"]
}

// operator_profile.json — optional, you running the agent
{
  "name": "Jordan Operator",
  "mode": "operator",
  "relationship_to_subject": "coach"
}
```

Intake script: `scripts/intake_profile.py --subject path/to/profile.json`

## Intelligence Modules

### Module map

| Module | Script | Input | Output |
|--------|--------|-------|--------|
| Network parse | `parse_linkedin_export.py` | Export ZIP | `network.json` |
| Network index | `build_network_index.py` | `network.json` | CSV + HTML |
| Skills intel | `skills_intelligence.py` | subject + target roles | `skills_roadmap.md` |
| Sector scanner | `sector_opportunity.py` | network + macro data | `sector_opportunities.csv` |
| Business opps | `business_opportunity.py` | network + sector | `business_opportunities.md` |
| Leadership intel | `leadership_intel.py` | company list | `leadership_map.csv` |
| Senior targets | `senior_recommendations.py` | network + goals | `senior_targets.csv` |
| Content strategy | `content_recommendations.py` | network + subject | `post_recommendations.md` |
| Job pipeline | `validate_skill.py` (existing) | jobs + profile | `job_pipeline.csv` |
| Dashboard | `build_dashboard.py` | workspace CSVs | HTML dashboard |

### Skills intelligence algorithm

```
1. Load subject skills + target role skill requirements
2. Load macro demand weights (Skills on the Rise baseline)
3. Compute gap set = required - possessed
4. Score each gap skill by priority formula
5. Group into: immediate (0-3mo), medium (3-6mo), stretch (6-12mo)
6. Map to suggested new agent skills user should build (meta-recommendation)
```

### Sector opportunity algorithm

```
1. Aggregate network by industry tag
2. Load macro sector growth weights (public research JSON)
3. For each sector: compute network_access × growth × skills_fit
4. Rank top 5 sectors with actionable "why now" rationale
```

### Content recommendation algorithm

```
1. Cluster network into audience segments (industry × seniority)
2. Cross product with subject content_pillars
3. For each segment: generate 2 post ideas with format + hook
4. Apply 2026 algorithm constraints (no external links, depth-first)
5. Output weekly calendar + 3 ready-to-edit drafts
```

## Output Workspace

```
linkedin-job-workspace/
├── subject_profile.json
├── network.json
├── network_index.csv / .html
├── company_network_map.csv
├── skills_roadmap.md / .json
├── sector_opportunities.csv
├── business_opportunities.md
├── leadership_map.csv
├── senior_targets.csv
├── post_recommendations.md
├── job_pipeline.csv
├── referral_targets.csv
├── outreach_messages.md
├── application_drafts/
├── application_status_dashboard.html
├── snapshots/                    # browser YAML snapshots
└── screenshots/                  # review screenshots
```

## Human Review Gates

| Gate | Trigger | Action |
|------|---------|--------|
| G0 | Session start | User confirms logged in |
| G1 | Profile intake | User confirms correct subject |
| G2 | Outreach send | User approves each message |
| G3 | Form prefill | User reviews screenshot |
| G4 | Submit/Apply | User clicks manually |
| G5 | Post publish | User approves draft before posting |
| G6 | CAPTCHA/rate limit | Stop automation entirely |

## Integration with Web Research

For leadership and sector intel, agent should:

1. Run `searxng-scrapling-research` or web search skill when available
2. Query: `"[Company] CEO leadership team 2026"`
3. Store `source_url` + `confidence` on every leadership row
4. Cross-reference with `company_network_map.csv`

## Security Boundaries

```
ALLOWED:                          FORBIDDEN:
- LinkedIn export CSV/ZIP         - Voyager API / hidden POST
- Public company websites         - Cookie export to Git
- Visible browser DOM             - CAPTCHA solvers
- Public news / SEC filings       - Mass connection requests
- Synthetic validation data       - Engagement pod automation
```