#!/usr/bin/env python3
"""Panel local, registro compartido y bandeja de tareas de Flowable 7.2."""
import base64
import json
import os
os.environ.pop("SSLKEYLOGFILE", None)
import socket
import sqlite3
import sys
import urllib.error
import urllib.request
from datetime import date, datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import unquote, urlencode, urlparse

import google_forms
import negocio

HTML = Path(__file__).with_name("index.html")
FLOWABLE = os.getenv("FLOWABLE_BASE", "http://127.0.0.1:8080/flowable-rest").rstrip("/")
AUTH = base64.b64encode((os.getenv("FLOWABLE_USER", "rest-admin") + ":" +
                         os.getenv("FLOWABLE_PASSWORD", "test")).encode()).decode()


def flowable(path, data=None):
    payload = json.dumps(data).encode() if data is not None else None
    headers = {"Authorization": "Basic " + AUTH}
    if payload is not None:
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(FLOWABLE + "/service" + path, data=payload, headers=headers)
    with urllib.request.urlopen(req, timeout=20) as response:
        raw = response.read()
        return json.loads(raw) if raw else None


def variable(name, value):
    return {"name": name, "value": value if isinstance(value, bool) else str(value),
            "type": "boolean" if isinstance(value, bool) else "string"}


def start_lead(data, deduplicate=False):
    required = ("id", "nombre", "wsp", "mascota", "tipoMascota", "cumple")
    if any(not isinstance(data.get(k), str) or not data[k].strip() for k in required):
        raise ValueError("Completa nombre, WhatsApp y los datos de la mascota")
    date.fromisoformat(data["cumple"])
    if deduplicate:
        # Una respuesta ya iniciada sigue identificable aunque el panel no haya guardado el cursor.
        query = urlencode({"businessKey": data["id"], "processDefinitionKey": "gestionLeads", "size": 1})
        for path in ("/runtime/process-instances?", "/history/historic-process-instances?"):
            previous = flowable(path + query)["data"]
            if previous:
                return previous[0]["id"], False
    fields = required + ("email", "canal", "motivo")
    result = flowable("/runtime/process-instances", {
        "processDefinitionKey": "gestionLeads", "businessKey": data["id"],
        "variables": [variable(k, data.get(k, "")) for k in fields]})
    return result["id"], True


def sale_details(sale):
    if not isinstance(sale, dict):
        raise ValueError("Venta inválida")
    producto = sale.get("producto", "")
    monto = sale.get("monto")
    if (not isinstance(producto, str) or not producto.strip() or
            type(monto) is not int or not 0 <= monto <= 9_007_199_254_740_991):
        raise ValueError("Indica el producto y un monto entero en pesos")
    return {"producto": producto.strip(), "monto": monto, "cupon": sale.get("cupon") is True}


