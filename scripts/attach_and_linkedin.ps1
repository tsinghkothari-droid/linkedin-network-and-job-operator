$Session = "linkedin-ops"
$ErrorActionPreference = "Continue"

Write-Host "Attaching to Chrome extension..."
playwright-cli -s=$Session attach --extension=chrome
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

Start-Sleep -Seconds 2

Write-Host "Navigating to LinkedIn feed..."
playwright-cli -s=$Session goto "https://www.linkedin.com/feed/"
Start-Sleep -Seconds 4

Write-Host "Taking snapshot..."
playwright-cli -s=$Session snapshot --filename=linkedin-job-workspace/snapshots/feed.yml

Write-Host "Done."