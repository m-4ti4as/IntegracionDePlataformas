@echo off
setlocal
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0herramientas\03-java.ps1"
if errorlevel 1 (echo Fallo la preparacion de Java 21. & pause & exit /b 1)
echo Paso 3 terminado.
pause
