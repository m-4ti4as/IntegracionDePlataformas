@echo off
setlocal
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0herramientas\02-python.ps1"
if errorlevel 1 (echo Fallo la preparacion de Python. & pause & exit /b 1)
echo Paso 2 terminado.
pause
