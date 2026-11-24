param([Parameter(Mandatory)][string]$Archivo, [switch]$Desplegar)

. (Join-Path $PSScriptRoot 'comun.ps1')
$Python = Join-Path $Runtime 'venv\Scripts\python.exe'
if (-not (Test-Path -LiteralPath $Python)) { throw 'Ejecuta primero 05-instalar-bibliotecas-python.cmd.' }
$env:PYTHONUTF8 = '1'
$Argumentos = @()
if ($Desplegar) { $Argumentos += '--desplegar' }
& $Python (Join-Path $Proyecto $Archivo) @Argumentos
if ($LASTEXITCODE -ne 0) { throw "Python terminó con código $LASTEXITCODE." }
