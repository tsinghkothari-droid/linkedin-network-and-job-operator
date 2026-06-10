# LinkedIn Data Export Guide (Any User)

Unlocks full network analysis. **You** download; agent parses locally.

## Request export

1. Go to [LinkedIn Settings](https://www.linkedin.com/mypreferences/d/download-my-data)
2. **Get a copy of your data** → **Want something in particular?**
3. Select at minimum:
   - **Connections**
   - **Profile**
   - **Positions** (recommended)
   - **Skills** (optional)
4. Request archive → LinkedIn emails when ready (minutes to days)

## Download

1. Open email from LinkedIn → download ZIP
2. Save to a local folder (e.g. `~/Downloads/Basic_LinkedInDataExport.zip`)
3. Tell agent the full path — **do not** commit ZIP to Git

## Parse (agent runs)

```bash
python scripts/parse_linkedin_export.py \
  --input /path/to/Basic_LinkedInDataExport.zip \
  --out linkedin-job-workspace/network.json

python scripts/build_network_index.py \
  --network linkedin-job-workspace/network.json \
  --out-dir linkedin-job-workspace
```

## Without export

Skill still works in **live-only mode** (jobs, analytics, viewers) but:

- No full connection graph
- Referral scores limited
- Connection suggestions less accurate

Dashboard shows **Export pending** until ZIP is parsed.

## Privacy

- Export contains PII — keep in `linkedin-job-workspace/` (gitignored)
- Never upload to GitHub or share in chat logs