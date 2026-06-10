@echo off
setlocal
cd /d "%~dp0.."
if exist .env (
  for /f "usebackq eol=# tokens=1,* delims==" %%a in (".env") do (
    if not "%%a"=="" set "%%a=%%b"
  )
)
call scripts\attach_and_linkedin.bat