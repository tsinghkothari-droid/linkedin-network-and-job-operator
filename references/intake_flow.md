# Intake Flow (≤7 Questions)

**Rule:** Collect all intake answers **before** running synthesis. Store in `linkedin-job-workspace/intake_responses.json`.

Schema: `templates/intake_questions.json`

## Agent script

### Opening

> Before I analyze your data, I need 7 quick inputs so recommendations match your goals. Most are multiple choice; two are sliders (1–5 or 1–3).

### Questions (ask in order)

**Q1 — Primary goal (MCQ, pick one)**  
What is your primary goal for the next 6 months?

- Job search — land a new role  
- Consulting & clients — grow revenue  
- Thought leadership — visibility and authority  
- Career pivot — new industry or function  
- Network expansion — strategic relationships  
- Fundraising / investors  
- Hiring / talent — build a team  

**Q2 — Time horizon (slider 1–3)**  
How far ahead should your action plan optimize?  
`1` = 3 months · `2` = 6 months · `3` = 12 months  

**Q3 — Geography (MCQ)**  
Primary geography for opportunities?

- My country only  
- My region  
- Global / remote-first  
- Specific city → *ask for city name*  

**Q4 — Industries (MCQ, up to 3)**  
Which industries matter most?

- Technology · Finance · Healthcare · Government / Public  
- Energy / Power · Consulting · Consumer · Other → *specify*  

**Q5 — Seniority path (MCQ)**  
Target trajectory?

- IC expert · Manager · Director+ · Founder · Board / advisor  

**Q6 — Outreach style (slider 1–5)**  
How aggressive should connection suggestions be?  
`1` = warm intros only · `5` = include thoughtful cold outreach  

**Q7 — Content cadence (MCQ)**  
How often will you post on LinkedIn?

- Rarely · Monthly · Bi-weekly · Weekly · Multiple per week  

### After answers

```bash
python scripts/intake_to_profile.py \
  --intake linkedin-job-workspace/intake_responses.json \
  --out linkedin-job-workspace/subject_profile.json
```

Then proceed to synthesis — **not before**.

## Defaults (if user skips)

| Field | Default |
|-------|---------|
| primary_goal | network_expansion |
| time_horizon | 2 (6 months) |
| geo_focus | country |
| industry_focus | ["tech"] |
| seniority_path | manager |
| outreach_style | 3 |
| content_cadence | monthly |