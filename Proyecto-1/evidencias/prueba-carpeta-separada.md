# Prueba de la copia separada

Fecha: 26-10-2026.

Se probó la misma versión de archivos en una copia separada de la carpeta original:

1. `preparar-flowable.ps1` descargó el ZIP oficial de Flowable 6.8.1, verificó su SHA-256 y extrajo `flowable-rest.war` y `flowable-ui.war`.
2. `iniciar-flowable-rest.cmd` inició el motor en 8080.
3. `desplegar-demo-flowable.cmd` instaló el proceso y los dos formularios.
4. `iniciar-servicio-java.cmd`, `iniciar-worker.cmd` e `iniciar-panel.cmd` iniciaron sus servicios.
5. Desde el panel se creó un caso de prueba, apareció el mensaje sugerido, se aprobó el envío simulado y se registró una compra. Flowable terminó el proceso con `estadoOportunidad=CONCRETADA`.
6. `abrir-flowable-modeler.cmd` inició Modeler en 8083.

Los archivos WAR de esa prueba se excluyeron de esta carpeta para que pueda subirse a GitHub. Al abrir `iniciar-flowable-rest.cmd` por primera vez, se descargarán otra vez.

