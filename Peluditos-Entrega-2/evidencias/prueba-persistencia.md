# Prueba de integración y persistencia

Ejecutada el 8 de noviembre de 2026 en una copia aislada del proyecto, con datos ficticios y Flowable OSS 7.2.0.

| Comprobación | Resultado observado |
| --- | --- |
| Despliegue del BAR | Flowable registró los dos BPMN ejecutables |
| Servicios y recorrido integrado | `pruebas/smoke.py` pasó compra y no compra de leads, y una oportunidad de cumpleaños hasta su fin |
| Escritura de negocio | El worker guardó en SQLite una venta de prueba con monto de 14 990 y cupón aplicado. La API guardó una fecha adicional |
| Importación | Se importó un JSON ficticio con una ficha, una venta y un evento. Al reiniciar, no se duplicó ningún registro |
| Lectura después de reiniciar panel y motor | La API devolvió las mismas 3 fichas, 2 ventas y 2 fechas |
| Escritura después de reiniciar el panel | Se editó una ficha por la API y se confirmó la escritura con una consulta SQL |
| Integridad | `PRAGMA integrity_check` devolvió `ok` y `PRAGMA foreign_key_check` no devolvió filas |
| Motor tras el reinicio | Flowable volvió a leer las dos definiciones de H2. La escritura de una instancia nueva recibió HTTP 500 porque H2 abrió el archivo en solo lectura en el entorno aislado |

Se aisló la diferencia en el último punto. En ese entorno, Java devolvió `false` para `Files.isWritable` sobre el archivo de H2, aunque permitió abrir un canal de escritura. H2 usa esa comprobación para decidir si abre la base en modo de solo lectura. Queda ejecutar el último paso desde un CMD normal en una carpeta escribible. La escritura en SQLite después del reinicio sí quedó verificada.

Para repetir la demostración, sigue [la guía de persistencia](../docs/persistencia.md).

## Verificación de la carpeta de publicación

El 9 de noviembre de 2026 se compiló el servicio Java con las dependencias en caché. El empaquetador generó un BAR con los mismos dos BPMN de la prueba integrada. En una base SQLite vacía se guardaron una ficha, una venta y un evento. Después de volver a inicializar la base, se recuperaron los tres registros. Reintentar el registro de la misma venta no generó un duplicado.

El entorno de prueba bloqueó la conexión local de Tomcat al iniciar Flowable. La verificación de esta carpeta cubrió el empaquetado, la compilación y SQLite. El recorrido HTTP está documentado en la prueba integrada del 8 de noviembre.
