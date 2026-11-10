. (Join-Path $PSScriptRoot 'comun.ps1')
$Maven = Preparar-Maven
$Repositorio = Join-Path $Runtime 'm2'
if (-not (Test-Path -LiteralPath (Join-Path $Repositorio 'org\glassfish\jersey'))) {
    throw 'Ejecuta primero 06-instalar-bibliotecas-java.cmd.'
}
$Pom = Join-Path $Proyecto 'servicio-java\pom.xml'
& $Maven -q "-Dmaven.repo.local=$Repositorio" -f $Pom -DskipTests package
if ($LASTEXITCODE -ne 0) { throw 'No se pudo compilar el servicio Java.' }
$Jar = Join-Path $Proyecto 'servicio-java\target\servicio-mensajes-1.0.0.jar'
if (-not (Test-Path -LiteralPath $Jar)) { throw 'La compilación terminó sin generar el JAR.' }
Write-Host "Servicio Java compilado: $Jar"
