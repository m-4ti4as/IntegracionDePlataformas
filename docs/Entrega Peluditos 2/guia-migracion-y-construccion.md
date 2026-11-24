# Cómo se construyó la Entrega 2 y cómo repetirla manualmente

Esta guía describe el trabajo realizado para Peluditos Pet Chile desde la primera prueba con Flowable 6.8.1 hasta la carpeta actual con Flowable OSS 7.2.0. Está escrita para que cualquier integrante del equipo pueda explicar el proyecto, ubicar cada archivo y reconstruirlo sin depender de una herramienta de generación de código.

## 1. Qué problema resuelve el prototipo

Peluditos vende tortas para mascotas. El dato importante para una futura venta es el cumpleaños de la mascota. Antes, una consulta llegaba por redes sociales, la dueña contestaba por chat y, si había compra, coordinaba pago y despacho. No existía un registro ordenado de interesados ni una forma de recordar fechas.

Se diseñaron dos procesos propuestos:

1. **Gestión de Leads:** registrar a la persona y su mascota desde un formulario, generar un cupón diario del 10 %, dejar el contacto pendiente y permitir que la dueña registre si hubo compra.
2. **Oportunidades por cumpleaños y eventos:** preparar una propuesta de correo para una fecha, dejar que la dueña la revise, simular el envío y registrar el resultado comercial.

El panel es una **bandeja de tareas**: las decisiones humanas pendientes llegan desde Flowable. Las fichas de clientes y el calendario ayudan a trabajar, pero no sustituyen al proceso BPMN.

## 2. Punto de partida y motivo de la migración

La primera entrega estaba en la carpeta antigua peluditos-para-subir. Usaba Flowable 6.8.1, un servicio Java hecho directamente con HttpServer, un worker Python que llamaba manualmente a la API REST y formularios .form de esa versión. El BPMN de oportunidades era la prueba ejecutable; Gestión de Leads aún era principalmente un modelo propuesto.

El profesor pidió Flowable 7.2 y observó cuatro asuntos: participantes claros en AS-IS, nombres de tareas expresados como acciones, regla de 15 días fuera del nombre de la tarea, y una implementación técnica con external worker oficial y servicio Java Jakarta REST dentro de Maven.

**Migrar aquí significó reconstruir el despliegue y adaptar código y BPMN. No se migró una base de datos 6.8.1 a 7.2.0.** La prueba nueva inicia con un motor 7.2.0 y despliega nuevamente los modelos. Esto evita confundir una migración de archivos y APIs con una migración de datos productivos.

La razón de reemplazar los .form antiguos es concreta: Flowable 7 OSS se concentra en los motores y la API REST; ya no distribuye las aplicaciones de interfaz ni el motor de formularios que había en la línea anterior. Por eso el panel propio cumple el papel de interfaz.

## 3. Qué se cambió en los BPMN

### AS-IS: atención actual

El archivo bpmn/diagrama as-is.bpmn representa el proceso actual y no se despliega para ejecutarlo. Tiene dos participantes: Persona interesada y Peluditos Pet Chile. Dentro del proceso del negocio hay un carril para la dueña. El flujo muestra consulta por redes, respuesta por chat y decisión: se pierde el lead sin registro o se coordina la venta sin agendar fechas futuras.

Para repetirlo manualmente en un editor BPMN 2.0: dibuja las piscinas, agrega el carril de la dueña, ubica inicio, tareas, compuerta exclusiva y eventos de fin, y conecta los flujos. El nombre del evento de fin describe **qué pasó**; el nombre de la tarea describe **qué se hace**.

### TO-BE 1: Gestión de Leads

El archivo bpmn/gestion-leads.bpmn tiene isExecutable=true. El proceso comienza cuando el panel recibe un formulario. Sus pasos son:

1. **Registrar lead pendiente**: External Worker Task, tema guardarLead. El worker registra la ficha en la API local.
2. **Generar y enviar cupón**: External Worker Task, tema enviarCupon. El worker pide el código al servicio Java y simula el correo si hay dirección.
3. **Conversar y registrar resultado**: User Task asignada a admin. La dueña ve la tarea en la bandeja.
4. Una compuerta evalúa el resultado. Si es COMPRA, la tarea externa registrarCompra actualiza al lead como CLIENTE y se alcanza el fin Cliente registrado. Si es NO_CONCRETADA, cerrarLead actualiza a NO CONCRETADO y se alcanza el fin Lead no concretado.

El saludo automático en Instagram, WhatsApp o Facebook y el enlace enviado desde esas plataformas **no están conectados**. En la prueba, el formulario del panel inicia el proceso.

### TO-BE 2: cumpleaños y eventos

El archivo bpmn/oportunidades-fechas.bpmn también tiene isExecutable=true. La pantalla de campañas inicia una instancia por destinatario con el mensaje oportunidadDetectada. Luego:

