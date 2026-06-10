# Implementation Roadmap

**Use-case driven plan:** [USE_CASES.md](./USE_CASES.md) · **Personas:** [PERSONAS.md](./PERSONAS.md)

## Phase 0 — Research (DONE)

- [x] Playwright CLI evaluation
- [x] LinkedIn Skills on the Rise 2026 review
- [x] Algorithm 2026 content strategy research
- [x] O*NET skills gap methodology
- [x] Leadership intel source mapping
- [x] Architecture + companion skills spec
- [x] Publish `docs/RESEARCH.md` on GitHub

## Phase 1 — Bootstrap & Foundation (IN PROGRESS)

- [x] Install `@playwright/cli` globally
- [x] `scripts/bootstrap_chrome.ps1` — launch headed Chrome session
- [x] `references/playwright_cli_workflow.md` — agent instructions
- [x] `scripts/intake_profile.py` — subject vs operator profile intake
- [x] `templates/subject_profile_schema.json`
- [x] Expand `.gitignore` for playwright profiles
- [ ] Verify headed Chrome opens LinkedIn on user's machine

## Phase 2 — Deep Intelligence Modules

- [x] `scripts/skills_intelligence.py` — skills gap + roadmap
- [x] `scripts/sector_opportunity.py` — sector scoring
- [x] `scripts/business_opportunity.py` — business opp detection
- [x] `scripts/senior_recommendations.py` — senior people ranking
- [x] `scripts/content_recommendations.py` — post ideas for network
- [ ] `scripts/leadership_intel.py` — company leadership lookup (web search integration)
- [ ] `data/skills_on_the_rise_2026.json` — macro skill weights

## Phase 3 — SKILL.md Integration

- [x] Workflow 5: Skills Intelligence
- [x] Workflow 6: Sector & Business Opportunities
- [x] Workflow 7: Leadership Intelligence
- [x] Workflow 8: Senior People Recommendations
- [x] Workflow 9: Content & Post Strategy
- [x] Phase 0 bootstrap section in SKILL.md
- [ ] End-to-end orchestrator script `scripts/run_pipeline.py`

## Phase 4 — Browser-Connected Workflows (IN PROGRESS)

- [x] `scripts/explore_linkedin.bat` — multi-page exploration
- [x] `scripts/parse_exploration.py` — capability report from snapshots
- [x] Extension attach flow (`attach_with_token.bat`)
- [ ] `parse_jobs_from_snapshot.py` — live jobs → `job_pipeline.csv` (Use case: **Job search**)
- [ ] `parse_viewers_from_snapshot.py` — viewer nurture targets (Use case: **Network growth**)
- [ ] Company page leadership snapshot parser (Use case: **Business opps**)
- [ ] Profile comparison from visible browser content
- [ ] Screenshot review pipeline for form prefill (Use case: **Applications**)
- [ ] Cross-site job compare script — Indeed/Glassdoor visible pages (Use case: **Cross-platform**)

## Phase 5 — Companion Skill Extraction

- [ ] Extract `linkedin-skills-intelligence` as standalone skill
- [ ] Extract `linkedin-content-strategist` as standalone skill
- [ ] Extract `playwright-cli-browser-ops` as shared dependency
- [ ] Register in `.agents/.skill-lock.json` after stable

## Phase 6 — Validation & Hardening

- [x] 3-job validation (original)
- [ ] Full pipeline validation with synthetic subject profile
- [ ] Leadership intel test on 3 public companies
- [ ] Post recommendation quality review
- [ ] Privacy audit (no PII in git)

## Phase 7 — Use-Case Maturity (by audience)

| Use case category | Shipped | Next |
|-------------------|---------|------|
| Job search & applications | Export scoring, validation | Live snapshot parser |
| Content & posting | `content_recommendations.py` | Analytics feedback loop parser |
| Trend identification | Sector + skills modules | Newsletter + notification digest |
| Business opportunities | `business_opportunity.py` | Leadership + tender watch |
| New industry connections | Senior recs, network index | PYMK + viewer parsers |
| Cross-site research | Documented in USE_CASES | Per-locale job site adapters |
| Multi-page brand ops | Exploration capture | `multi_page_operator.py` |

## Success Criteria

| Metric | Target |
|--------|--------|
| Chrome bootstrap | User sees headed LinkedIn in <30s |
| Subject profile mode | Analyze different person than operator |
| Skills roadmap | Top 10 ranked skills with rationale |
| Sector opps | Top 5 sectors with scores |
| Senior targets | Top 10 ranked with intro rationale |
| Post recs | 9+ ideas (3/week × 3 weeks) tied to network |
| Job pipeline | Score + referral + checklist (no submit) |
| Exploration | 10 LinkedIn surfaces captured in one run |
| USE_CASES doc | All major personas covered on GitHub |
| Git safety | Zero real PII committed |