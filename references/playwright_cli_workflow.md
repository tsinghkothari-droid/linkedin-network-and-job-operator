# Playwright CLI Workflow for LinkedIn

Primary browser control plane. MCP is fallback only.

## Install

```bash
npm install -g @playwright/cli@latest
playwright-cli install --skills   # optional
```

## Phase 0: Bootstrap (every session)

### Windows

```powershell
.\scripts\bootstrap_chrome.ps1
```

### macOS/Linux

```bash
bash scripts/bootstrap_chrome.sh
```

### What happens

1. Headed Chrome opens to `https://www.linkedin.com/feed/`
2. Named session: `linkedin-ops`
3. Profile stored in `.playwright-profiles/linkedin-ops/` (gitignored)
4. **User logs in manually** if needed
5. User tells agent: `LinkedIn session ready`

## Agent commands (after login)

```bash
# Verify session
playwright-cli -s=linkedin-ops snapshot

# Job search
playwright-cli -s=linkedin-ops goto "https://www.linkedin.com/jobs/search/?keywords=senior%20product%20manager"
playwright-cli -s=linkedin-ops snapshot --filename=linkedin-job-workspace/snapshots/jobs.yml

# Company page (leadership visible content)
playwright-cli -s=linkedin-ops goto "https://www.linkedin.com/company/example/about/"
playwright-cli -s=linkedin-ops snapshot --filename=linkedin-job-workspace/snapshots/company-about.yml

# Screenshot for human review before form fill
playwright-cli -s=linkedin-ops screenshot --filename=linkedin-job-workspace/screenshots/review.png

# Monitor all sessions visually
playwright-cli show

# End session
playwright-cli -s=linkedin-ops close
```

## Human review gates

| Before | Require |
|--------|---------|
| First navigation after open | User confirms logged in |
| Form fill | User approves field values |
| Message send | User approves draft text |
| Submit/Apply | User clicks manually — agent NEVER clicks |
| CAPTCHA appears | Stop all automation |

## Stop conditions

Stop immediately and notify user if snapshot contains:

- "Let's verify you're human"
- "Sign in to LinkedIn"
- "unusual activity"
- Rate limit warnings

## Privacy

- **Never** `state-save` to repo paths
- **Never** commit `.playwright-profiles/`
- **Never** automate credential entry
- Snapshots in `linkedin-job-workspace/snapshots/` are gitignored

## CLI vs MCP decision

| Use CLI when | Use MCP when |
|--------------|--------------|
| Step-by-step job search | MCP already configured and CLI missing |
| Token budget matters | Long exploratory browser loop requested |
| User wants headed Chrome | Extension attach mode needed |

Default: **CLI first**.