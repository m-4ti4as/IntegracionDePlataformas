. (Join-Path $PSScriptRoot 'comun.ps1')
$Maven = Preparar-Maven
$Repositorio = Join-Path $Runtime 'm2'
$Pom = Join-Path $Proyecto 'servicio-java\pom.xml'
& $Maven -q "-Dmaven.repo.local=$Repositorio" -f $Pom dependency:go-offline
if ($LASTEXITCODE -ne 0) { throw 'No se pudieron descargar las bibliotecas Java.' }
Write-Host "Jersey, Grizzly y otras bibliotecas Java preparados en: $Repositorio"
