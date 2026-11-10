"""External Worker Tasks de los dos procesos en Flowable OSS 7.2."""
import json
import os
os.environ.pop("SSLKEYLOGFILE", None)
import time
from datetime import datetime, timezone
from pathlib import Path

import requests
from requests.auth import HTTPBasicAuth
from flowable.external_worker_client import ExternalWorkerClient

FLOWABLE = os.getenv("FLOWABLE_BASE", "http://127.0.0.1:8080/flowable-rest")
API = os.getenv("PELUDITOS_API", "http://127.0.0.1:8091")
PANEL = os.getenv("PELUDITOS_PANEL", "http://127.0.0.1:8092")
EVIDENCE = Path(__file__).resolve().parents[1] / "evidencias" / "worker.jsonl"


# Java recibe campos de formulario y el panel recibe JSON para actualizar los datos de negocio.
def servicio(path, data):
    response = requests.post(API + path, data=data, timeout=15)
    response.raise_for_status()
    return response.json()


def panel(path, data):
    response = requests.post(PANEL + path, json=data, timeout=15)
    response.raise_for_status()
    return response.json()


# El identificador de la instancia permite seguir el recorrido en worker.jsonl durante la demostración.
def registrar(accion, job, **datos):
    EVIDENCE.parent.mkdir(exist_ok=True)
    evento = {"fechaUtc": datetime.now(timezone.utc).isoformat(),
              "accion": accion, "instancia": job.process_instance_id, **datos}
    with EVIDENCE.open("a", encoding="utf-8") as archivo:
        archivo.write(json.dumps(evento, ensure_ascii=False) + "\n")


def actualizar_compra(client_id, estado, motivo, job, variables):

    cambios = {"estado": estado, "actividad": datetime.now().date().isoformat(), "motivo": motivo}
    # La API usa el identificador de la instancia para evitar duplicar una venta si se reintenta la tarea.
    if variables.get("detalleVenta"):
        venta = json.loads(variables["detalleVenta"])
        cambios.update(venta=venta, instancia=job.process_instance_id,
                       motivo="Compró " + venta["producto"] + ".")
    panel(f"/api/clients/{client_id}/state", cambios)


