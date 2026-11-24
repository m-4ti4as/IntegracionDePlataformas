# Prueba de los instaladores separados

Fecha: 06-11-2026. La prueba se hizo en una copia de esta carpeta, en Windows.

- Paso 1: el script reconoció un WAR Flowable 7.2 existente. Además se probó la extracción desde un ZIP oficial cuya huella SHA-256 coincidió; generó `flowable-rest.war` de 91 273 507 bytes.
- Revisión posterior: un WAR incompleto se reconstruyó correctamente desde el ZIP verificado.
- Pasos 2 y 3: detectaron Python 3.14 y Java 21 ya instalados. Las ramas que descargan Python o Java cuando faltan no se probaron en otro computador.
- Paso 4: descargó Maven 3.9.11.
- Paso 5: creó el entorno Python e instaló `flowable.external-worker-client==1.0.2` y Requests.
- Paso 6: Maven descargó Jersey, Grizzly y las demás dependencias del `pom.xml`.
- Paso 7: Maven generó `servicio-mensajes-1.0.0.jar`.
- Después se inició Flowable REST, se desplegaron los dos BPMN, y se ejecutó `pruebas/smoke.py`. Pasaron las dos salidas de Gestión de Leads y la oportunidad completa de cumpleaños.

La carpeta para compartir no incluye `.runtime/`, `data/`, `target/` ni registros de esta prueba. Cada compañero genera esos archivos al ejecutar los CMD.
