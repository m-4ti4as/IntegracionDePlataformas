. (Join-Path $PSScriptRoot 'comun.ps1')
$Java = Leer-Ruta 'java-path.txt' '03-instalar-java.cmd'
$Jar = Join-Path $Proyecto 'servicio-java\target\servicio-mensajes-1.0.0.jar'
if (-not (Test-Path -LiteralPath $Jar)) { throw 'Ejecuta primero 07-compilar-servicio-java.cmd.' }
& $Java -jar $Jar
if ($LASTEXITCODE -ne 0) { throw "El servicio Java terminó con código $LASTEXITCODE." }
