
# Peluditos Pet Chile · Entrega 2

La solución ayuda a Peluditos Pet Chile a registrar clientes y mascotas, dar seguimiento a ventas y preparar campañas para cumpleaños y fechas especiales.

## Qué se hizo

- **Gestión de Leads.** El formulario crea un contacto y su mascota. Flowable coordina el registro y la generación de un cupón. La dueña recibe una tarea en la bandeja y registra si hubo compra.
- **Oportunidades por fechas.** La dueña inicia una campaña desde el panel. El worker solicita un mensaje al servicio Java, la dueña lo revisa y puede aprobar o posponer el envío. El correo se simula y el resultado comercial queda en la ficha.
- **Integración.** Flowable OSS 7.2.0 ejecuta los BPMN y conserva sus instancias, tareas e historial en H2. El panel propio de HTML, CSS y JavaScript se comunica con una API Python. El external worker Python atiende las tareas automáticas y llama a los servicios Jakarta REST.
- **Persistencia.** SQLite reemplazó al archivo JSON como almacenamiento de negocio. El panel aplica el esquema SQL al arrancar y guarda fichas, ventas y eventos. Puede importar los datos del JSON anterior en el primer arranque.

## Observaciones del profesor

| Observación | Corrección y estado |
| --- | --- |
| Videos de presentación | Pendiente de publicar los dos videos y agregar sus enlaces en [Videos](Videos/README.md). |
| Identificación en GitHub | Cada integrante debe revisar que su perfil muestre su nombre y apellido y que sus aportes se atribuyan a esa cuenta. |
| Estructura del monorepo | Esta copia organiza los componentes en `panel-peluditos/`, `worker-python/` y `servicio-java/`, listos para incorporarlos al repositorio del equipo. |
| Piscinas y carriles en el AS-IS | El modelo tiene las piscinas **Persona interesada** y **Peluditos Pet Chile**, y el carril **Dueña de Peluditos**. [BPMN AS-IS](BPMN/AS-IS.bpmn) |
| Nombres de tareas y eventos finales | Las tareas nombran acciones como **Registrar venta** y **Actualizar estado del lead a cliente**. Los eventos finales describen el resultado del proceso. [Gestión de Leads](BPMN/gestion-leads.bpmn) · [Oportunidades por fechas](BPMN/oportunidades-fechas.bpmn) |
| Regla de los 15 días | La tarea se llama **Generar mensaje de recordatorio** y la anticipación está en una anotación. El calendario muestra las fechas próximas y la dueña inicia la campaña desde el panel. |
| External worker | El worker se suscribe a los ocho temas de los BPMN con `ExternalWorkerClient`, ejecuta el trabajo y devuelve los resultados a Flowable. [Worker Python](worker-python/worker.py) |
| Servicios web Java | Los recursos usan Jakarta REST con Jersey. Maven administra las dependencias y compila el servicio. [Proyecto Maven](servicio-java/pom.xml) · [Recurso REST](servicio-java/src/main/java/cl/peluditos/PeluditosResource.java) |

## Estructura

| Carpeta | Contenido |
| --- | --- |
| [BPMN](BPMN/) | Proceso [AS-IS](BPMN/AS-IS.bpmn) y dos TO-BE ejecutables en Flowable OSS 7.2.0. |
| [panel-peluditos](panel-peluditos/) | Interfaz HTML, CSS y JavaScript, API Python y esquema SQLite. |
| [worker-python](worker-python/) | External worker que ejecuta tareas automáticas y comunica el resultado a Flowable. |
| [servicio-java](servicio-java/) | API Jakarta REST con Jersey y Grizzly, compilada con Maven. |
| [Arquitectura](Arquitectura/README.md) | Diagrama editable con los componentes implementados y planificados. |
| [docs](docs/) | Contratos de los servicios y decisiones de persistencia. |
| [pruebas](pruebas/) y [evidencias](evidencias/) | Prueba integrada y resultados de persistencia. |
| [Actas](Actas/) y [Videos](Videos/) | Actas semanales y enlaces a las grabaciones. |

## Instalación en Windows

Descarga o clona el repositorio y entra a la carpeta que contiene los CMD. Con conexión a internet, ejecuta cada instalador y espera a que termine antes de pasar al siguiente.

1. `01-instalar-flowable.cmd`
2. `02-instalar-python.cmd`
3. `03-instalar-java.cmd`
4. `04-instalar-maven.cmd`
5. `05-instalar-bibliotecas-python.cmd`
6. `06-instalar-bibliotecas-java.cmd`
7. `07-compilar-servicio-java.cmd`

## Inicio

1. Abre `iniciar-flowable-rest.cmd` y espera a que Flowable inicie en el puerto **8080**.
2. Abre `desplegar-demo-flowable.cmd`. El script empaqueta los dos TO-BE desde `BPMN/` y los despliega. Repite este paso si cambias los modelos.
3. Abre `iniciar-servicio-java.cmd` para iniciar Jakarta REST en el puerto **8091**.
4. Abre `iniciar-panel.cmd` para iniciar el panel en el puerto **8092**.
5. Abre `iniciar-worker.cmd` y entra al [panel local](http://127.0.0.1:8092/).

Mantén abiertas las cuatro ventanas de los servicios mientras usas el panel.

## Demostración

- **Gestión de leads.** En **Formulario**, registra a un cliente y su mascota. El worker registra el lead y genera el cupón. En **Hoy → Bandeja de tareas**, marca si hubo compra y consulta el resultado en **Clientes**.
- **Oportunidades.** En **Campañas**, inicia un recordatorio de cumpleaños o evento. Revisa y aprueba el mensaje en la bandeja. Registra el resultado de la conversación.
- **Persistencia.** Reinicia el panel y busca la misma ficha y su venta. SQLite guarda los datos del negocio en `data/negocio.sqlite3`. Flowable guarda el estado de los procesos en H2 bajo `.runtime/data/`.

El envío de correo es simulado. La dueña inicia las campañas desde el panel y el calendario muestra las próximas fechas. El envío real, la integración con redes sociales y el inicio automático quedan para otra etapa.

Con los cuatro servicios activos, ejecuta `.runtime\venv\Scripts\python.exe pruebas\smoke.py` para probar los endpoints Java, ambos resultados de Gestión de Leads y una oportunidad de cumpleaños completa.

El worker registra la sugerencia y el evento `correo-simulado` en `evidencias/worker.jsonl` al ejecutar la demostración. La evidencia detalla los resultados verificados y la comprobación pendiente de escritura en H2 tras reiniciar.

[Contratos de los servicios](docs/servicios.md) · [Guía de persistencia](docs/persistencia.md) · [Evidencia de pruebas](evidencias/prueba-persistencia.md)
