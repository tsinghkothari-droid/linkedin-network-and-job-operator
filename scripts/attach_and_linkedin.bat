@echo off
set SESSION=linkedin-ops
if exist "%~dp0..\.env" for /f "usebackq tokens=1,* delims==" %%a in ("%~dp0..\.env") do set %%a=%%b
echo Attaching...
call playwright-cli -s=%SESSION% attach --extension=chrome
if errorlevel 1 exit /b 1
timeout /t 2 /nobreak >nul
echo Goto LinkedIn...
call playwright-cli -s=%SESSION% goto https://www.linkedin.com/feed/
timeout /t 5 /nobreak >nul
echo Snapshot...
call playwright-cli -s=%SESSION% snapshot --filename=linkedin-job-workspace/snapshots/feed.yml
echo Done.