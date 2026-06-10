# Personas & Entry Points

Quick routing for **people at large**. Full detail in [USE_CASES.md](./USE_CASES.md).

## By goal

| I want to… | Start here | Workflows |
|------------|------------|-----------|
| Apply for jobs with referrals | `find jobs on linkedin` | 2 → 4 → 3 |
| Write and plan LinkedIn posts | `what should I post` | 9, 10 |
| Spot industry trends early | `sector opportunities` | 5, 6, 10 + research |
| Find consulting / BD opportunities | `business opportunities` | 6, 7, 4 |
| Meet new people in my industry | `senior people to connect` | 8, 10, 1 |
| Switch careers | `skills gap` | 5, 6, 1 |
| Run this for a client | Set `subject_profile.json` | 1, 5–9 |
| Grow a company page | `explore linkedin pages` | 10, 9 |

## By role

| Role | Highest-value features |
|------|------------------------|
| Job seeker | Job pipeline, referral-first, application drafts |
| Consultant | Business opp finder, viewer nurture, content loop |
| Founder | Leadership intel, hiring signals, senior targets |
| Creator | Analytics loop, newsletters, carousel drafts |
| Recruiter / coach | Subject mode, network index, senior rankings |
| Sales / BD | Company map, notifications triage, warm intros |
| Student | Skills roadmap, PYMK ranking, entry-level job scan |

## First-time setup

1. Clone skill → install `playwright-cli`  
2. `scripts/attach_with_token.bat` (or bootstrap Chrome) → log in manually  
3. Optional: LinkedIn data export → `parse_linkedin_export.py`  
4. Pick a journey from [USE_CASES.md §5](./USE_CASES.md#5-typical-journeys-end-to-end)