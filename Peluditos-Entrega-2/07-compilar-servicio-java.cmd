@echo off
setlocal
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0herramientas\07-compilar-java.ps1"
if errorlevel 1 (echo Fallo la compilacion del servicio Java. & pause & exit /b 1)
echo Paso 7 terminado.
pause
