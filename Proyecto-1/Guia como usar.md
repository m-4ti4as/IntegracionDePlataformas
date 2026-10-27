# Guía de demostración

Se necesita Java 21 JDK y Python 3. La primera vez también se necesita internet para descargar Flowable 6.8.1.

Abre estos archivos desde esta carpeta y en este orden:

1. `iniciar-flowable-rest.cmd`. Espera a que aparezca `Started FlowableRestApplication` y deja la ventana abierta.
2. `desplegar-demo-flowable.cmd`. Espera a que aparezca `Despliegue terminado`. Esta ventana se puede cerrar.
3. `iniciar-servicio-java.cmd`. Deja la ventana abierta.
4. `iniciar-worker.cmd`. Deja la ventana abierta.
5. `iniciar-panel.cmd`. Deja la ventana abierta.

Después abre `http://127.0.0.1:8092/` en el navegador e inicia un caso de prueba.

Para ver los BPMN en Flowable Modeler, ejecuta `abrir-flowable-modeler.cmd`. Entra a `http://127.0.0.1:8083/flowable-ui/` con usuario `admin` y clave `test`. Importa los archivos de `bpmn/`.

Si Flowable REST se cerró, vuelve a ejecutar el paso 1 y después el paso 2. Si un puerto está ocupado, revisa si ya tienes abierta otra ventana del mismo programa. Para cerrar una ventana en ejecución usa Ctrl+C.

El correo de la prueba es simulado. Los datos del motor son temporales y se pierden al cerrarlo.
