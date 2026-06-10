# LinkedIn Job Workflow Reference

End-to-end procedure for job discovery, referral outreach, and application preparation.

## Phase Map

```
[Network Export] → Workflow 1 → network_index.*
                                      ↓
[Search Criteria] → Workflow 2 → job_pipeline.csv
                                      ↓
                              Workflow 4 → referral_targets.csv
                                      ↓
                              Workflow 3 → application_drafts/*
                                      ↓
                              USER REVIEW → manual Submit
```

---

## Workflow 2: Job Discovery (Detailed)

### 1. Gather criteria

Ask user for (or infer from profile):

| Field | Example |
|-------|---------|
| `target_role` | Senior Product Manager |
| `location` | Remote US, NYC |
| `industry` | Fintech, B2B SaaS |
| `salary_min` | $180k |
| `seniority` | Senior, Staff |
| `visa_constraints` | H1B sponsorship required |
| `work_mode` | Remote, hybrid |
| `exclude_companies` | Current employer |

### 2. Search execution

**Option A — Playwright MCP (logged-in LinkedIn Jobs)**

1. User provides search URL or asks agent to build one:
   `https://www.linkedin.com/jobs/search/?keywords=senior%20product%20manager&location=United%20States`
2. Navigate with Playwright; snapshot visible job cards.
3. For each card extract:
   - `job_id`, `title`, `company`, `location`, `url`
   - `posted_date` (relative text OK: "2 days ago")
   - `application_type`: `easy_apply` | `external` | `unknown`
4. Open detail page for top N jobs; extract full requirements from visible description.
5. On CAPTCHA or auth wall → stop, notify user.

**Option B — Public career pages**

1. User or agent compiles company career URLs.
2. Fetch/read visible listings only.
3. Same extraction fields as Option A.

**Option C — Manual paste**

User pastes job URLs or descriptions; agent parses and scores.

### 3. Scoring formula

```python
total_score = (
    0.35 * fit_score +
    0.25 * relevance_score +
    0.25 * network_score +
    0.15 * effort_score
)
```

**fit_score** — keyword overlap between job requirements and resume:

- Required skills present: +15 each (cap 60)
- Preferred skills present: +5 each (cap 20)
- Years of experience match: +20
- Penalty for hard missing requirements: -20 each

**relevance_score**:

- Location match: +30
- Industry match: +30
- Seniority match: +25
- Salary range overlap (if known): +15

**network_score**:

- 0 connections: 0
- 1 weak (no recent interaction): 40
- 1 strong (recruiter/hiring manager): 70
- 2+ connections: 90
- Referral already received: 100

**effort_score**:

- Easy Apply, <5 questions: 90
- Standard form + cover letter: 60
- Custom assessments, multiple essays: 30
- External ATS with account creation: 20

### 4. Pipeline status values

| Status | Meaning |
|--------|---------|
| `discovered` | Scored, not yet actioned |
| `referral_pending` | Referral outreach drafted |
| `referral_sent` | User sent referral message |
| `draft_ready` | Application draft complete |
| `applied` | User confirmed submission |
| `rejected` | User or employer declined |
| `withdrawn` | User chose not to pursue |

---

## Workflow 3: Application Assistant (Detailed)

### Resume comparison output format

```markdown
## Fit Analysis: [Company] — [Role]

### Strong matches
- [Requirement] ← [Your experience]

### Partial matches
- [Requirement] ← [Related experience, gap note]

### Gaps (honest)
- [Missing requirement] — suggest: [course, project, or truthful framing]

### Do not claim
- [Skill you lack] — do not fabricate
```

### Cover letter structure

1. Hook — specific to company/product (from public research)
2. Fit — 2–3 bullets mapping experience to requirements
3. Gap acknowledgment — brief, only if needed
4. Close — enthusiasm + availability

### Form prefill policy

| Field | Auto-prefill |
|-------|--------------|
| Name, email, phone | Yes, after user review |
| LinkedIn URL | Yes |
| Work history | Yes, from resume |
| Salary expectation | No — user provides |
| Visa sponsorship | No — user confirms |
| Custom essay questions | Draft only, user edits |
| Submit button | **Never** |

---

## Workflow 4: Referral-first (Detailed)

### Target ranking

```
referral_rank = (
    0.30 * relationship_strength +
    0.25 * role_relevance +
    0.20 * seniority_match +
    0.15 * recency +
    0.10 * response_likelihood
)
```

**relationship_strength**: 1st degree = 100, 2nd = 50, none = 0

**role_relevance**:

- Recruiter / TA: 100
- Hiring manager for role: 95
- Same department peer: 70
- Alumni / friend at company: 60
- Distant connection: 30

### Referral message rules

- Under 300 words
- Mention specific role (with URL)
- One clear ask: "Would you be open to referring me or pointing me to the right person?"
- No mass-copy feel — personalize with one detail about them or company
- Plain text only (no markdown in messages)

### Status tracking

Update `referral_targets.csv` after each user action:

```
not_contacted → contacted → replied → referred → applied
```

If no reply in 7 days, user may choose to apply anyway or follow up once.

---

## Playwright MCP Integration

### Tool usage pattern

1. Read MCP tool schema before calling
2. `browser_navigate` to job URL
3. `browser_snapshot` to get visible content
4. Parse snapshot text — never call undocumented APIs
5. For form fill: snapshot → propose values → wait for user approval → fill one field at a time
6. Final snapshot showing prefilled form — **do not click Submit**

### Error handling

| Condition | Action |
|-----------|--------|
| CAPTCHA visible | Stop, ask user to solve |
| "Sign in" page | Stop, ask user to log in manually |
| Empty results | Widen search criteria with user |
| Page timeout | Retry once, then manual fallback |
| Rate limit message | Stop session, resume later |

---

## Output File Schemas

### job_pipeline.csv

See `templates/job_pipeline_schema.csv`

### company_network_map.csv

```
company,connection_count,recruiter_count,hiring_manager_count,top_targets,best_referral_rank
```

### referral_targets.csv

```
company,job_id,connection_name,connection_title,relationship,rank,status,message_draft_path,last_updated
```

---

## Validation Run (3 Sample Jobs)

Use `validation/sample_jobs.json` and `validation/sample_data/network.json`.

For each job output:

1. Score breakdown table
2. Best referral target with rank
3. Draft referral message (fictional names)
4. Application checklist
5. Explicit note: **No submission performed**