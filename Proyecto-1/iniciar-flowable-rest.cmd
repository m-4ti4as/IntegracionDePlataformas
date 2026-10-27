@echo off
setlocal
set "BASE=%~dp0"
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%BASE%herramientas\preparar-flowable.ps1" -Componente rest
if errorlevel 1 (
  echo No se pudo preparar Flowable REST. Revisa la conexion a internet y vuelve a intentarlo.
  pause
  exit /b 1
)
where java >nul 2>nul
if errorlevel 1 (
  echo Java 21 no esta disponible en PATH.
  pause
  exit /b 1
)
cd /d "%BASE%"
echo Iniciando Flowable REST en http://127.0.0.1:8080/flowable-rest/docs
echo Deja esta ventana abierta. Despues ejecuta desplegar-demo-flowable.cmd.
java -jar "%BASE%flowable-6.8.1\flowable-rest.war" --server.port=8080 "--spring.datasource.url=jdbc:h2:mem:peluditosDemo;DB_CLOSE_DELAY=-1" --spring.datasource.username=sa "--spring.datasource.password="
echo Flowable REST se ha cerrado.
pause
