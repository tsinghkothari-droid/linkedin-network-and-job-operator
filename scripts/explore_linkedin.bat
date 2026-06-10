@echo off
setlocal EnableDelayedExpansion
cd /d "%~dp0.."
set SESSION=linkedin-ops
set OUT=linkedin-job-workspace\exploration
if exist .env (
  for /f "usebackq eol=# tokens=1,* delims==" %%a in (".env") do (
    if not "%%a"=="" set "%%a=%%b"
  )
)
if not exist "%OUT%\snapshots" mkdir "%OUT%\snapshots"
if not exist "%OUT%\screenshots" mkdir "%OUT%\screenshots"

echo === LinkedIn Exploration ===
call playwright-cli -s=%SESSION% attach --extension=chrome
if errorlevel 1 exit /b 1

call :visit feed https://www.linkedin.com/feed/
call :visit network https://www.linkedin.com/mynetwork/
call :visit profile-views https://www.linkedin.com/analytics/profile-views/
call :visit creator-analytics https://www.linkedin.com/analytics/creator/content/
call :visit jobs-govtech "https://www.linkedin.com/jobs/search/?keywords=govtech+power+sector&f_TPR=r604800&location=India"
call :visit jobs-ai-strategy "https://www.linkedin.com/jobs/search/?keywords=AI+strategy+consultant&f_TPR=r604800&location=India"
call :visit company-leeladhar https://www.linkedin.com/company/31121788/about/
call :visit audience-analytics https://www.linkedin.com/analytics/creator/audience/
call :visit newsletters https://www.linkedin.com/mynetwork/network-manager/newsletters/
call :visit notifications https://www.linkedin.com/notifications/

call playwright-cli -s=%SESSION% detach
echo Exploration complete. Output: %OUT%
exit /b 0

:visit
set "NAME=%~1"
set "URL=%~2"
echo --- !NAME! ---
call playwright-cli -s=%SESSION% goto "!URL!"
if /i "!NAME!"=="profile-views" (
  timeout /t 10 /nobreak >nul
) else if /i "!NAME!"=="jobs-govtech" (
  timeout /t 8 /nobreak >nul
) else if /i "!NAME!"=="jobs-ai-strategy" (
  timeout /t 8 /nobreak >nul
) else (
  timeout /t 5 /nobreak >nul
)
call playwright-cli -s=%SESSION% snapshot --filename=%OUT%/snapshots/!NAME!.yml
call playwright-cli -s=%SESSION% screenshot --filename=%OUT%/screenshots/!NAME!.png
goto :eof