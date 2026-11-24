. (Join-Path $PSScriptRoot 'comun.ps1')
. (Join-Path $PSScriptRoot 'postgresql.ps1')
$Java = Leer-Ruta 'java-path.txt' '03-instalar-java.cmd'
$War = Join-Path $Runtime 'flowable-rest.war'
if (-not (Test-Path -LiteralPath $War)) { throw 'Ejecuta primero 01-instalar-flowable.cmd.' }
New-Item -ItemType Directory -Path (Join-Path $Runtime 'data') -Force | Out-Null
Push-Location $Proyecto
try {
    $env:SERVER_ADDRESS = if ($env:FLOWABLE_HOST) { $env:FLOWABLE_HOST } else { '127.0.0.1' }
    $env:SERVER_PORT = if ($env:FLOWABLE_PORT) { $env:FLOWABLE_PORT } else { '8080' }
    $env:SPRING_DATASOURCE_URL = if ($env:FLOWABLE_DB_URL) { $env:FLOWABLE_DB_URL } else { 'jdbc:h2:file:./.runtime/data/flowable;DB_CLOSE_ON_EXIT=FALSE' }
    $env:SPRING_DATASOURCE_USERNAME = if ($env:FLOWABLE_DB_USER) { $env:FLOWABLE_DB_USER } else { 'sa' }
    [Environment]::SetEnvironmentVariable('SPRING_DATASOURCE_PASSWORD', [string]$env:FLOWABLE_DB_PASSWORD, 'Process')
    if ($env:FLOWABLE_USER) { $env:FLOWABLE_REST_APP_ADMIN_USERID = $env:FLOWABLE_USER }
    if ($env:FLOWABLE_PASSWORD) { $env:FLOWABLE_REST_APP_ADMIN_PASSWORD = $env:FLOWABLE_PASSWORD }
    if ($env:SPRING_DATASOURCE_URL -like 'jdbc:postgresql:*') {
        Preparar-JdbcPostgres
        if (Usar-PostgresDelProyecto $env:SPRING_DATASOURCE_URL) { Iniciar-Postgres }
        $env:SPRING_DATASOURCE_DRIVER_CLASS_NAME = 'org.postgresql.Driver'
        $Classpath = "WEB-INF/classes,WEB-INF/lib,WEB-INF/lib-provided,$JdbcArchivo"
        & $Java "-Dloader.path=$Classpath" -cp $War org.springframework.boot.loader.launch.PropertiesLauncher
    } else {
        & $Java -jar $War
    }
    if ($LASTEXITCODE -ne 0) { throw "Flowable terminó con código $LASTEXITCODE." }
} finally { Pop-Location }
