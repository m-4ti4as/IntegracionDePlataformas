# Servicios web de la solución

## Implementado para semana 3

| Servicio | Operación | Entrada | Salida | Uso |
| --- | --- | --- | --- | --- |
| Sugerencia en Java | POST /api/sugerencia | nombre, mascota, tipo, evento | mensaje | Worker generarSugerencia |
| Flowable REST | External Worker API | topic, workerId, variables | tarea adquirida/completada | Continuación BPMN |
| Flowable Forms | Form API | definición, tarea, respuestas | instancia de formulario | Aprobación y resultado |

El correo es una simulación local; no hay envío real. Los topics enviarCorreo, registrarVenta y cerrarOportunidad cambian variables y escriben evidencia mediante el worker de prueba.

## Necesarios para la solución completa

| Servicio propuesto | Función |
| --- | --- |
| Registro de leads | Guardar nombre, apellidos, correo, WhatsApp, dirección opcional y una o más mascotas |
| Cupón diario | Generar, consultar y validar el 10% con reglas de uso y vigencia |
| Consulta de clientes/mascotas | Mostrar fichas y cumpleaños próximos |
| Planificador de oportunidades | Detectar cumpleaños a 15 días y evitar duplicados por mascota/año |
| Generación de mensajes | Crear sugerencias personalizadas editables por la dueña |
| Envío de correo | Enviar solo después de la aprobación y registrar resultado de entrega |
| Estados de oportunidad | Mantener PENDIENTE, CONCRETADA o NO_CONCRETADA sin alterar el estado de cliente |
| Redes sociales | Respuesta inicial y enlace al formulario en Instagram, WhatsApp y Facebook, sujeto a sus APIs/permisos |

Prioridad funcional: cumpleaños de la mascota. Navidad y días del gato/perro pueden añadirse después.
