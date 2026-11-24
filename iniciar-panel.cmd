@echo off
setlocal
set "SSLKEYLOGFILE="
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0herramientas\iniciar-python.ps1" "panel-peluditos\server.py"
pause
