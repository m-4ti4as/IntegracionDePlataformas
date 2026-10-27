#!/usr/bin/env python3
"""Worker externo de Flowable 6.8.1 para el BPMN de cumpleaños."""
# Importa el lector de argumentos de la línea de comandos.
import argparse
# Importa la codificación necesaria para la autenticación Basic.
import base64
# Importa las funciones para leer y escribir JSON.
import json
# Importa el acceso a variables de entorno.
import os
# Importa la pausa entre consultas al motor.
import time
# Importa herramientas para codificar campos de formulario.
import urllib.parse
# Importa el cliente HTTP incluido en Python.
import urllib.request
# Importa fechas y la zona horaria UTC para las evidencias.
from datetime import datetime, timezone
# Importa rutas de archivos independientes del sistema operativo.
from pathlib import Path

# Lee la dirección de Flowable o utiliza la instalación local por defecto.
FLOWABLE = os.getenv("FLOWABLE_BASE", "http://127.0.0.1:8080/flowable-rest")
# Lee la dirección del servicio Java o utiliza su puerto local.
API = os.getenv("PELUDITOS_API", "http://127.0.0.1:8091")
# Lee el usuario de la API de Flowable.
USER = os.getenv("FLOWABLE_USER", "rest-admin")
# Lee la contraseña de la API de Flowable.
PASSWORD = os.getenv("FLOWABLE_PASSWORD", "test")
# Identifica a este programa cuando adquiere trabajos externos.
WORKER_ID = "peluditos-worker"
# Enumera los cuatro temas BPMN que puede ejecutar el worker.
TOPICS = ("generarSugerencia", "enviarCorreo", "registrarVenta", "cerrarOportunidad")
# Calcula la ruta donde se guardarán las evidencias de ejecución.
EVIDENCE = Path(__file__).resolve().parents[1] / "evidencias" / "worker-eventos.jsonl"


# Define una función para hacer solicitudes HTTP y recibir respuestas JSON.
def request_json(url, data=None, authenticated=False, form=False):
    # Comienza con un conjunto vacío de encabezados HTTP.
    headers = {}
    # Comprueba si la API requiere autenticación.
    if authenticated:
        # Codifica usuario y contraseña para el esquema Basic.
        token = base64.b64encode(f"{USER}:{PASSWORD}".encode()).decode()
        # Agrega el encabezado Authorization a la solicitud.
        headers["Authorization"] = f"Basic {token}"
    # Comprueba si la solicitud no lleva datos en el cuerpo.
    if data is None:
        # Deja vacío el cuerpo cuando no hay datos.
        payload = None
    # Elige el formato de formulario si se solicitó expresamente.
    elif form:
        # Codifica los campos del formulario en bytes.
        payload = urllib.parse.urlencode(data).encode()
        # Informa al servidor que los datos son de formulario.
        headers["Content-Type"] = "application/x-www-form-urlencoded"
    # Selecciona JSON para cualquier otro cuerpo de solicitud.
    else:
        # Convierte los datos a JSON y luego a bytes.
        payload = json.dumps(data).encode()
        # Informa al servidor que el cuerpo contiene JSON.
        headers["Content-Type"] = "application/json"
    # Construye la solicitud con URL, cuerpo y encabezados.
    request = urllib.request.Request(url, data=payload, headers=headers)
    # Abre la conexión HTTP con un límite de espera de 15 segundos.
    with urllib.request.urlopen(request, timeout=15) as response:
        # Lee todos los bytes devueltos por el servidor.
        raw = response.read()
        # Interpreta la respuesta como JSON o devuelve None si vino vacía.
        return json.loads(raw) if raw else None


# Define una función para guardar un evento como evidencia.
def log_event(event):
    # Crea la carpeta de evidencias si todavía no existe.
    EVIDENCE.parent.mkdir(parents=True, exist_ok=True)
    # Agrega al evento la fecha y hora actual en UTC.
    event["fechaUtc"] = datetime.now(timezone.utc).isoformat()
    # Abre el archivo de eventos para agregar una línea sin borrar las anteriores.
    with EVIDENCE.open("a", encoding="utf-8") as output:
        # Escribe el evento como una línea JSON que conserva tildes.
        output.write(json.dumps(event, ensure_ascii=False) + "\n")


# Define el formato de una variable que se devolverá a Flowable.
def variable(name, value):
    # Distingue las variables booleanas de las variables de texto.
    kind = "boolean" if isinstance(value, bool) else "string"
    # Devuelve nombre, tipo y valor según la estructura esperada por Flowable.
    return {"name": name, "type": kind, "value": value}


