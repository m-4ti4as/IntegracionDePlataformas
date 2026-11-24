. (Join-Path $PSScriptRoot 'configuracion.ps1')
$ErrorActionPreference = 'Stop'
$archivo = Join-Path $Proyecto 'config.local'
if (-not (Test-Path -LiteralPath $archivo)) {
    Copy-Item -LiteralPath (Join-Path $Proyecto 'config.example') -Destination $archivo
}
$contenido = Get-Content -LiteralPath $archivo -Raw -Encoding UTF8
$lineaClave = '(?m)^GOOGLE_FORMS_SYNC_KEY\s*=.*$'
$claveActual = [regex]::Match($contenido, $lineaClave)
if (-not $claveActual.Success -or -not (($claveActual.Value -split '=', 2)[1].Trim())) {
    $bytes = New-Object byte[] 32
    $generador = [System.Security.Cryptography.RandomNumberGenerator]::Create()
    try { $generador.GetBytes($bytes) } finally { $generador.Dispose() }
    $clave = [BitConverter]::ToString($bytes).Replace('-', '').ToLowerInvariant()
    if ($claveActual.Success) {
        $contenido = $contenido -replace $lineaClave, "GOOGLE_FORMS_SYNC_KEY=$clave"
    } else {
        $contenido += "`r`nGOOGLE_FORMS_SYNC_KEY=$clave`r`n"
    }
    Set-Content -LiteralPath $archivo -Value $contenido -Encoding UTF8 -NoNewline
}
Write-Host 'Completa los enlaces en config.local. Sigue los pasos en google-forms\README.md.'
Start-Process -FilePath notepad.exe -ArgumentList ('"{0}"' -f $archivo)
