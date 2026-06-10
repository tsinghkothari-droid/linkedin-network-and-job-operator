@echo off
setlocal
cd /d "%~dp0.."
set SESSION=linkedin-ops
if exist .env (
  for /f "usebackq eol=# tokens=1,* delims==" %%a in (".env") do (
    if not "%%a"=="" set "%%a=%%b"
  )
)
if not exist linkedin-job-workspace\screenshots mkdir linkedin-job-workspace\screenshots
if not exist linkedin-job-workspace\snapshots mkdir linkedin-job-workspace\snapshots
call playwright-cli -s=%SESSION% attach --extension=chrome
if errorlevel 1 exit /b 1
timeout /t 1 /nobreak >nul
call playwright-cli -s=%SESSION% goto "https://www.linkedin.com/jobs/search/?keywords=senior%%20product%%20manager&f_TPR=r604800&location=India"
timeout /t 5 /nobreak >nul
call playwright-cli -s=%SESSION% snapshot --filename=linkedin-job-workspace/snapshots/jobs-search.yml
call playwright-cli -s=%SESSION% screenshot --filename=linkedin-job-workspace/screenshots/jobs-search.png
call playwright-cli -s=%SESSION% detach
echo Done.