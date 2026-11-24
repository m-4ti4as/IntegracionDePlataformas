@echo off
setlocal
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0herramientas\iniciar-servicio-java.ps1"
if errorlevel 1 echo El servicio Java no pudo iniciar. Revisa el mensaje anterior.
pause
