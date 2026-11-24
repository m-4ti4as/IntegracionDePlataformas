@echo off
setlocal
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0herramientas\detener-postgresql.ps1"
if errorlevel 1 (
  pause
  exit /b 1
)
pause
