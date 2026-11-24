. (Join-Path $PSScriptRoot 'comun.ps1')
$Maven = Join-Path $Runtime 'apache-maven-3.9.11\bin\mvn.cmd'
if (-not (Test-Path -LiteralPath $Maven)) {
    $Zip = Join-Path $Descargas 'maven-3.9.11.zip'
    Descargar 'https://repo.maven.apache.org/maven2/org/apache/maven/apache-maven/3.9.11/apache-maven-3.9.11-bin.zip' $Zip
    Expand-Archive -LiteralPath $Zip -DestinationPath $Runtime -Force
}
if (-not (Test-Path -LiteralPath $Maven)) { throw 'No se pudo preparar Maven 3.9.11.' }
Write-Host "Maven preparado: $Maven"