1. Generar mensaje de recordatorio: External Worker Task, tema generarSugerencia; llama al servicio Java.
2. Revisar y decidir envío: User Task; la dueña puede editar el texto y aprobar o posponer.
3. Si pospone, termina en Envío pospuesto. Si aprueba, la tarea externa enviarCorreo llama al servicio de envío simulado y deja la ficha pendiente.
4. Conversar y registrar resultado: segunda User Task.
5. Si hay compra, registrarVenta actualiza la oportunidad y termina en Venta concretada. Si no, cerrarOportunidad actualiza a no concretada y termina en Oportunidad no concretada.

La tarea se llama **Generar mensaje de recordatorio**. La regla de avisar 15 días antes aparece en una anotación del BPMN y en la lógica visual del calendario. El inicio automático exactamente 15 días antes **aún no está implementado**: hoy la dueña pulsa la campaña en el panel. Una implementación posterior necesita un planificador y control de duplicados.

### Cómo se distingue cada elemento

| Elemento BPMN | Qué significa | Ejemplo |
| --- | --- | --- |
| User Task | La dueña debe decidir o registrar información | Conversar y registrar resultado |
| External Worker Task | Un programa externo ejecuta trabajo técnico | Generar y enviar cupón |
| Compuerta exclusiva | Elige una sola ruta según una variable | COMPRA o NO_CONCRETADA |
| Evento de fin | Describe el resultado alcanzado | Venta concretada |

No se usan Script Tasks ni Java Delegates para las integraciones.

## 4. Cómo se preparó Flowable 7.2

El paso 01-instalar-flowable.cmd llama a herramientas/01-flowable.ps1. Descarga el ZIP oficial de Flowable 7.2.0, comprueba su SHA-256 y extrae únicamente wars/flowable-rest.war a .runtime/flowable-rest.war. Flowable se ejecuta con Java 21 mediante iniciar-flowable-rest.cmd en el puerto 8080.

Los dos TO-BE se empaquetaron en despliegue-proceso-720.bar. El archivo BAR es un ZIP con los dos archivos BPMN. Para desplegarlo se usa desplegar-demo-flowable.cmd, que envía el BAR a la API REST de Flowable. Se comprueba el despliegue consultando las definiciones gestionLeads y oportunidadesFechas en la API REST.

El motor usa H2 en .runtime/data/flowable y el panel usa SQLite para negocio. La prueba recuperó las definiciones de H2 y los datos de SQLite después de reiniciar. También verificó una escritura nueva en SQLite. H2 abrió el archivo en solo lectura en el entorno aislado, así que queda comprobar una instancia nueva después de reiniciar desde un CMD normal. Los resultados están en [la evidencia de persistencia](../evidencias/prueba-persistencia.md).

Si se modifica un BPMN, hay que reconstruir el BAR. herramientas/preparar-bpmn.py contiene el procedimiento usado para preparar Gestión de Leads y empaquetar ambos modelos. Como ese script también reescribe el BPMN de leads, antes de usarlo conviene revisar los cambios que se quieren conservar. Para un flujo manual simple, exporta los BPMN desde el editor y vuelve a crear un ZIP .bar con ambos.

## 5. Cómo se rehizo el servicio Java

En 6.8.1 el archivo antiguo PeluditosService.java usaba com.sun.net.httpserver.HttpServer y manejaba las rutas y el JSON manualmente. Esa prueba funcionaba, pero no cumplía la observación del profesor sobre Jakarta REST ni tenía gestor de dependencias.

En la carpeta actual:

- servicio-java/pom.xml define un proyecto Maven para Java 21 y declara Jersey, Grizzly y Jackson.
- PeluditosApplication.java arranca Grizzly en 127.0.0.1:8091.
- PeluditosResource.java define recursos REST mediante anotaciones Jakarta, como @Path, @POST, @FormParam y @Produces.
- Maven descarga las bibliotecas en .runtime/m2 y, en el paso 7, construye un JAR ejecutable en servicio-java/target/.

Las rutas son: GET /health; POST /api/sugerencia; POST /api/cupon; POST /api/envio; y POST /api/estado. El cupón tiene formato diario, por ejemplo PELUDITOS-06NOV. /api/envio valida los datos y responde que el envío fue simulado: **no manda correo real**.

Una persona lo haría así: crea el pom.xml, agrega las dependencias de Jersey/Grizzly/Jackson, escribe la clase que levanta el servidor, escribe la clase de rutas con anotaciones Jakarta, ejecuta Maven para descargar dependencias y compilar, y prueba cada endpoint con curl o Postman. El archivo docs/servicios.md contiene los parámetros y ejemplos de curl.

## 6. Cómo se rehizo el external worker

