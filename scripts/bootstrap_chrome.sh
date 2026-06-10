#!/usr/bin/env bash
# Bootstrap headed Chrome for LinkedIn operations via Playwright CLI.
set -euo pipefail

SESSION="${1:-linkedin-ops}"
PROFILE_DIR="${2:-.playwright-profiles/linkedin-ops}"
START_URL="${3:-https://www.linkedin.com/feed/}"

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

if ! command -v playwright-cli >/dev/null 2>&1; then
  echo "Installing playwright-cli..."
  npm install -g @playwright/cli@latest
fi

mkdir -p "$PROFILE_DIR" linkedin-job-workspace/snapshots linkedin-job-workspace/screenshots

echo ""
echo "=== LinkedIn Browser Bootstrap ==="
echo "Session:  $SESSION"
echo "Browser:  Chrome (headed)"
echo "Profile:  $PROFILE_DIR (gitignored)"
echo "URL:      $START_URL"
echo ""
echo "Opening Chrome. Log in to LinkedIn manually if prompted."
echo "When ready, tell the agent: 'LinkedIn session ready'"
echo ""

playwright-cli -s="$SESSION" open "$START_URL" --browser=chrome --headed --persistent

echo ""
echo "Session started. Useful commands:"
echo "  playwright-cli -s=$SESSION snapshot"
echo "  playwright-cli -s=$SESSION goto <url>"
echo "  playwright-cli -s=$SESSION show"
echo "  playwright-cli -s=$SESSION close"