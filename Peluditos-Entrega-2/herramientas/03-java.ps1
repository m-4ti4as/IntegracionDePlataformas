. (Join-Path $PSScriptRoot 'comun.ps1')
$Java = $null
if ($env:PELUDITOS_JAVA -and (Test-Path -LiteralPath $env:PELUDITOS_JAVA)) {
    $Java = $env:PELUDITOS_JAVA
} else {
    $Existente = Get-ChildItem -LiteralPath (Join-Path $Runtime 'jdk') -Filter java.exe -Recurse -ErrorAction SilentlyContinue | Select-Object -First 1
    if ($Existente) { $Java = $Existente.FullName }
    elseif (Get-Command java.exe -ErrorAction SilentlyContinue) { $Java = (Get-Command java.exe).Source }
}
if ($Java) {
    try {
        $Version = (& $Java --version 2>$null | Select-Object -First 1) -join ' '
        if ($Version -notmatch '^(openjdk|java) 21[.]') { $Java = $null }
    } catch { $Java = $null }
}
if (-not $Java) {
    $Zip = Join-Path $Descargas 'jdk21.zip'
    Descargar 'https://api.adoptium.net/v3/binary/latest/21/ga/windows/x64/jdk/hotspot/normal/eclipse' $Zip
    $Destino = Join-Path $Runtime 'jdk'
    Expand-Archive -LiteralPath $Zip -DestinationPath $Destino -Force
    $Encontrado = Get-ChildItem -LiteralPath $Destino -Filter java.exe -Recurse | Select-Object -First 1
    if (-not $Encontrado) { throw 'No se encontró Java 21 en el ZIP.' }
    $Java = $Encontrado.FullName
}
Set-Content -LiteralPath (Join-Path $Runtime 'java-path.txt') -Value $Java -Encoding utf8
Write-Host "Java 21 preparado: $Java"
