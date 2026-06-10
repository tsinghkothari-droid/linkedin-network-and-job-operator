# Onboarding: Playwright + Trusted Browser + LinkedIn

**For any user.** Agent walks through this before synthesis.

## What you need

- Node.js 18+
- Google Chrome (or Chromium) — a profile **you trust**
- 10 minutes for first-time setup

## Step 1 — Install Playwright CLI

```bash
npm install -g @playwright/cli@latest
playwright-cli --version
```

## Step 2 — Install browser extension

1. Install the [Playwright MCP Chrome extension](https://github.com/microsoft/playwright/tree/main/packages/extension)
2. Open extension → copy **extension token**
3. In skill folder, copy `env.example` → `.env` (never commit `.env`):

```
PLAYWRIGHT_MCP_EXTENSION_TOKEN=your_token_here
```

## Step 3 — Attach to your Chrome

**Windows:**

```bat
scripts\attach_with_token.bat
```

**macOS/Linux:** set token in env, then:

```bash
playwright-cli -s=linkedin-ops attach --extension=chrome
```

## Step 4 — Log in manually

- Use **your** normal Chrome window
- Log in to LinkedIn yourself (password, 2FA — agent never sees these)
- Tell the agent: **"LinkedIn session ready"**

## Step 5 — Verify

```bash
playwright-cli -s=linkedin-ops goto "https://www.linkedin.com/feed/"
playwright-cli -s=linkedin-ops snapshot
playwright-cli -s=linkedin-ops detach
```

Agent confirms your name/headline appear in the snapshot.

## Troubleshooting

| Issue | Fix |
|-------|-----|
| Attach fails | Chrome must be open; extension enabled |
| Wrong account | Log out in Chrome; log in as correct user |
| Session drops | Chain commands in one batch script; always `detach` |
| Profile locked | Close other Chrome instances using same profile |

## Privacy

- Token stays in `.env` (gitignored)
- No cookies or passwords stored in the repo
- See `references/privacy_rules.md`