El worker viejo llamaba directamente a la API de Flowable para buscar y completar trabajos. El actual, worker/worker.py, usa flowable.external-worker-client==1.0.2 y Requests. El archivo worker/requirements.txt fija esas dependencias. El paso 05-instalar-bibliotecas-python.cmd crea .runtime/venv e instala los paquetes.

El worker se suscribe a ocho temas: guardarLead, enviarCupon, registrarCompra, cerrarLead, generarSugerencia, enviarCorreo, registrarVenta y cerrarOportunidad. Cada tema coincide exactamente con flowable:topic del BPMN.

Al recibir un trabajo, el callback lee sus variables, llama al servicio Java o a la API local según corresponda, y devuelve success con variables nuevas. Flowable entonces avanza a la tarea o evento siguiente. El archivo evidencias/worker.jsonl se genera al ejecutar el proyecto y registra acciones de prueba; está excluido de Git.

Para reconstruirlo manualmente: instala la biblioteca oficial, crea un ExternalWorkerClient apuntando a Flowable REST, suscribe cada tema, implementa una función por tipo de trabajo y devuelve el resultado a Flowable. Después inicia una instancia y comprueba que la tarea externa desaparece y aparece la User Task siguiente.

## 7. Cómo se conectó el panel v4

El archivo entregado panel v4.html se copió a formularios/index.html y se conservó como base visual. Originalmente guardaba clientes en localStorage y solo mostraba una comprobación informativa de conexión a Flowable. Eso no era suficiente para ejecutar una bandeja real.

Se añadió formularios/server.py, un servidor local en 127.0.0.1:8092 que sirve el HTML y hace de puente con Flowable REST. El panel ahora:

1. Carga fichas desde GET /api/state y tareas humanas desde GET /api/tasks.
2. Inicia leads con POST /api/lead/start y oportunidades con POST /api/start.
3. Completa tareas humanas con POST /api/tasks/{id}; el servidor valida el paso actual antes de completar.
4. Muestra el mensaje sugerido, permite editarlo, aprobarlo o posponerlo, y permite registrar compra o no compra.
5. Guarda fichas, ventas y eventos en SQLite, en data/negocio.sqlite3. El servidor aplica el esquema de formularios/esquema.sql y, si existe el JSON anterior, lo importa una sola vez al inicializar la base.

La página refresca la bandeja periódicamente. El worker usa la API local para actualizar fichas cuando termina una tarea externa. Los tres servicios que deben estar abiertos durante la demostración son Flowable 8080, Java 8091 y panel 8092; el worker corre como cuarto proceso sin puerto propio.

Una persona lo haría en este orden: dibuja la pantalla HTML, implementa en JavaScript llamadas fetch a su servidor, crea las rutas del servidor que consultan Flowable REST, mapea los campos del formulario a variables de proceso y enlaza los botones de la bandeja a la acción complete de cada User Task. El estado de una oportunidad se muestra después de que el proceso lo actualiza.

## 8. Instalación separada, paso por paso

La carpeta actual sustituyó el instalador único por siete CMD. Cada CMD llama a un script PowerShell concreto; herramientas/comun.ps1 solo comparte funciones para descargar y localizar rutas.

| CMD | Qué hace | Cómo lo haría manualmente |
| --- | --- | --- |
| 01-instalar-flowable.cmd | Obtiene el WAR 7.2 y verifica el ZIP | Descargar la distribución oficial, comprobar versión y extraer flowable-rest.war |
| 02-instalar-python.cmd | Detecta Python 3.12+ o lo instala | Instalar Python y verificar python --version |
| 03-instalar-java.cmd | Detecta Java 21 o descarga JDK | Instalar JDK 21 y verificar java --version |
| 04-instalar-maven.cmd | Descarga Maven 3.9.11 | Descargar Maven, extraerlo y ubicar mvn.cmd |
| 05-instalar-bibliotecas-python.cmd | Crea venv e instala requirements.txt | Ejecutar python -m venv y pip install -r requirements.txt |
| 06-instalar-bibliotecas-java.cmd | Descarga dependencias Maven | Ejecutar Maven dependency:go-offline con el pom.xml |
| 07-compilar-servicio-java.cmd | Genera el JAR | Ejecutar Maven package y comprobar target/ |

Si Java o Python ya están instalados y cumplen la versión, los pasos 2 y 3 los detectan y guardan su ruta; no los reinstalan. Los CMD numerados se ejecutan una vez o cuando haya que reparar su componente. La carpeta compartida no trae .runtime/, target/ ni data/: se generan localmente en cada equipo. Así el ZIP puede subirse a GitHub sin incluir el WAR de más de 90 MB.

## 9. Cómo iniciar y demostrar la solución

Después de los siete instaladores, abre estos CMD en orden:

