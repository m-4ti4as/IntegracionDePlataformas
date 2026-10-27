param(
    [Parameter(Mandatory = $true)]
    [ValidateSet('rest', 'ui')]
    [string]$Componente
)

$ErrorActionPreference = 'Stop'
$carpetaProyecto = Split-Path -Parent $PSScriptRoot
$carpetaFlowable = Join-Path $carpetaProyecto 'flowable-6.8.1'
$archivos = @{
    'flowable-rest.war' = 58722080
    'flowable-ui.war' = 103592310
}
$nombreNecesario = if ($Componente -eq 'rest') { 'flowable-rest.war' } else { 'flowable-ui.war' }
$archivoNecesario = Join-Path $carpetaFlowable $nombreNecesario

if ((Test-Path -LiteralPath $archivoNecesario -PathType Leaf) -and
    (Get-Item -LiteralPath $archivoNecesario).Length -eq $archivos[$nombreNecesario]) {
    Write-Host "Flowable 6.8.1 ya esta disponible: $nombreNecesario"
    exit 0
}

if (-not (Get-Command curl.exe -ErrorAction SilentlyContinue)) {
    Write-Error 'No se encontro curl.exe para descargar Flowable.'
    exit 1
}

$url = 'https://github.com/flowable/flowable-engine/releases/download/flowable-6.8.1/flowable-6.8.1.zip'
$hashEsperado = '2298109A688860666E24B33361D08A1627BF3CEA54DE112A9C345633AABBECAC'
$zipTemporal = Join-Path ([IO.Path]::GetTempPath()) ("flowable-6.8.1-$PID.zip")
$archivosTemporales = @()

try {
    Write-Host 'Descargando Flowable OSS 6.8.1 desde el lanzamiento oficial de GitHub...'
    & curl.exe -L --fail --silent --show-error --retry 2 --connect-timeout 15 --max-time 1800 --output $zipTemporal $url
    if ($LASTEXITCODE -ne 0) { throw "La descarga fallo (curl: $LASTEXITCODE)." }
    if ((Get-FileHash -LiteralPath $zipTemporal -Algorithm SHA256).Hash -ne $hashEsperado) {
        throw 'El ZIP descargado no coincide con la version verificada de Flowable 6.8.1.'
    }

    New-Item -ItemType Directory -Path $carpetaFlowable -Force | Out-Null
    Add-Type -AssemblyName System.IO.Compression.FileSystem
    $zip = [IO.Compression.ZipFile]::OpenRead($zipTemporal)
    try {
        foreach ($nombre in $archivos.Keys) {
            $entrada = $zip.GetEntry("flowable-6.8.1/wars/$nombre")
            if ($null -eq $entrada -or $entrada.Length -ne $archivos[$nombre]) {
                throw "El ZIP no contiene el archivo esperado: $nombre"
            }
            $destino = Join-Path $carpetaFlowable $nombre
            $temporal = "$destino.descarga"
            $archivosTemporales += $temporal
            $origen = $entrada.Open()
            $salida = [IO.File]::Create($temporal)
            try { $origen.CopyTo($salida) }
            finally { $salida.Dispose(); $origen.Dispose() }
            Move-Item -LiteralPath $temporal -Destination $destino -Force
            Write-Host "Preparado: $nombre"
        }
    }
    finally { $zip.Dispose() }
}
catch {
    Write-Error $_
    exit 1
}
finally {
    foreach ($temporal in $archivosTemporales) {
        if (Test-Path -LiteralPath $temporal) { Remove-Item -LiteralPath $temporal -Force }
    }
    if (Test-Path -LiteralPath $zipTemporal) { Remove-Item -LiteralPath $zipTemporal -Force }
}

