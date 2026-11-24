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
| Oportunidades | `enviarCorreo` | Llama a `/api/envio` y registra la oportunidad como pendiente |
| Oportunidades | `registrarVenta`, `cerrarOportunidad` | Llama a `/api/estado` y actualiza el resultado de la oportunidad |

La API del panel expone `/api/lead/start`, `/api/start`, `/api/tasks`, `/api/tasks/{id}` y `/api/state`. El worker escribe clientes y oportunidades mediante las rutas internas del panel. Las tareas humanas se completan desde la API del panel. El servicio REST Java aplica las reglas de cupón, mensaje, envío simulado y estado.

Al marcar una compra, el panel exige el producto y el monto. El worker guarda la venta y el cambio de estado en una transacción. El servidor consulta las respuestas de Google mediante Apps Script e inicia Gestión de Leads para cada respuesta válida. La clave de sincronización se usa en el servidor.

La prueba automatizada de `pruebas/smoke.py` verifica las rutas REST, las dos salidas de Gestión de Leads y una oportunidad completa hasta su evento final.