1. iniciar-flowable-rest.cmd; espera a que indique que el motor inició en 8080.
2. desplegar-demo-flowable.cmd; despliega ambos BPMN. Normalmente basta la primera vez.
3. iniciar-servicio-java.cmd; deja abierto el puerto 8091.
4. iniciar-panel.cmd; deja abierto el puerto 8092.
5. iniciar-worker.cmd; observa las ocho suscripciones.

Abre http://127.0.0.1:8092/ en el navegador. En Formulario registra una persona y mascota con datos de prueba. Espera a que aparezca la ficha pendiente y su tarea en Hoy. Marca Compró o No compró y verifica que la tarea desaparece. Después prepara una campaña de cumpleaños, revisa y aprueba el correo simulado y registra el resultado.

Para probar los servicios sin interfaz, usa los ejemplos de docs/servicios.md. Para probar ambos procesos completos, con los cuatro procesos abiertos ejecuta:

~~~cmd
.runtime\venv\Scripts\python.exe pruebas\smoke.py
~~~

La prueba inicia dos leads, cubre compra y no compra, inicia una oportunidad de cumpleaños, completa sus dos User Tasks y consulta el historial de Flowable para confirmar el fin. Crea datos ficticios en la carpeta local.

## 10. Qué está probado y qué falta

En la copia de prueba pasaron la instalación de Maven, bibliotecas Python y Java, compilación Jakarta REST, despliegue de los dos BPMN y smoke.py. También se completó una tarea real desde la bandeja del navegador. El paso de Flowable se probó con ZIP oficial previamente descargado y verificado; se comprobó que repara un WAR incompleto.

La rama que descarga e instala Python o Java cuando faltan queda pendiente de probar en otro computador. El alcance futuro incluye envío SMTP, registro desde redes, autenticación de usuarios finales y un planificador automático de 15 días. En esta entrega H2 guarda los datos del motor y SQLite guarda las fichas, ventas y eventos. El panel usa la cuenta de prueba de Flowable REST.

Para avanzar a una solución real habría que: acordar la política de datos personales y acceso, reemplazar el envío simulado por un proveedor de correo, conectar el formulario público y canales sociales, programar el detector diario de cumpleaños con deduplicación, mover clientes y mascotas a una base de datos compartida, y añadir pruebas de fallos y reintentos del worker.

## 11. Receta manual resumida para un integrante nuevo

1. Lee el caso de Peluditos y escribe en una hoja qué ocurre hoy, qué datos faltan y qué decisiones debe tomar la dueña.
2. En un editor BPMN dibuja el AS-IS con participantes y carril. Exporta el XML BPMN y comprueba que sea solo descriptivo.
3. Dibuja Gestión de Leads. En propiedades marca el proceso ejecutable, asigna admin a la tarea humana y configura cada tarea de servicio como external-worker con el tema exacto. Repite para oportunidades; escribe la regla de 15 días en una anotación.
4. Guarda los dos BPMN. Crea un ZIP con **los dos archivos en la raíz del ZIP**, sin carpetas internas, y usa la extensión .bar. Ese es el despliegue.
5. Instala Flowable OSS 7.2 y Java 21; inicia Flowable. Publica el BAR con desplegar-demo-flowable.cmd. Consulta las definiciones en la API REST para confirmar que Flowable aceptó ambos XML.
6. En un IDE Java crea un proyecto Maven. Copia la declaración de dependencias de servicio-java/pom.xml, implementa la aplicación y los recursos REST, ejecuta Maven package y prueba cada ruta con curl.
7. Crea un entorno virtual Python, instala worker/requirements.txt y programa el worker: una suscripción por tema BPMN, lectura de variables, llamada HTTP y resultado success. Inícialo y verifica en consola las ocho suscripciones.
8. Implementa la API del panel: listar tareas, iniciar instancias y completar User Tasks usando Flowable REST. Conecta esas rutas a los botones del HTML. Prueba primero un lead y después una oportunidad.
9. Ejecuta pruebas/smoke.py y revisa el historial de las instancias. Guarda capturas o resultados en evidencias/ para que cada integrante pueda explicar su contribución.

Los CMD automatizan descarga, compilación y arranque. La comprensión del BPMN, las rutas y las variables sigue siendo trabajo del equipo: cada integrante debe poder señalar qué acción humana o automática ejecuta cada paso.

## Referencias oficiales

- Flowable 7.2.0: https://github.com/flowable/flowable-engine/releases/tag/flowable-7.2.0
- Cambio de alcance de Flowable OSS 7: https://github.com/flowable/flowable-engine/releases/tag/flowable-7.0.0
- Cliente Python de external worker: https://github.com/flowable/flowable-external-client-python/blob/main/external-worker/README.md
- Jakarta REST: https://jakarta.ee/specifications/restful-ws/
- Maven: https://maven.apache.org/
