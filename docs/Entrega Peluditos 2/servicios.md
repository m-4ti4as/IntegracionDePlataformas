# Servicios y tareas externas

El servicio Java está en `servicio-java/`. Usa Jakarta REST con Jersey y Maven. Escucha solo en `127.0.0.1:8091`. Recibe datos `application/x-www-form-urlencoded` y responde JSON.

| Ruta | Entrada | Salida | Uso en el proceso |
| --- | --- | --- | --- |
| `GET /health` | Ninguna | `{"estado":"ok"}` | Comprobar servicio |
| `POST /api/cupon` | `clienteId` | `codigo` | Generar cupón diario para lead |
| `POST /api/sugerencia` | `nombre, mascota, tipo, evento` | `mensaje` | Sugerir recordatorio |
| `POST /api/envio` | `destinatario, mensaje` | `simulado: true` | Simular correo/cupón |
| `POST /api/estado` | `resultado=COMPRA` o `NO_CONCRETADA` | `estado` | Validar estado final |

Ejemplos con `curl`:

```cmd
curl.exe -f -X POST -d "clienteId=prueba123" http://127.0.0.1:8091/api/cupon
curl.exe -f -X POST -d "resultado=COMPRA" http://127.0.0.1:8091/api/estado
curl.exe -f -X POST -d "nombre=Ana&mascota=Luna&tipo=Perro&evento=CUMPLEANOS" http://127.0.0.1:8091/api/sugerencia
```

El worker Python usa `flowable-external-worker-client`. Se suscribe a:

| Proceso | Tema | Acción |
| --- | --- | --- |
| Gestión de Leads | `guardarLead` | Registra ficha pendiente mediante API local |
| Gestión de Leads | `enviarCupon` | Llama a `/api/cupon` y `/api/envio` |
| Gestión de Leads | `registrarCompra`, `cerrarLead` | Llama a `/api/estado` y actualiza ficha |
| Oportunidades | `generarSugerencia` | Llama a `/api/sugerencia` |
| Oportunidades | `enviarCorreo` | Llama a `/api/envio` y marca pendiente |
| Oportunidades | `registrarVenta`, `cerrarOportunidad` | Llama a `/api/estado` y cierra |

La API del panel (`127.0.0.1:8092`) expone `/api/lead/start`, `/api/start`, `/api/tasks`, `/api/tasks/{id}`, `/api/state` y rutas internas de actualización de clientes. Las User Tasks se completan solo desde esta API; el Java REST realiza las reglas de cupón, mensaje, envío simulado y estado.

Se priorizaron el cupón, el recordatorio, el envío simulado y el cambio de estado para completar ambos recorridos con una intervención humana. El correo real y el inicio automático quedan para una etapa posterior. Al cerrar una tarea con compra, el panel puede enviar el detalle de la venta. El worker guarda la venta y el estado de la ficha mediante la API local y una sola transacción SQLite.

La prueba automatizada de `pruebas/smoke.py` verifica las rutas REST, las dos salidas de Gestión de Leads y una oportunidad completa hasta su evento final.
