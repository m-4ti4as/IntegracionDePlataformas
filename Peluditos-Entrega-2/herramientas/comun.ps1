$ErrorActionPreference = 'Stop'
$Proyecto = Split-Path -Parent $PSScriptRoot
$Runtime = Join-Path $Proyecto '.runtime'
$Descargas = Join-Path $Runtime 'descargas'
New-Item -ItemType Directory -Path $Descargas -Force | Out-Null

function Descargar([string]$Url, [string]$Destino) {
    if (-not (Get-Command curl.exe -ErrorAction SilentlyContinue)) {
        throw 'Falta curl.exe en Windows.'
    }
    Write-Host "Descargando: $Url"
    & curl.exe -L --fail --show-error --retry 2 --connect-timeout 20 --max-time 1800 --output $Destino $Url
    if ($LASTEXITCODE -ne 0) { throw "Falló la descarga: $Url" }
}

function Leer-Ruta([string]$Nombre, [string]$Paso) {
    $Archivo = Join-Path $Runtime $Nombre
    if (-not (Test-Path -LiteralPath $Archivo)) { throw "Ejecuta primero $Paso." }
    $Ruta = (Get-Content -LiteralPath $Archivo -Raw).Trim()
    if (-not (Test-Path -LiteralPath $Ruta)) { throw "La ruta guardada no existe: $Ruta. Repite $Paso." }
    return $Ruta
}

function Preparar-Maven {
    $Java = Leer-Ruta 'java-path.txt' '03-instalar-java.cmd'
    $Maven = Join-Path $Runtime 'apache-maven-3.9.11\bin\mvn.cmd'
    if (-not (Test-Path -LiteralPath $Maven)) { throw 'Ejecuta primero 04-instalar-maven.cmd.' }
    $env:JAVA_HOME = Split-Path -Parent (Split-Path -Parent $Java)
    $env:MAVEN_OPTS = "$env:MAVEN_OPTS -Djavax.net.ssl.trustStoreType=Windows-ROOT"
    return $Maven
}
