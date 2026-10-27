@echo off
setlocal
where javac >nul 2>nul
if errorlevel 1 (
  echo No se encontro javac. Instala Java 21 y agregalo a PATH.
  pause
  exit /b 1
)
where java >nul 2>nul
if errorlevel 1 (
  echo No se encontro java. Instala Java 21 y agregalo a PATH.
  pause
  exit /b 1
)
cd /d "%~dp0servicio-java"
javac PeluditosService.java
if errorlevel 1 (
  echo No se pudo compilar PeluditosService.java.
  pause
  exit /b 1
)
echo Iniciando servicio Java en http://127.0.0.1:8091/health
java PeluditosService
echo El servicio Java se ha cerrado.
pause