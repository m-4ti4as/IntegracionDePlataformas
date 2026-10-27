@echo off
setlocal
set "SSLKEYLOGFILE="
set "SCRIPT=%~dp0formularios\server.py"
if defined PELUDITOS_PYTHON if exist "%PELUDITOS_PYTHON%" goto custom
if exist "C:\Python314\python.exe" goto localpython
py -3 -c "import sys" >nul 2>nul
if not errorlevel 1 goto launcher
python -c "import sys" >nul 2>nul
if not errorlevel 1 goto pathpython
echo No se encontro Python. Instala Python 3 o define PELUDITOS_PYTHON con la ruta de python.exe.
pause
exit /b 1
:custom
"%PELUDITOS_PYTHON%" "%SCRIPT%" 
goto end
:localpython
"C:\Python314\python.exe" "%SCRIPT%" 
goto end
:launcher
py -3 "%SCRIPT%" 
goto end
:pathpython
python "%SCRIPT%" 
:end
pause

