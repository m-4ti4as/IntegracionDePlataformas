@echo off
setlocal
set "BASE=%~dp0"
where curl.exe >nul 2>nul
if errorlevel 1 (
  echo curl.exe no esta disponible.
  pause
  exit /b 1
)
curl.exe -sS -f --max-time 20 -u rest-admin:test -F "file=@%BASE%despliegue-proceso-681.bar" "http://127.0.0.1:8080/flowable-rest/service/repository/deployments"
if errorlevel 1 goto fail
echo.
curl.exe -sS -f --max-time 20 -u rest-admin:test -F "file=@%BASE%formularios\aprobarMensaje.form" "http://127.0.0.1:8080/flowable-rest/form-api/form-repository/deployments"
if errorlevel 1 goto fail
echo.
curl.exe -sS -f --max-time 20 -u rest-admin:test -F "file=@%BASE%formularios\resultadoOportunidad.form" "http://127.0.0.1:8080/flowable-rest/form-api/form-repository/deployments"
if errorlevel 1 goto fail
echo.
echo Despliegue terminado.
pause
exit /b 0
:fail
echo El despliegue fallo. Comprueba que Flowable REST siga abierto en 8080.
pause
exit /b 1