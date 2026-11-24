# Persistencia

| Información | Componente responsable | Persistencia |
| --- | --- | --- |
| Contactos, cumpleaños, eventos, ventas y oportunidades | API Python del panel | SQLite, archivo configurable con `PELUDITOS_DB` |
| Punto hasta el que se importaron las respuestas de Google Forms | API Python del panel | SQLite, tabla `google_forms_cursor` |
| Instancias, tareas, trabajos automáticos e historial BPMN | Flowable OSS 7.2 | Base dedicada en PostgreSQL, configurable con `FLOWABLE_DB_URL` |
| Respuestas originales del formulario | Cuenta Google del negocio | Google Forms |

El panel aplica [esquema.sql](../panel-peluditos/esquema.sql) al arrancar. En bases anteriores reconoce las fichas con ventas y recupera su estado de cliente. Las ventas se vinculan por instancia para que repetir un trabajo no genere otra venta. El envío de una campaña crea una oportunidad pendiente. Al terminar el proceso, el worker modifica esa oportunidad. Una venta y el estado de esa oportunidad se guardan en la misma transacción.

Se conserva SQLite para un solo equipo porque el panel es el único servicio que abre ese archivo. Cada operación usa una transacción y las escrituras se serializan. PostgreSQL o MariaDB son opciones si el despliegue pasa a varios equipos o necesita más escrituras simultáneas. Se mantienen separadas la persistencia del motor y la de negocio.

Flowable crea sus tablas en `peluditos_flowable` al arrancar por primera vez. Despliega luego los dos TO-BE. Las instancias antiguas de H2, si existen, siguen en su archivo original. La instalación configura una base nueva de Flowable.

Para demostrar los datos, abre en DB Browser el archivo indicado por `PELUDITOS_DB` y entra a **Browse Data**. Usa `clientes` para la ficha, `ventas` para comprobar montos y `oportunidades` para ver el resultado por campaña.
