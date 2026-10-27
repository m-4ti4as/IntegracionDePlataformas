@echo off
setlocal
set "BASE=%~dp0"
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%BASE%herramientas\preparar-flowable.ps1" -Componente ui
if errorlevel 1 (
  echo No se pudo preparar Flowable Modeler. Revisa la conexion a internet y vuelve a intentarlo.
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
echo Iniciando Flowable Modeler en http://127.0.0.1:8083/flowable-ui/
echo Usuario: admin  Clave: test
java -jar "%BASE%flowable-6.8.1\flowable-ui.war" --server.port=8083 "--spring.datasource.url=jdbc:h2:mem:peluditosModeler;DB_CLOSE_DELAY=-1" --spring.datasource.username=sa "--spring.datasource.password="
echo Flowable Modeler se ha cerrado.
pause