# Define cómo se ejecuta un trabajo externo según su tema BPMN.
def execute(topic, job):
    # Convierte la lista de variables del trabajo en un diccionario por nombre.
    values = {item["name"]: item.get("value") for item in job.get("variables", [])}
    # Prepara una lista vacía para las variables que se devolverán a Flowable.
    result = []
    # Selecciona el trabajo que debe generar una sugerencia.
    if topic == "generarSugerencia":
        # Empieza una solicitud al servicio Java de sugerencias.
        response = request_json(API + "/api/sugerencia", {
            # Envía el nombre del cliente o un valor general.
            "nombre": values.get("nombreCliente", "cliente"),
            # Envía el nombre de la mascota o un valor general.
            "mascota": values.get("nombreMascota", "tu mascota"),
            # Envía el tipo de mascota o un valor general.
            "tipo": values.get("tipoMascota", "mascota"),
            # Envía el nombre del evento o asume cumpleaños.
            "evento": values.get("evento", "CUMPLEANOS")
        # Cierra los datos y los envía con formato de formulario.
        }, form=True)
        # Guarda el mensaje recibido como variable BPMN mensajeSugerido.
        result = [variable("mensajeSugerido", response["mensaje"])]
        # Comienza a registrar evidencia de la llamada al servicio Java.
        log_event({"accion": "sugerencia", "instancia": job.get("processInstanceId"),
                   # Guarda la dirección del servicio y el mensaje que este devolvió.
                   "servicioJava": API + "/api/sugerencia", "mensaje": response["mensaje"]})
    # Selecciona el trabajo encargado del envío de correo de prueba.
    elif topic == "enviarCorreo":
        # Obtiene el destinatario definido en el proceso.
        recipient = values.get("destinatario", "")
        # Obtiene el mensaje final aprobado por la dueña.
        message = values.get("mensajeFinal", "")
        # Comprueba si falta el destinatario o el mensaje.
        if not recipient or not message:
            # Produce un error para evitar marcar como enviado un mensaje incompleto.
            raise ValueError("Faltan destinatario o mensajeFinal")
        # Semana 3: se registra el envío simulado, sin enviar un correo real.
        # Comienza el registro del envío simulado como evidencia.
        log_event({"accion": "correo-simulado", "instancia": job.get("processInstanceId"),
                   # Guarda el destinatario y el contenido del mensaje simulado.
                   "destinatario": recipient, "mensaje": message})
        # Indica en Flowable que el correo de prueba fue enviado.
        result = [variable("correoEnviado", True),
                  # Deja esta oportunidad de venta en estado PENDIENTE.
                  variable("estadoOportunidad", "PENDIENTE")]
    # Selecciona el trabajo que registra una venta concretada.
    elif topic == "registrarVenta":
        # Registra como evidencia la venta de esta instancia.
        log_event({"accion": "venta-concretada", "instancia": job.get("processInstanceId")})
        # Marca la oportunidad como CONCRETADA en Flowable.
        result = [variable("estadoOportunidad", "CONCRETADA")]
    # Selecciona el trabajo que cierra una oportunidad sin venta.
    elif topic == "cerrarOportunidad":
        # Registra como evidencia el cierre de esta instancia.
        log_event({"accion": "no-concretada", "instancia": job.get("processInstanceId")})
        # Marca la oportunidad como NO_CONCRETADA en Flowable.
        result = [variable("estadoOportunidad", "NO_CONCRETADA")]
    # Abre el caso para un tema que el worker no reconoce.
    else:
        # Produce un error con el nombre del tema desconocido.
        raise ValueError(f"Tópico desconocido: {topic}")

    # Llama a la API de Flowable para completar el trabajo adquirido.
    request_json(FLOWABLE + f"/external-job-api/acquire/jobs/{job['id']}/complete",
                 # Envía el identificador del worker y las variables resultantes.
                 {"workerId": WORKER_ID, "variables": result}, authenticated=True)
    # Informa en consola qué tema e instancia se completaron.
    print(f"Completado {topic}, instancia {job.get('processInstanceId')}", flush=True)


# Define una pasada de consulta por todos los temas conocidos.
def cycle():
    # Inicia en cero el contador de trabajos completados.
    done = 0
    # Recorre los temas que este worker puede atender.
    for topic in TOPICS:
        # Solicita a Flowable trabajos pendientes para el tema actual.
        jobs = request_json(FLOWABLE + "/external-job-api/acquire/jobs", {
            # Indica el tema BPMN que se desea adquirir.
            "topic": topic,
            # Pide bloquear los trabajos durante diez minutos.
            "lockDuration": "PT10M",
            # Indica qué worker adquiere los trabajos.
            "workerId": WORKER_ID,
            # Solicita como máximo cinco trabajos por llamada.
            "numberOfTasks": 5
        # Termina la solicitud autenticada de adquisición.
        }, authenticated=True)
        # Recorre cada trabajo devuelto por Flowable.
        for job in jobs:
            # Ejecuta la lógica correspondiente al tema del trabajo.
            execute(topic, job)
            # Aumenta el contador de trabajos completados.
            done += 1
    # Devuelve cuántos trabajos procesó esta pasada.
    return done


# Define la función principal del programa.
def main():
    # Crea el lector de opciones de línea de comandos.
    parser = argparse.ArgumentParser()
    # Permite activar consultas continuas con la opción --watch.
    parser.add_argument("--watch", action="store_true", help="Sondear continuamente")
    # Lee las opciones usadas al iniciar el programa.
    args = parser.parse_args()
    # Repite las consultas hasta que se ordene una sola pasada.
    while True:
        # Ejecuta una consulta de todos los temas y cuenta sus trabajos.
        count = cycle()
        # Comprueba si se solicitó una sola pasada en vez de vigilancia continua.
        if not args.watch:
            # Muestra cuántos trabajos se procesaron en esa pasada.
            print(f"Ciclo terminado: {count} tarea(s) externa(s).")
            # Termina el programa después de la única pasada solicitada.
            return
        # Comprueba si en esta pasada no había trabajos disponibles.
        if count == 0:
            # Espera dos segundos antes de volver a consultar a Flowable.
            time.sleep(2)


# Ejecuta el bloque siguiente solo cuando se inicia este archivo directamente.
if __name__ == "__main__":
    # Llama a la función principal del worker.
    main()

