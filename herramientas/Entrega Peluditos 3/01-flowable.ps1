. (Join-Path $PSScriptRoot 'comun.ps1')
$War = Join-Path $Runtime 'flowable-rest.war'
if (Test-Path -LiteralPath $War) {
    if ((Get-Item -LiteralPath $War).Length -eq 91273507) {
        Write-Host "Flowable 7.2 ya está preparado: $War"
        exit 0
    }
    Write-Host 'El WAR existente está incompleto; se reconstruirá.'
}
$Zip = Join-Path $Descargas 'flowable-7.2.0.zip'
if ((-not (Test-Path -LiteralPath $Zip)) -or
    (Get-FileHash -LiteralPath $Zip -Algorithm SHA256).Hash -ne '7A9659E25D06E8FCF4C6A5EF7EA5EA9CEE78F136ED1C919DD2BEF1E3EF536491') {
    Descargar 'https://github.com/flowable/flowable-engine/releases/download/flowable-7.2.0/flowable-7.2.0.zip' $Zip
}
if ((Get-FileHash -LiteralPath $Zip -Algorithm SHA256).Hash -ne '7A9659E25D06E8FCF4C6A5EF7EA5EA9CEE78F136ED1C919DD2BEF1E3EF536491') {
    throw 'El ZIP descargado no coincide con Flowable 7.2.0 verificado.'
}
Add-Type -AssemblyName System.IO.Compression.FileSystem
$Archive = [IO.Compression.ZipFile]::OpenRead($Zip)
try {
    $Entry = $Archive.GetEntry('wars/flowable-rest.war')
    if (-not $Entry -or $Entry.Length -ne 91273507) { throw 'No se encontró flowable-rest.war en el ZIP.' }
    $InputStream = $Entry.Open()
    $OutputStream = [IO.File]::Create($War)
    try { $InputStream.CopyTo($OutputStream) }
    finally { $InputStream.Dispose(); $OutputStream.Dispose() }
} finally { $Archive.Dispose() }
Write-Host "Flowable REST 7.2 preparado: $War"
