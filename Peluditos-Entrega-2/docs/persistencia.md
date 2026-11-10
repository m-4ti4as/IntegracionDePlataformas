# Persistencia de datos

| Responsabilidad | Tecnología | Archivo de trabajo | Qué guarda |
| --- | --- | --- | --- |
| Motor de procesos | H2 en modo archivo, por JDBC | `.runtime/data/flowable.mv.db` | Definiciones, instancias, tareas e historial de Flowable |
| Negocio | SQLite mediante el módulo estándar `sqlite3` de Python | `data/negocio.sqlite3` | Clientes y mascotas, estados y cupones, ventas y fechas de eventos |

H2 ahora forma parte del despliegue de Flowable. SQLite permite que el panel se ejecute en Windows con el mismo Python del proyecto. La API del panel controla el acceso y el worker usa esa API. Ambas bases están dentro del proyecto y se crean al iniciar sus servicios.

El panel aplica automáticamente [el esquema SQL](../panel-peluditos/esquema.sql). Las ventas tienen una referencia a su ficha. Si el worker reintenta guardar una venta, la clave de la instancia de Flowable impide crear un duplicado. El estado y la venta se actualizan en la misma transacción.


## Demostración de guardado y reinicio

1. Iniciar la solución siguiendo el [README](../README.md).
2. Registra al cliente, espera el cupón y completa la tarea con **Compró**. Indica un producto y un monto. También puedes agregar una fecha en **Campañas**.
3. Verificar la ficha, la venta y la fecha en el panel. La consulta `http://127.0.0.1:8092/api/state` permite ver el mismo resultado en JSON.
4. Cerrar el worker, el panel y Flowable. Iniciar Flowable, el panel y el worker en ese orden. El servicio Java puede seguir encendido. Conserva ambos archivos de base de datos.
5. Buscar la misma ficha y la fecha. Verifica que Flowable conserve sus definiciones en `http://127.0.0.1:8080/flowable-rest/service/repository/process-definitions`. En la demo local se usan `rest-admin` y `test`.
6. Crea otra ficha y completa la tarea para comprobar que se puede guardar un registro nuevo después del reinicio.

Para revisar SQLite visualmente, abre `data/negocio.sqlite3` en DB Browser for SQLite. En **Browse Data**, elige `clientes` o `ventas`. El `id` de la ficha coincide con el `cliente_id` de sus ventas.
