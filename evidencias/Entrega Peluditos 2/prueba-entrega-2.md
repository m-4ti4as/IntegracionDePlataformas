# Prueba local de Entrega 2

Fecha: 06-11-2026. Equipo: Windows, Java 21, Python 3, Flowable OSS 7.2.0.

- El BAR desplegó `gestionLeads` y `oportunidadesFechas` como procesos ejecutables.
- Los servicios Java `/health`, `/api/sugerencia`, `/api/cupon`, `/api/estado` y `/api/envio` respondieron correctamente.
- `pruebas/smoke.py` inició dos leads, comprobó que el worker generó cupón y tarea humana, completó compra y no compra, y verificó que ambas instancias terminaron.
- La misma prueba inició una oportunidad de cumpleaños, esperó la sugerencia, aprobó el mensaje, verificó el envío simulado, registró la compra y confirmó el evento final.
- El panel abrió en el navegador y mostró Flowable conectado, clientes, calendario y bandeja de tareas.
- Desde la bandeja se pulsó **No compró** en una tarea real: la tarea desapareció, la ficha dejó de estar pendiente y mostró **no concretado**.
- Se volvió a abrir la base H2 después de reiniciar Flowable y las definiciones desplegadas seguían disponibles. En el entorno aislado de Codex, el archivo recibió permiso de solo lectura para ese proceso después del reinicio; falta comprobar una escritura posterior con el CMD normal del usuario.

Salida de la prueba:

```text
Servicios Jakarta REST: OK
Gestión de Leads: COMPRA OK
Gestión de Leads: NO_CONCRETADA OK
Oportunidad de cumpleaños: OK
Prueba completa: OK
```

Las pruebas usan datos inventados. El envío es simulado. El instalador automático de Java/Python cuando faltan no se probó en otro computador.
