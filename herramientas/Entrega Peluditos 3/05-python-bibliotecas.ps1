. (Join-Path $PSScriptRoot 'comun.ps1')
$env:TMP = Join-Path $Runtime 'tmp'
$env:TEMP = $env:TMP
$env:SSLKEYLOGFILE = ''
New-Item -ItemType Directory -Path $env:TMP -Force | Out-Null
$Python = Leer-Ruta 'python-path.txt' '02-instalar-python.cmd'
$Entorno = Join-Path $Runtime 'venv'
$PythonEntorno = Join-Path $Entorno 'Scripts\python.exe'
if (-not (Test-Path -LiteralPath $PythonEntorno)) {
    & $Python -m venv $Entorno
    if ($LASTEXITCODE -ne 0) { throw 'No se pudo crear el entorno virtual.' }
}
& $PythonEntorno -m ensurepip --upgrade --default-pip
if ($LASTEXITCODE -ne 0) { throw 'No se pudo instalar pip en el entorno virtual.' }
& $PythonEntorno -m pip install --disable-pip-version-check -r (Join-Path $Proyecto 'worker-python\requirements.txt')
if ($LASTEXITCODE -ne 0) { throw 'No se pudieron instalar las bibliotecas Python.' }
Write-Host "Bibliotecas Python preparadas: $PythonEntorno"
