$Proyecto = Split-Path -Parent $PSScriptRoot
$Configuracion = Join-Path $Proyecto 'config.local'
if (Test-Path -LiteralPath $Configuracion) {
    foreach ($Linea in (Get-Content -LiteralPath $Configuracion -Encoding UTF8)) {
        if ($Linea -match '^\s*([A-Z][A-Z0-9_]*)\s*=(.*)$') {
            $Nombre = $Matches[1]
            $Valor = $Matches[2].Trim()
            if ($Nombre -match '^(FLOWABLE_|PELUDITOS_|GOOGLE_FORMS_)') {
                [Environment]::SetEnvironmentVariable($Nombre, $Valor, 'Process')
            }
        }
    }
}
