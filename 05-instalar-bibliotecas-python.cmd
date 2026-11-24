@echo off
setlocal
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0herramientas\05-python-bibliotecas.ps1"
if errorlevel 1 (echo Fallo la instalacion de bibliotecas Python. & pause & exit /b 1)
echo Paso 5 terminado.
pause
