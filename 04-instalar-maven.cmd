@echo off
setlocal
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0herramientas\04-maven.ps1"
if errorlevel 1 (echo Fallo la preparacion de Maven. & pause & exit /b 1)
echo Paso 4 terminado.
pause
