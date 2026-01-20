@echo off
setlocal

set "ROOT=%~dp0"
set "PY=%ROOT%.venv\Scripts\python.exe"
set "APP=%ROOT%Sonic_Cipher\main_gui.py"

if exist "%PY%" (
  "%PY%" "%APP%"
  if errorlevel 1 goto :error
  goto :eof
)

py -3 "%APP%"
if errorlevel 1 goto :error
goto :eof

:error
echo Failed to start Sonic Cipher. Ensure Python and dependencies are installed.
echo Tip: .\.venv\Scripts\python -m pip install cryptography matplotlib
pause
