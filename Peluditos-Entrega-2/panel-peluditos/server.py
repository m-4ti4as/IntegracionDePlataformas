#!/usr/bin/env python3
"""Panel local, registro compartido y bandeja de tareas de Flowable 7.2."""
import base64
import json
import os
os.environ.pop("SSLKEYLOGFILE", None)
import socket
import urllib.error
import urllib.request
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import unquote, urlparse

import negocio

HTML = Path(__file__).with_name("index.html")
FLOWABLE = os.getenv("FLOWABLE_BASE", "http://127.0.0.1:8080/flowable-rest")
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
            self.reply(error.code, {"error": error.read().decode("utf-8", "replace")})
        elif isinstance(error, urllib.error.URLError):
            self.reply(503, {"error": "Flowable REST no responde en el puerto 8080."})
        elif isinstance(error, (ValueError, KeyError)):
            self.reply(400, {"error": str(error)})
        else:
            self.reply(500, {"error": str(error)})

    def do_GET(self):
        path = urlparse(self.path).path
        try:
            if path == "/":
                self.reply(200, HTML.read_bytes(), "text/html; charset=utf-8")
            elif path == "/api/state":
                self.reply(200, negocio.read_state())
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
            if path == "/api/clients/upsert":
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
            elif path == "/api/events":
                negocio.create_event(data)
                self.reply(201, {"ok": True})
            elif path == "/api/lead/start":
                # El formulario inicia Gestión de Leads. El worker registra la ficha en una tarea posterior.
                required = ("id", "nombre", "wsp", "mascota", "tipoMascota", "cumple")
                if any(not str(data.get(k, "")).strip() for k in required):
                    raise ValueError("Completa nombre, WhatsApp y los datos de la mascota")
                fields = ("id", "nombre", "wsp", "email", "canal", "mascota", "tipoMascota", "cumple", "motivo")
                result = flowable("/runtime/process-instances", {
                    "processDefinitionKey": "gestionLeads", "businessKey": data["id"],
                    "variables": [variable(k, data.get(k, "")) for k in fields]})
                self.reply(201, {"id": result["id"]})
            elif path == "/api/start":
                required = ("nombreCliente", "nombreMascota", "tipoMascota", "fechaEvento", "correoCliente")
                if any(not str(data.get(k, "")).strip() for k in required):
                    raise ValueError("Completa cliente, mascota, fecha y correo")
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
                    if data["resultado"] == "COMPRA" and "venta" in data:
                        variables.append(variable("detalleVenta", json.dumps(sale_details(data["venta"]))))
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
    server = PanelServer(("127.0.0.1", port), Handler)
    print(f"Panel: http://127.0.0.1:{port}", flush=True)
    server.serve_forever()