class Handler(BaseHTTPRequestHandler):
    def reply(self, code, body, kind="application/json; charset=utf-8"):
        raw = body if isinstance(body, bytes) else json.dumps(body, ensure_ascii=False).encode()
        self.send_response(code)
        self.send_header("Content-Type", kind)
        self.send_header("Content-Length", str(len(raw)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(raw)

    def body(self):
        size = int(self.headers.get("Content-Length", "0"))
        if size > 1_000_000:
            raise ValueError("Datos demasiado grandes")
        return json.loads(self.rfile.read(size)) if size else {}

    def fail(self, error):
        if isinstance(error, urllib.error.HTTPError):
            print(f"Flowable respondió HTTP {error.code} durante {self.command}.", file=sys.stderr)
            if error.code == 409:
                self.reply(409, {"error": "La tarea ya cambió. Actualiza la bandeja y revisa su estado."})
            else:
                self.reply(502, {"error": "Flowable rechazó la operación. Revisa el motor y el despliegue."})
        elif isinstance(error, (urllib.error.URLError, TimeoutError)):
            self.reply(503, {"error": "Flowable REST no responde. Revisa que el motor esté iniciado."})
        elif isinstance(error, google_forms.SyncError):
            self.reply(503, {"error": str(error)})
        elif isinstance(error, sqlite3.Error):
            print(f"Error de base de datos: {type(error).__name__}", file=sys.stderr)
            self.reply(503, {"error": "No se pudo acceder a los datos de negocio. Revisa la base e inténtalo de nuevo."})
        elif isinstance(error, (ValueError, KeyError)):
            self.reply(400, {"error": str(error)})
        else:
            print(f"Error del panel: {type(error).__name__}", file=sys.stderr)
            self.reply(500, {"error": "Ocurrió un error en el panel. Revisa la consola del servidor."})

    def do_GET(self):
        path = urlparse(self.path).path
        try:
            if path == "/":
                self.reply(200, HTML.read_bytes(), "text/html; charset=utf-8")
            elif path == "/api/state":
                self.reply(200, negocio.read_state())
            elif path == "/api/google-forms":
                self.reply(200, google_forms.public_config())
            elif path == "/api/health":
                self.reply(200, {"flowable": "ok", "desplegados": flowable("/repository/process-definitions?size=1")["total"]})
            elif path == "/api/tasks":
                # La bandeja muestra las tareas activas de estos dos procesos y sus variables.
                result = flowable("/runtime/tasks?size=100")
                tasks = []
                for task in result["data"]:
                    process = task["processDefinitionId"].split(":")[0]
                    if process not in ("gestionLeads", "oportunidadesFechas"):
                        continue
                    values = flowable(f"/runtime/process-instances/{task['processInstanceId']}/variables")
                    tasks.append({"id": task["id"], "name": task["name"], "step": task["taskDefinitionKey"],
                                  "process": process, "processInstanceId": task["processInstanceId"],
                                  "variables": {v["name"]: v.get("value") for v in values}})
                self.reply(200, {"tasks": tasks})
            elif path.startswith("/api/history/"):
                self.reply(200, flowable("/history/historic-process-instances/" + path.removeprefix("/api/history/")))
            else:
                self.reply(404, {"error": "Ruta no encontrada"})
        except Exception as error:
            self.fail(error)

    def do_DELETE(self):
        path = urlparse(self.path).path
        try:
            if path == "/api/example-clients":
                negocio.delete_examples()
            elif path.startswith("/api/clients/"):
                negocio.delete_client(unquote(path.removeprefix("/api/clients/")))
            elif path.startswith("/api/events/"):
                negocio.delete_event(unquote(path.removeprefix("/api/events/")))
            else:
                return self.reply(404, {"error": "Ruta no encontrada"})
            self.reply(200, {"ok": True})
        except Exception as error:
            self.fail(error)

    def do_POST(self):
        path = urlparse(self.path).path
        try:
            data = self.body()
            if path == "/api/google-forms/sync":
                self.reply(200, google_forms.synchronize(start_lead))
            elif path == "/api/clients/upsert":
                if not data.get("id"):
                    raise ValueError("Falta id")
                negocio.create_client(data)
                self.reply(200, {"ok": True})
            elif path.startswith("/api/clients/") and path.endswith("/profile"):
                client_id = unquote(path[len("/api/clients/"):-len("/profile")])
                self.reply(200, negocio.patch_client(client_id, data, fields=negocio.PROFILE))
            elif path.startswith("/api/clients/") and path.endswith("/state"):
                client_id = unquote(path[len("/api/clients/"):-len("/state")])
                sale = None
                if "venta" in data:
                    if data.get("estado") != "CLIENTE" or not data.get("instancia"):
                        raise ValueError("La venta requiere una instancia y el estado CLIENTE")
                    sale = {**sale_details(data["venta"]), "fecha": data["actividad"]}
                self.reply(200, negocio.patch_client(client_id, data, sale=sale, origin=data.get("instancia")))
            elif path == "/api/opportunities":
                instance, client_id = data.get("instancia"), data.get("cliente_id")
                if not instance or not client_id or not data.get("actividad") or not data.get("motivo"):
                    raise ValueError("Faltan los datos de la oportunidad")
                if data.get("estado") not in ("PENDIENTE", "CONCRETADA", "NO_CONCRETADA"):
                    raise ValueError("Estado de oportunidad inválido")
                sale = None
                if data["estado"] == "CONCRETADA":
                    sale = {**sale_details(data.get("venta")), "fecha": data["actividad"]}
                negocio.save_opportunity(instance, client_id, data, sale)
                self.reply(200, {"ok": True})
            elif path == "/api/events":
                negocio.create_event(data)
                self.reply(201, {"ok": True})
            elif path == "/api/lead/start":
                # El formulario inicia Gestión de Leads. El worker registra la ficha en una tarea posterior.
                self.reply(201, {"id": start_lead(data)[0]})
            elif path == "/api/start":
                required = ("nombreCliente", "nombreMascota", "tipoMascota", "fechaEvento", "correoCliente")
                if any(not isinstance(data.get(k), str) or not data[k].strip() for k in required):
                    raise ValueError("Completa cliente, mascota, fecha y correo")
                if data.get("clientId") and not negocio.is_customer(data["clientId"]):
                    raise ValueError("Las campañas están disponibles para clientes con compra previa")
                date.fromisoformat(data["fechaEvento"])
                key = "fecha-" + datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S%f")
                fields = required + ("evento", "clientId", "asunto", "mensajePropuesto")
                result = flowable("/runtime/process-instances", {
                    "message": "oportunidadDetectada", "businessKey": key,
                    "variables": [variable(k, data.get(k, "")) for k in fields]})
                self.reply(201, {"id": result["id"]})
            elif path.startswith("/api/tasks/"):
                # La decisión de la dueña se convierte en variables que el BPMN usa para elegir la siguiente ruta.
                task_id = path.removeprefix("/api/tasks/")
                task = flowable("/runtime/tasks/" + task_id)
                step = task["taskDefinitionKey"]
                if step == "approve":
                    approved = data.get("aprobado") is True
                    variables = [variable("aprobado", approved)]
                    if approved:
                        if not data.get("destinatario") or not data.get("mensajeFinal"):
                            raise ValueError("Completa destinatario y mensaje")
                        variables += [variable("destinatario", data["destinatario"]),
                                      variable("mensajeFinal", data["mensajeFinal"])]
                elif step == "follow":
                    if data.get("resultado") not in ("COMPRA", "NO_CONCRETADA"):
                        raise ValueError("Selecciona compra o no concretada")
                    variables = [variable("resultado", data["resultado"])]
                    if data["resultado"] == "COMPRA":
                        variables.append(variable("detalleVenta", json.dumps(sale_details(data.get("venta")))))
                else:
                    raise ValueError("Tarea no reconocida")
                flowable("/runtime/tasks/" + task_id, {"action": "complete", "variables": variables})
                self.reply(200, {"ok": True})
            else:
                self.reply(404, {"error": "Ruta no encontrada"})
        except Exception as error:
            self.fail(error)


class PanelServer(ThreadingHTTPServer):
    allow_reuse_address = False

    def server_bind(self):
        if hasattr(socket, "SO_EXCLUSIVEADDRUSE"):
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_EXCLUSIVEADDRUSE, 1)
        super().server_bind()


if __name__ == "__main__":
    negocio.initialize()
    port = int(os.getenv("PELUDITOS_UI_PORT", "8092"))
    host = os.getenv("PELUDITOS_UI_HOST", "127.0.0.1")
    server = PanelServer((host, port), Handler)
    print(f"Panel: http://{host}:{port}", flush=True)
    server.serve_forever()
