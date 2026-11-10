@echo off
setlocal
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0herramientas\01-flowable.ps1"
if errorlevel 1 (echo Fallo la preparacion de Flowable 7.2. & pause & exit /b 1)
echo Paso 1 terminado.
pause
