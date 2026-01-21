@echo off
setlocal

set "ROOT=%~dp0.."
for %%I in ("%ROOT%") do set "ROOT=%%~fI"
set "PY=%ROOT%\.venv\Scripts\python.exe"
set "APP=%ROOT%\app.py"

if exist "%PY%" (
  "%PY%" "%APP%"
  if errorlevel 1 goto :error
  goto :eof
)

py -3 "%APP%"
if errorlevel 1 goto :error
goto :eof

:error
echo Failed to start Sonic Cipher Web. Ensure Python and dependencies are installed.
echo Tip: .\.venv\Scripts\python -m pip install -r requirements.txt
pause
