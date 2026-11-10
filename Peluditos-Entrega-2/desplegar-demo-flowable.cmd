@echo off
setlocal
set "BASE=%~dp0"
set "PYTHON=%BASE%.runtime\venv\Scripts\python.exe"
if not exist "%PYTHON%" (
  echo Primero ejecuta 05-instalar-bibliotecas-python.cmd.
  pause
  exit /b 1
)
"%PYTHON%" "%BASE%herramientas\preparar-bpmn.py"
if errorlevel 1 (
  echo No se pudo preparar el despliegue.
  pause
  exit /b 1
)
curl.exe -sS -f --max-time 30 -u rest-admin:test -F "file=@%BASE%.runtime\despliegue-proceso-720.bar" "http://127.0.0.1:8080/flowable-rest/service/repository/deployments"
if errorlevel 1 (
  echo Error de despliegue. Revisa que Flowable REST siga abierto.
  pause
  exit /b 1
)
echo.
echo Procesos desplegados en Flowable 7.2.
pause
