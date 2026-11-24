# Pruebas de Entrega 3

Pruebas realizadas el 19 de noviembre de 2026 en una copia separada con datos ficticios. El servicio Java se compiló con Maven y las dependencias disponibles. Los dos TO-BE se ejecutaron en Flowable OSS 7.2.0.

| Escenario | Resultado observado |
| --- | --- |
| Arranque y despliegue con configuración externa | Flowable, Java y el panel respondieron en 18180, 18191 y 18192. El empaquetador desplegó los dos TO-BE con la cuenta REST de prueba. |
| Gestión de leads | Pasaron las ramas de compra y de cierre sin compra. El alta incompleta y el intento de guardar una compra sin monto y producto devolvieron un error de validación. |
| Campaña de cumpleaños | Pasaron las ramas de cierre sin envío, envío y cierre sin compra, y envío con segunda compra. Un intento de campaña para un interesado sin compra se rechazó. Una campaña sin venta conservó la condición de cliente y su venta anterior. |
| Repetición del registro de venta | Repetir la escritura de una venta desde la misma instancia conservó una sola venta para esa instancia. |
| Reinicio del panel | SQLite devolvió las mismas fichas, ventas y oportunidades después del reinicio. |
| Caída de Java | Se detuvo Java durante la generación del cupón. El worker registró el error para esa instancia. Tras reiniciar Java, se generó el cupón y apareció la tarea humana. |
| Google Forms con proveedor simulado | Se importó una respuesta válida y se omitió otra con correo inválido. Al repetir el lote sin el cursor guardado, Flowable reconoció la misma respuesta y el panel conservó una sola ficha. |
| Inicio de la consulta desde la pantalla | Se verificó el JavaScript con una API simulada. Ejecutó la sincronización al abrir y al pulsar **Actualizar respuestas**. El script de Google se probó con servicios simulados para comprobar las preguntas, la clave y el orden de un lote. |
| Reinicio de Flowable con H2 | Una tarea humana pendiente reapareció. La escritura de otra instancia recibió HTTP 502 del panel porque H2 abrió el archivo como solo lectura en el entorno de prueba. El resultado con PostgreSQL se documenta más abajo. |

Para repetir las pruebas locales con los servicios activos, ejecuta `pruebas/smoke.py` mediante el comando del README. Para las pruebas del importador con respuestas controladas, ejecuta `pruebas/test_google_forms.py` con el mismo Python.

## Flowable con PostgreSQL · 20 de noviembre de 2026

Se instaló PostgreSQL 17.12 con JDBC 42.7.14 y se desplegaron los dos TO-BE en la base local `peluditos_flowable`. Se verificó la versión del servidor y la presencia de ambos modelos consultando PostgreSQL directamente.

| Prueba en una base aislada | Resultado |
| --- | --- |
| Instalación en otro puerto y repetición del instalador | PostgreSQL inició en 15434. Repetir la configuración conservó la misma cuenta y contraseña. |
| Ejecución integrada con el nuevo motor | Pasaron ambos resultados de Gestión de Leads y los tres caminos de Cumpleaños. Respondieron los servicios Jakarta REST y se verificó que repetir el registro de una venta deja una sola fila. |
| Reinicio del panel | SQLite devolvió las mismas fichas, ventas y oportunidades. |
| Reinicio de PostgreSQL y Flowable | Se dejó una tarea humana abierta, se detuvieron ambos servicios y se iniciaron nuevamente. La misma tarea reapareció con el mismo identificador y se completó desde la API del panel. |
| Escritura después del reinicio | Se inició otro proceso y apareció su tarea humana. Los dos identificadores de proceso constaban en el historial de PostgreSQL. |

Para repetir la prueba de reinicio, registra a un interesado ficticio y deja su seguimiento pendiente. Cierra Flowable, ejecuta `detener-postgresql.cmd` y vuelve a abrir `iniciar-flowable-rest.cmd`. Abre la bandeja, completa la tarea recuperada y registra un interesado nuevo. Los modelos permanecen desplegados en PostgreSQL durante el reinicio.

## Google Forms publicado · 20 de noviembre de 2026

| Escenario | Resultado observado |
| --- | --- |
| Acceso a las respuestas | Apps Script respondió por HTTPS con la clave configurada y rechazó la consulta con una clave incorrecta. |
| Registro público y seguimiento | Se envió una respuesta ficticia por Google Forms. El panel inició Gestión de Leads, se guardó el interesado con estado pendiente, se generó su cupón y apareció la tarea humana. La prueba aislada cerró como **No concretado** y Flowable registró el fin. |
| Resincronización | Tras volver a sincronizar y reiniciar el panel de prueba, quedó una sola ficha para la misma respuesta. |
| Instancia de trabajo en el puerto 8092 | Se corrigió la configuración de la copia en uso, se reiniciaron los servicios y se importaron dos respuestas disponibles. El registro ficticio apareció como **Pendiente** con cupón. Al volver a abrir **Formulario**, el panel mostró el enlace público, la opción de actualizar y el mensaje **No hay respuestas nuevas**. |

## Verificación de la copia para GitHub

Se consultó el formulario real con la configuración privada de esta copia y se ejecutaron las dos pruebas del importador. En un directorio de prueba con dependencias en caché se desplegaron ambos BPMN en PostgreSQL, se ejecutaron los recorridos de compra y campaña y se recuperó una tarea tras reiniciar el motor. Se comprobó que el paso 08 conserva los ajustes de Google Forms y que Git excluye `config.local`, las bases y las trazas.
