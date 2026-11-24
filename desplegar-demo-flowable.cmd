@echo off
setlocal
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0herramientas\iniciar-python.ps1" "herramientas\preparar-bpmn.py" -Desplegar
pause
