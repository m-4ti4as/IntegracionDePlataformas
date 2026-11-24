$PostgresVersion = '17.12'
$JdbcVersion = '42.7.14'
$PostgresDir = Join-Path $Runtime 'postgresql'
$PostgresBin = Join-Path $PostgresDir 'pgsql\bin'
$PostgresData = Join-Path $PostgresDir 'data'
$PostgresLog = Join-Path $PostgresDir 'postgresql.log'
$PostgresConfig = Join-Path $PostgresDir 'conexion.json'
$PostgresControl = Join-Path $PostgresBin 'pg_ctl.exe'
$JdbcArchivo = Join-Path $Descargas "postgresql-$JdbcVersion.jar"
$NombreBase = 'peluditos_flowable'
$UsuarioMotor = 'flowable_peluditos'

function Calcular-Sha256([string]$Ruta) {
    $Flujo = [IO.File]::OpenRead($Ruta)
    $Sha = [Security.Cryptography.SHA256]::Create()
    try { return [BitConverter]::ToString($Sha.ComputeHash($Flujo)).Replace('-', '') }
    finally { $Sha.Dispose(); $Flujo.Dispose() }
}

function Obtener-ArchivoVerificado([string]$Url, [string]$Destino, [string]$Hash) {
    if ((Test-Path -LiteralPath $Destino) -and (Calcular-Sha256 $Destino) -eq $Hash) { return }
    $Parcial = "$Destino.part"
    Descargar $Url $Parcial
    if ((Calcular-Sha256 $Parcial) -ne $Hash) {
        throw "La descarga no coincide con la versión fijada: $Url"
    }
    Move-Item -LiteralPath $Parcial -Destination $Destino -Force
}

function Preparar-JdbcPostgres {
    Obtener-ArchivoVerificado "https://jdbc.postgresql.org/download/postgresql-$JdbcVersion.jar" $JdbcArchivo `
        '73914527305A40CCE504B0D3D90B23CAF565136912D607AE8AE7C5895512332C'
}

function Preparar-BinariosPostgres {
    $Listo = Join-Path $PostgresDir 'binarios-version.txt'
    if ((Test-Path -LiteralPath $PostgresControl) -and (Test-Path -LiteralPath $Listo) -and
        (Get-Content -LiteralPath $Listo -Raw).Trim() -eq $PostgresVersion) { return }
    $Archivo = "postgresql-$PostgresVersion-2-windows-x64-binaries.zip"
    $Zip = Join-Path $Descargas $Archivo
    Obtener-ArchivoVerificado "https://get.enterprisedb.com/postgresql/$Archivo" $Zip `
        '520C8C6F19ABB3B31FA83EC5E486E2F769EEDD7593D94E60A7CDA8A5BFB4DF91'
    Add-Type -AssemblyName System.IO.Compression.FileSystem
    $Raiz = [IO.Path]::GetFullPath($PostgresDir) + [IO.Path]::DirectorySeparatorChar
    $Paquete = [IO.Compression.ZipFile]::OpenRead($Zip)
    try {
        foreach ($Entrada in $Paquete.Entries) {
            if ($Entrada.Name -and $Entrada.FullName -match '^pgsql/(bin|lib|share)/') {
                $Destino = [IO.Path]::GetFullPath((Join-Path $PostgresDir $Entrada.FullName))
                if (-not $Destino.StartsWith($Raiz, [StringComparison]::OrdinalIgnoreCase)) {
                    throw 'Ruta inválida en el ZIP de PostgreSQL.'
                }
                New-Item -ItemType Directory -Path ([IO.Path]::GetDirectoryName($Destino)) -Force | Out-Null
                [IO.Compression.ZipFileExtensions]::ExtractToFile($Entrada, $Destino, $true)
            }
        }
    } finally { $Paquete.Dispose() }
    if (-not (Test-Path -LiteralPath $PostgresControl)) { throw 'El ZIP no contiene pg_ctl.exe.' }
    Set-Content -LiteralPath $Listo -Value $PostgresVersion -Encoding ASCII
}

function Nueva-ClavePostgres {
    $Bytes = New-Object byte[] 32
    $Generador = [Security.Cryptography.RandomNumberGenerator]::Create()
    try { $Generador.GetBytes($Bytes) } finally { $Generador.Dispose() }
    return [BitConverter]::ToString($Bytes).Replace('-', '').ToLowerInvariant()
}

function Leer-ConexionPostgres {
    Get-Content -LiteralPath $PostgresConfig -Raw -Encoding UTF8 | ConvertFrom-Json
}

function Iniciar-Postgres {
    if (-not (Test-Path -LiteralPath (Join-Path $PostgresData 'PG_VERSION'))) {
        throw 'Ejecuta primero 08-configurar-postgresql.cmd.'
    }
    & $PostgresControl status -D $PostgresData | Out-Null
    if ($LASTEXITCODE -eq 0) { return }
    & $PostgresControl start -D $PostgresData -l $PostgresLog -w -t 30
    if ($LASTEXITCODE -ne 0) {
        throw "PostgreSQL no arrancó. Revisa si el puerto está ocupado y consulta $PostgresLog."
    }
}

function Detener-Postgres {
    if (Test-Path -LiteralPath (Join-Path $PostgresData 'PG_VERSION')) {
        & $PostgresControl status -D $PostgresData | Out-Null
        if ($LASTEXITCODE -eq 0) {
            & $PostgresControl stop -D $PostgresData -m fast -w -t 30
            if ($LASTEXITCODE -ne 0) { throw 'No fue posible detener PostgreSQL.' }
            return
        }
    }
    Write-Host 'PostgreSQL local ya está detenido.'
}

function Usar-PostgresDelProyecto([string]$Url) {
    if (Test-Path -LiteralPath $PostgresConfig) {
        $Conexion = Leer-ConexionPostgres
        return $Url -eq "jdbc:postgresql://127.0.0.1:$($Conexion.puerto)/$NombreBase"
    }
    return $false
}
