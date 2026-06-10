# Bootstrap headed Chrome for LinkedIn operations via Playwright CLI.
# Does NOT automate login. User must sign in manually.

param(
    [string]$Session = "linkedin-ops",
    [string]$ProfileDir = ".playwright-profiles\linkedin-ops",
    [string]$StartUrl = "https://www.linkedin.com/feed/"
)

$ErrorActionPreference = "Stop"

function Test-PlaywrightCli {
    $cli = Get-Command playwright-cli -ErrorAction SilentlyContinue
    if (-not $cli) {
        Write-Host "playwright-cli not found. Installing..."
        npm install -g @playwright/cli@latest
    }
    playwright-cli --help | Out-Null
}

Test-PlaywrightCli

$root = Split-Path -Parent $PSScriptRoot
Set-Location $root

New-Item -ItemType Directory -Force -Path $ProfileDir | Out-Null
New-Item -ItemType Directory -Force -Path "linkedin-job-workspace\snapshots" | Out-Null
New-Item -ItemType Directory -Force -Path "linkedin-job-workspace\screenshots" | Out-Null

Write-Host ""
Write-Host "=== LinkedIn Browser Bootstrap ===" -ForegroundColor Cyan
Write-Host "Session:  $Session"
Write-Host "Browser:  Chrome (headed)"
Write-Host "Profile:  $ProfileDir (gitignored)"
Write-Host "URL:      $StartUrl"
Write-Host ""
Write-Host "Opening Chrome. Log in to LinkedIn manually if prompted."
Write-Host "When ready, tell the agent: 'LinkedIn session ready'"
Write-Host ""

playwright-cli -s=$Session open $StartUrl --browser=chrome --headed --persistent

Write-Host ""
Write-Host "Session started. Useful commands:" -ForegroundColor Green
Write-Host "  playwright-cli -s=$Session snapshot"
Write-Host "  playwright-cli -s=$Session goto <url>"
Write-Host "  playwright-cli -s=$Session show"
Write-Host "  playwright-cli -s=$Session close"