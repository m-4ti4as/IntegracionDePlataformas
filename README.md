# Peluditos Pet Chile · Entrega 3

El panel de la dueña registra interesados, mantiene su historial de compras y muestra las tareas de Flowable. El registro público se realiza en Google Forms. En el panel se puede registrar manualmente a quien necesite ayuda.

En la bandeja, la API reúne las fichas guardadas en SQLite y las tareas que entrega Flowable. Por ejemplo, cuando hay que generar un cupón, el worker pide la tarea a Flowable, recibe sus datos, obtiene el código de Java y comunica el resultado. Flowable guarda el avance del proceso en PostgreSQL. [Diagrama y función de cada componente](Arquitectura/README.md)

## Instalación en Windows

**Para la dueña.** Usa el ZIP privado que te entrega el equipo. Haz clic derecho y elige **Extraer todo**. Después de la instalación y con los servicios iniciados, abre el [panel de Peluditos](http://127.0.0.1:8092/) y entra a **Formulario**. Puedes copiar el enlace para tus interesados. El panel trae las respuestas al abrirse y cada 30 segundos mientras está abierto. La conexión ya viene preparada.

Ejecuta los CMD del 01 al 08, en ese orden, y espera a que termine cada uno. Preparan Flowable OSS 7.2.0, Python 3.12 o superior, Java 21, Maven 3.9.11 y las dependencias del worker Python y de Jakarta REST con Jersey. El paso 07 compila Java. El paso 08 instala PostgreSQL 17.12 en la carpeta del proyecto, crea la base de Flowable y prepara el controlador JDBC.

1. El formulario ya está publicado. La copia privada está lista para el paso siguiente. Si instalaste desde GitHub, el equipo puede copiar el archivo privado `config.local.forms` junto a `iniciar-panel.cmd` y reiniciar el panel. [Configuración del formulario](google-forms/README.md)
2. Abre `iniciar-flowable-rest.cmd`. Arranca el PostgreSQL local del proyecto cuando corresponde y luego inicia Flowable.
3. Ejecuta `desplegar-demo-flowable.cmd`. Repite este paso si cambia algún BPMN ejecutable.
4. Abre `iniciar-servicio-java.cmd`, `iniciar-panel.cmd` e `iniciar-worker.cmd`, en ese orden. Mantén abiertas las cuatro ventanas de los servicios.
5. Abre el [panel local](http://127.0.0.1:8092/). Al abrirlo, el panel consulta las respuestas nuevas de Google Forms si la conexión está configurada.

El paso 08 prepara `config.local`. El ejemplo usa PostgreSQL en 5432, Flowable en 8080, Java en 8091 y el panel en 8092. La [guía de despliegue](docs/despliegue.md) indica qué ajustar para otro entorno y cómo detener la base local.

## Demostración

1. Registra una respuesta en Google Forms y abre el panel. Con el worker activo, aparecerá un interesado con su mascota y una tarea de seguimiento. También puedes usar **Registrar interesado**.
2. En **Hoy**, marca **Compró** e indica producto y monto. En **Contactos** se registra la primera venta y la ficha pasa a **Cliente**.
3. Para el cumpleaños de esa mascota, pulsa **Preparar correo** y luego **Iniciar tareas de envío**. La dueña revisa el mensaje en **Hoy**, aprueba el envío simulado y puede marcar **No compró** en el seguimiento. La oportunidad queda cerrada sin compra. La persona conserva su estado de **Cliente** y su venta anterior.
4. Reinicia el panel y consulta otra vez la ficha, la venta y la oportunidad. En SQLite están en `clientes`, `ventas` y `oportunidades`. PostgreSQL guarda las instancias, tareas e historial de Flowable. Puedes dejar una tarea pendiente, reiniciar el motor y retomarla en la bandeja.

## Componentes

- [BPMN](BPMN/) contiene los modelos editables y sus PNG.
- [Arquitectura](Arquitectura/README.md) contiene el diagrama y su fuente editable.
- [panel-peluditos](panel-peluditos/) contiene la interfaz, la API y el esquema SQLite.
- [worker-python](worker-python/) consume las tareas externas de Flowable y llama a los servicios.
- [servicio-java](servicio-java/) contiene los servicios Jakarta REST.
- [google-forms](google-forms/) contiene el script que crea el formulario y entrega las respuestas de forma autenticada.
- [Actas](Actas/) y [Videos](Videos/) reúnen los registros, los guiones y los enlaces del equipo.


Para ejecutar la prueba integrada con la configuración del proyecto, usa PowerShell con los cuatro servicios activos.

    powershell -NoProfile -ExecutionPolicy Bypass -File .\herramientas\iniciar-python.ps1 "pruebas\smoke.py"

[Diseño de persistencia](docs/persistencia.md) · [Pruebas de Entrega 3](evidencias/pruebas-entrega-3.md) · [Servicios](docs/servicios.md)
