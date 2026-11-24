param([ValidateRange(1024,65535)][int]$Puerto = 5432)

. (Join-Path $PSScriptRoot 'comun.ps1')
. (Join-Path $PSScriptRoot 'postgresql.ps1')

Preparar-JdbcPostgres
Preparar-BinariosPostgres

if (Test-Path -LiteralPath $PostgresConfig) {
    $Conexion = Leer-ConexionPostgres
    if ($PSBoundParameters.ContainsKey('Puerto') -and $Puerto -ne $Conexion.puerto) {
        throw "La instalación actual usa el puerto $($Conexion.puerto)."
    }
} else {
    if (Test-Path -LiteralPath (Join-Path $PostgresData 'PG_VERSION')) {
        throw 'La base local ya existe. Recupera su archivo de conexión antes de continuar.'
    }
    $PuertoLocal = [Net.Sockets.TcpClient]::new()
    try {
        try {
            $PuertoLocal.Connect('127.0.0.1', $Puerto)
        } catch [Net.Sockets.SocketException] {
            if ($_.Exception.SocketErrorCode -ne [Net.Sockets.SocketError]::ConnectionRefused) { throw }
        }
        if ($PuertoLocal.Connected) {
            throw "El puerto $Puerto ya está ocupado. Ejecuta 08-configurar-postgresql.cmd con -Puerto seguido de un puerto libre."
        }
    } finally { $PuertoLocal.Dispose() }
    $Conexion = [pscustomobject]@{
        puerto = $Puerto
        administrador = Nueva-ClavePostgres
        motor = Nueva-ClavePostgres
    }
    $Conexion | ConvertTo-Json | Set-Content -LiteralPath $PostgresConfig -Encoding UTF8
}
$Url = "jdbc:postgresql://127.0.0.1:$($Conexion.puerto)/$NombreBase"
$Plantilla = $env:FLOWABLE_DB_URL -eq "jdbc:postgresql://127.0.0.1:5432/$NombreBase" -and -not $env:FLOWABLE_DB_PASSWORD
if ($env:FLOWABLE_DB_URL -like 'jdbc:postgresql:*' -and $env:FLOWABLE_DB_URL -ne $Url -and -not $Plantilla) {
    throw 'config.local apunta a otro servidor PostgreSQL. Revisa esa conexión antes de cambiarla.'
}

$Psql = Join-Path $PostgresBin 'psql.exe'
if (-not (Test-Path -LiteralPath (Join-Path $PostgresData 'PG_VERSION'))) {
    $ClaveTemporal = Join-Path $PostgresDir ('initdb-' + [Guid]::NewGuid().ToString('N') + '.txt')
    try {
        Set-Content -LiteralPath $ClaveTemporal -Value $Conexion.administrador -Encoding ASCII
        & (Join-Path $PostgresBin 'initdb.exe') -D $PostgresData -U peluditos_admin --auth=scram-sha-256 `
            --encoding=UTF8 --locale=C "--pwfile=$ClaveTemporal"
        if ($LASTEXITCODE -ne 0) { throw 'PostgreSQL no pudo inicializar la carpeta de datos.' }
    } finally {
        if (Test-Path -LiteralPath $ClaveTemporal) { Remove-Item -LiteralPath $ClaveTemporal }
    }
}
$Conf = Join-Path $PostgresData 'postgresql.conf'
if (-not (Select-String -LiteralPath $Conf -Pattern '^# Peluditos Postgres local$' -Quiet)) {
    Add-Content -LiteralPath $Conf -Encoding ASCII -Value @(
        '', '# Peluditos Postgres local', "listen_addresses = '127.0.0.1'", "port = $($Conexion.puerto)"
    )
}
Iniciar-Postgres

$ClaveAnterior = $env:PGPASSWORD
try {
    $env:PGPASSWORD = $Conexion.administrador
    @"
SELECT format('CREATE ROLE %I LOGIN PASSWORD %L', '$UsuarioMotor', '$($Conexion.motor)')
WHERE NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = '$UsuarioMotor') \gexec
SELECT format('CREATE DATABASE %I OWNER %I', '$NombreBase', '$UsuarioMotor')
WHERE NOT EXISTS (SELECT 1 FROM pg_database WHERE datname = '$NombreBase') \gexec
"@ | & $Psql -X -w -h 127.0.0.1 -p $Conexion.puerto -U peluditos_admin -d postgres -v ON_ERROR_STOP=1
    if ($LASTEXITCODE -ne 0) { throw 'No se pudo preparar la base exclusiva de Flowable.' }
    $env:PGPASSWORD = $Conexion.motor
    & $Psql -X -w -h 127.0.0.1 -p $Conexion.puerto -U $UsuarioMotor -d $NombreBase -c 'SELECT current_database();'
    if ($LASTEXITCODE -ne 0) { throw 'La cuenta de Flowable no pudo conectarse a PostgreSQL.' }
} finally { $env:PGPASSWORD = $ClaveAnterior }

if (-not (Test-Path -LiteralPath $Configuracion)) {
    Copy-Item -LiteralPath (Join-Path $Proyecto 'config.example') -Destination $Configuracion
} elseif ($env:FLOWABLE_DB_URL -ne $Url) {
    $Backup = Join-Path $Runtime 'config.antes-postgresql'
    if (-not (Test-Path -LiteralPath $Backup)) {
        Copy-Item -LiteralPath $Configuracion -Destination $Backup
    }
}
$Lineas = @(Get-Content -LiteralPath $Configuracion -Encoding UTF8 | Where-Object {
    $_ -notmatch '^\s*FLOWABLE_DB_(URL|USER|PASSWORD)\s*='
})
$Lineas += "FLOWABLE_DB_URL=$Url", "FLOWABLE_DB_USER=$UsuarioMotor", "FLOWABLE_DB_PASSWORD=$($Conexion.motor)"
Set-Content -LiteralPath $Configuracion -Value $Lineas -Encoding UTF8
Write-Host 'PostgreSQL preparado para Flowable. Ahora inicia el motor y despliega los BPMN.'
