@echo off
set SESSION=linkedin-ops
call playwright-cli -s=%SESSION% attach --extension=chrome
timeout /t 1 /nobreak >nul
call playwright-cli -s=%SESSION% goto "https://www.linkedin.com/jobs/search/?keywords=senior%%20product%%20manager&f_TPR=r604800&location=India"
timeout /t 5 /nobreak >nul
call playwright-cli -s=%SESSION% snapshot --filename=linkedin-job-workspace/snapshots/jobs-search.yml
call playwright-cli -s=%SESSION% screenshot --filename=linkedin-job-workspace/screenshots/jobs-search.png