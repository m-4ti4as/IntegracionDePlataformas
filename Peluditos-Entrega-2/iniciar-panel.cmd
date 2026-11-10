@echo off
setlocal
set "SSLKEYLOGFILE="
set "PYTHON=%~dp0.runtime\venv\Scripts\python.exe"
if not exist "%PYTHON%" (
  echo Primero ejecuta 05-instalar-bibliotecas-python.cmd.
  pause
  exit /b 1
)
"%PYTHON%" "%~dp0panel-peluditos\server.py"
pause