def procesar(topic):
    # Cada tarea recibe variables del BPMN. Al devolver success(), el cliente oficial informa el resultado a Flowable.
    def callback(job, resultado):
        variables = {variable.name: variable.value for variable in job.variables}
        # En Gestión de Leads, la API del panel guarda la ficha como pendiente en SQLite.
        if topic == "guardarLead":
            client = {
                "id": variables["id"], "nombre": variables["nombre"],
                "wsp": variables["wsp"], "email": variables.get("email", ""),
                "canal": variables.get("canal", ""), "mascota": variables["mascota"],
                "tipoMascota": variables["tipoMascota"], "cumple": variables["cumple"],
                "estado": "PENDIENTE", "cupon": "",
                "motivo": variables.get("motivo") or "Formulario recibido. Falta contactar.",
                "actividad": datetime.now().date().isoformat(), "ventas": []
            }
            panel("/api/clients/upsert", client)
            registrar("lead-guardado", job, cliente=client["id"])
            return resultado.success().variable_string("estadoLead", "PENDIENTE")

        # El servicio Java genera el cupón y simula el envío solo si hay una dirección de correo.
        if topic == "enviarCupon":
            client_id = variables["id"]
            codigo = servicio("/api/cupon", {"clienteId": client_id})["codigo"]
            correo = variables.get("email", "")
            if correo:
                servicio("/api/envio", {"destinatario": correo,
                                         "mensaje": "Tu cupón de 10% es " + codigo})
            panel(f"/api/clients/{client_id}/state", {
                "cupon": codigo, "motivo": "Cupón 10% " + codigo +
                (" enviado (simulación)." if correo else " generado; sin correo para envío.")})
            registrar("cupon-simulado", job, cliente=client_id, correo=correo, codigo=codigo)
            return resultado.success().variable_string("cupon", codigo)

        # El tema corresponde a la rama que eligió el BPMN tras la decisión de compra o no compra.
        if topic in ("registrarCompra", "cerrarLead"):
            client_id = variables["id"]
            outcome = "COMPRA" if topic == "registrarCompra" else "NO_CONCRETADA"
            estado = servicio("/api/estado", {"resultado": outcome})["estado"]
            if outcome == "COMPRA":
                actualizar_compra(client_id, estado, "Compra registrada.", job, variables)
            else:
                panel(f"/api/clients/{client_id}/state", {
                    "estado": estado, "actividad": datetime.now().date().isoformat(),
                    "motivo": "Seguimiento cerrado sin compra."})
            registrar("lead-resuelto", job, cliente=client_id, estado=estado)
            return resultado.success().variable_string("estadoLead", estado)

        # El mensaje de Java vuelve al BPMN como mensajeSugerido para la revisión humana.
        if topic == "generarSugerencia":
            respuesta = requests.post(API + "/api/sugerencia", data={
                "nombre": variables.get("nombreCliente", "cliente"),
                "mascota": variables.get("nombreMascota", "tu mascota"),
                "tipo": variables.get("tipoMascota", "mascota"),
                "evento": variables.get("evento", "CUMPLEANOS"),
            }, timeout=15)
            respuesta.raise_for_status()
            mensaje = respuesta.json()["mensaje"]
            registrar("sugerencia", job, mensaje=mensaje)
            return resultado.success().variable_string("mensajeSugerido", mensaje)

        # Tras la aprobación humana, se simula el envío y la oportunidad pasa a seguimiento.
        if topic == "enviarCorreo":
            destinatario = variables.get("destinatario")
            mensaje = variables.get("mensajeFinal")
            if not destinatario or not mensaje:
                raise ValueError("Faltan destinatario o mensajeFinal")
            servicio("/api/envio", {"destinatario": destinatario, "mensaje": mensaje})
            client_id = variables.get("clientId", "")
            if client_id:
                panel(f"/api/clients/{client_id}/state", {
                    "estado": "PENDIENTE", "actividad": datetime.now().date().isoformat(),
                    "motivo": "Correo de oportunidad enviado (simulación). Falta conversar."})
            registrar("correo-simulado", job, destinatario=destinatario, mensaje=mensaje)
            return (resultado.success().variable_boolean("correoEnviado", True)
                    .variable_string("estadoOportunidad", "PENDIENTE"))

        # Estas dos ramas cierran la oportunidad y actualizan la ficha vinculada, si existe.
        if topic == "registrarVenta":
            client_id = variables.get("clientId", "")
            estado = servicio("/api/estado", {"resultado": "COMPRA"})["estado"]
            if client_id:
                actualizar_compra(client_id, estado, "Venta de oportunidad registrada.", job, variables)
            registrar("venta-concretada", job)
            return resultado.success().variable_string("estadoOportunidad", "CONCRETADA")

        if topic == "cerrarOportunidad":
            client_id = variables.get("clientId", "")
            estado = servicio("/api/estado", {"resultado": "NO_CONCRETADA"})["estado"]
            if client_id:
                panel(f"/api/clients/{client_id}/state", {
                    "estado": estado, "actividad": datetime.now().date().isoformat(),
                    "motivo": "Oportunidad cerrada sin compra."})
            registrar("no-concretada", job)
            return resultado.success().variable_string("estadoOportunidad", "NO_CONCRETADA")

        raise ValueError("Tema desconocido: " + topic)
    return callback


def main():
    cliente = ExternalWorkerClient(
        FLOWABLE, worker_id="peluditos-worker",
        auth=HTTPBasicAuth(os.getenv("FLOWABLE_USER", "rest-admin"),
                           os.getenv("FLOWABLE_PASSWORD", "test")))
    # Los temas deben coincidir con los configurados en los BPMN para que el worker encuentre las tareas.
    for topic in ("guardarLead", "enviarCupon", "registrarCompra", "cerrarLead",
                  "generarSugerencia", "enviarCorreo", "registrarVenta", "cerrarOportunidad"):
        cliente.subscribe(topic, procesar(topic), wait_period_seconds=2)
        print("Suscrito a", topic, flush=True)
    while True:
        time.sleep(60)


if __name__ == "__main__":
    main()
