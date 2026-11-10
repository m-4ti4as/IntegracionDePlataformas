. (Join-Path $PSScriptRoot 'comun.ps1')
$Python = $null
$Candidatos = @()
if ($env:PELUDITOS_PYTHON) { $Candidatos += $env:PELUDITOS_PYTHON }
$Candidatos += Join-Path $Runtime 'Python312\python.exe'
$Candidatos += @(Get-Command python.exe -All -ErrorAction SilentlyContinue | ForEach-Object Source)
foreach ($Candidato in $Candidatos) {
    if (-not (Test-Path -LiteralPath $Candidato)) { continue }
    try {
        & $Candidato -c 'import sys; sys.exit(0 if sys.version_info >= (3, 12) else 1)' 2>$null
        if ($LASTEXITCODE -eq 0) { $Python = $Candidato; break }
    } catch { continue }
}
if (-not $Python -and (Get-Command py.exe -ErrorAction SilentlyContinue)) {
    try {
        $Candidato = (& py.exe -3 -c 'import sys; print(sys.executable)' 2>$null | Select-Object -First 1)
        if ($Candidato -and (Test-Path -LiteralPath $Candidato)) {
            & $Candidato -c 'import sys; sys.exit(0 if sys.version_info >= (3, 12) else 1)' 2>$null
            if ($LASTEXITCODE -eq 0) { $Python = $Candidato }
        }
    } catch { $Python = $null }
}
if (-not $Python) {
    $Destino = Join-Path $Runtime 'Python312'
    $Python = Join-Path $Destino 'python.exe'
    $Instalador = Join-Path $Descargas 'python-3.12.10-amd64.exe'
    Descargar 'https://www.python.org/ftp/python/3.12.10/python-3.12.10-amd64.exe' $Instalador
    $Proceso = Start-Process -FilePath $Instalador -ArgumentList "/quiet InstallAllUsers=0 PrependPath=0 Include_test=0 TargetDir=`"$Destino`"" -Wait -PassThru -WindowStyle Hidden
    if ($Proceso.ExitCode -ne 0 -or -not (Test-Path -LiteralPath $Python)) {
        throw "No se pudo instalar Python: $($Proceso.ExitCode)"
    }
}
Set-Content -LiteralPath (Join-Path $Runtime 'python-path.txt') -Value $Python -Encoding utf8
Write-Host "Python preparado: $Python"
