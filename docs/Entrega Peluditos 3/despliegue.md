# Despliegue y configuración

El destino elegido para esta versión es un computador Windows de la dueña. Google Forms recibe respuestas por internet. Los servicios internos escuchan en loopback en la instalación local. El panel obtiene las respuestas mediante HTTPS.

## Configuración por entorno

| Ajuste | Variables |
| --- | --- |
| Dirección de enlace y puerto de Flowable | `FLOWABLE_HOST`, `FLOWABLE_PORT` |
| URL de acceso y cuenta REST de Flowable | `FLOWABLE_BASE`, `FLOWABLE_USER`, `FLOWABLE_PASSWORD` |
| Conexión del motor | `FLOWABLE_DB_URL`, `FLOWABLE_DB_USER`, `FLOWABLE_DB_PASSWORD` |
| Dirección y URL del servicio de mensajes | `PELUDITOS_API_HOST`, `PELUDITOS_API_PORT`, `PELUDITOS_API` |
| Dirección y URL del panel | `PELUDITOS_UI_HOST`, `PELUDITOS_UI_PORT`, `PELUDITOS_PANEL` |
| Archivo de datos de negocio | `PELUDITOS_DB` |
| Registro público e importación de respuestas | `GOOGLE_FORMS_PUBLIC_URL`, `GOOGLE_FORMS_EXEC_URL`, `GOOGLE_FORMS_SYNC_KEY` |

Los CMD leen `config.local` sin modificar el código. Ajusta cada URL cuando cambies el puerto correspondiente. Usa valores sin comillas. SQLite acepta una ruta absoluta o relativa a la raíz. La cuenta REST de Flowable y el usuario de PostgreSQL se configuran por separado. `config.example` es la plantilla que se versiona.

## PostgreSQL para Flowable

- Ejecuta `08-configurar-postgresql.cmd` una vez. Prepara PostgreSQL 17.12, el controlador JDBC y la base `peluditos_flowable` con un usuario dedicado. La instancia local escucha en `127.0.0.1:5432`. Si ya hay un servidor en ese puerto, antes de instalar usa `08-configurar-postgresql.cmd -Puerto 15432`.
- `iniciar-flowable-rest.cmd` inicia el PostgreSQL de esta carpeta según la URL configurada. En el primer arranque Flowable prepara las tablas. Después, ejecuta `desplegar-demo-flowable.cmd`. Para reiniciar ambos servicios, cierra Flowable, ejecuta `detener-postgresql.cmd` y abre nuevamente Flowable.
- Para usar un PostgreSQL administrado aparte, crea una base dedicada y un rol con permiso para crear tablas en ella. Indica esa conexión en `config.local` con `FLOWABLE_DB_URL`, `FLOWABLE_DB_USER` y `FLOWABLE_DB_PASSWORD`. El arranque prepara el controlador JDBC y conecta con el servidor indicado.
- Para consultar una base histórica de H2, usa la configuración anterior guardada en `.runtime/config.antes-postgresql`. El paso 08 mantiene el archivo H2 que existía. El historial de H2 y el nuevo historial de PostgreSQL quedan en sus respectivos motores.

Para verificar la instalación, clona el monorepo en un equipo limpio, sigue el orden del README, abre el panel y ejecuta la demostración. Cierra los servicios desde sus consolas, vuelve a iniciarlos y comprueba que el panel mantiene las ventas, que reaparecen las tareas y que se puede iniciar un nuevo proceso. Para verificar portabilidad, cambia los puertos de los tres servicios y las URL correspondientes.

## Control de versiones

Esta carpeta es una copia de trabajo local. Los componentes de Entrega 3 deben incorporarse juntos a la estructura vigente del monorepo del equipo mediante commits. Un tag permite recuperar la Entrega 2. Cada integrante puede trabajar en su propia rama para revisar sus cambios antes de integrarlos. `config.local`, los archivos de bases de datos, `.runtime` y las trazas generadas quedan fuera de Git.

Incorpora estos archivos a la ubicación existente del proyecto en el clon del equipo. Usa Git para preparar el commit y revisa la lista de archivos con `git status --short`. Publica los cambios de la misma aplicación. Si otra persona necesita importar respuestas, comparte los dos valores privados de Google Forms por separado con alguien autorizado. [Configuración del formulario](../google-forms/README.md)

## Pendientes para la Entrega 4

- Definir con la dueña si se habilitará correo real y cuándo se programa el inicio automático de campañas.
- Probar en el equipo de la dueña y acordar respaldo y recuperación antes de incorporar información real.
- Si el destino cambia a varios usuarios o aplicaciones que escriben a la vez, reevaluar SQLite para la base de negocio.
