. (Join-Path $PSScriptRoot 'comun.ps1')
$Java = Leer-Ruta 'java-path.txt' '03-instalar-java.cmd'
$War = Join-Path $Runtime 'flowable-rest.war'
if (-not (Test-Path -LiteralPath $War)) { throw 'Ejecuta primero 01-instalar-flowable.cmd.' }
New-Item -ItemType Directory -Path (Join-Path $Runtime 'data') -Force | Out-Null
Push-Location $Proyecto
try {
    & $Java -jar $War --server.port=8080 '--spring.datasource.url=jdbc:h2:file:./.runtime/data/flowable;DB_CLOSE_ON_EXIT=FALSE' --spring.datasource.username=sa '--spring.datasource.password='
    if ($LASTEXITCODE -ne 0) { throw "Flowable terminó con código $LASTEXITCODE." }
} finally { Pop-Location }
