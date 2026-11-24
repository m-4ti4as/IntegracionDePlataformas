@echo off
setlocal
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0herramientas\iniciar-flowable.ps1"
if errorlevel 1 echo Flowable no pudo iniciar. Revisa el mensaje anterior.
pause
