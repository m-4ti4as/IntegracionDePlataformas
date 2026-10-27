#!/usr/bin/env python3
"""Pantalla local que presenta y completa tareas reales de Flowable OSS."""
import base64
import json
import os
import socket
import urllib.error
import urllib.request
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

FLOWABLE = os.getenv("FLOWABLE_BASE", "http://127.0.0.1:8080/flowable-rest")
USER = os.getenv("FLOWABLE_USER", "rest-admin")
PASSWORD = os.getenv("FLOWABLE_PASSWORD", "test")
HTML = Path(__file__).with_name("index.html")


def flowable(path, data=None):
    payload = json.dumps(data).encode("utf-8") if data is not None else None
    token = base64.b64encode(f"{USER}:{PASSWORD}".encode()).decode()
    headers = {"Authorization": f"Basic {token}"}
    if payload is not None:
        headers["Content-Type"] = "application/json"
    request = urllib.request.Request(FLOWABLE + "/service" + path, data=payload, headers=headers)
    with urllib.request.urlopen(request, timeout=15) as response:
        raw = response.read()
        return json.loads(raw) if raw else None


def form_api(path, data):
    token = base64.b64encode(f"{USER}:{PASSWORD}".encode()).decode()
    headers = {"Authorization": f"Basic {token}", "Content-Type": "application/json"}
    request = urllib.request.Request(
        FLOWABLE + "/form-api" + path,
        data=json.dumps(data).encode("utf-8"),
        headers=headers)
    with urllib.request.urlopen(request, timeout=15) as response:
        raw = response.read()
        return json.loads(raw) if raw else None

def var(name, value):
    return {"name": name, "value": value, "type": "boolean" if isinstance(value, bool) else "string"}


class Handler(BaseHTTPRequestHandler):
    def reply(self, status, body, content_type="application/json; charset=utf-8"):
        data = body if isinstance(body, bytes) else json.dumps(body, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(data)

    def read_json(self):
        length = int(self.headers.get("Content-Length", "0"))
        return json.loads(self.rfile.read(length)) if length else {}

    def do_GET(self):
        route = urlparse(self.path).path
        try:
            if route == "/":
                self.reply(200, HTML.read_bytes(), "text/html; charset=utf-8")
            elif route == "/api/tasks":
                result = flowable("/runtime/tasks?size=100")
                tasks = []
                for task in result["data"]:
                    if task["processDefinitionId"].split(":")[0] != "oportunidadesFechas":
                        continue
                    values = flowable(f"/runtime/process-instances/{task['processInstanceId']}/variables")
                    tasks.append({
                        "id": task["id"], "name": task["name"],
                        "step": task["taskDefinitionKey"],
                        "processInstanceId": task["processInstanceId"],
                        "variables": {item["name"]: item.get("value") for item in values}
                    })
                self.reply(200, {"tasks": tasks})
            elif route.startswith("/api/history/"):
                instance = route.removeprefix("/api/history/")
                result = flowable(f"/history/historic-process-instances/{instance}")
                variables = flowable(f"/history/historic-variable-instances?processInstanceId={instance}&size=100")
                self.reply(200, {"instance": result,
                                 "variables": {item["variable"]["name"]: item["variable"].get("value")
                                               for item in variables["data"]}})
            else:
                self.reply(404, {"error": "Ruta no encontrada"})
        except urllib.error.HTTPError as error:
            self.reply(error.code, {"error": error.read().decode("utf-8", "replace")})
        except urllib.error.URLError as error:
            self.reply(503, {"error": f"Flowable REST no responde en {FLOWABLE}. Inicia el motor en el puerto 8080 y vuelve a intentarlo."})
        except Exception as error:
            self.reply(500, {"error": str(error)})

    def do_POST(self):
        route = urlparse(self.path).path
        try:
            data = self.read_json()
            if route == "/api/start":
                required = ("nombreCliente", "nombreMascota", "tipoMascota",
                            "fechaEvento", "correoCliente")
                if any(not str(data.get(key, "")).strip() for key in required):
                    self.reply(400, {"error": "Completa los datos de cliente, mascota, fecha y correo."})
                    return
                key = "cumple-" + datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S%f")
                variables = [var(key, str(data[key]).strip()) for key in required]
                variables.append(var("evento", "CUMPLEANOS"))
                result = flowable("/runtime/process-instances", {
                    "message": "oportunidadDetectada",
                    "businessKey": key,
                    "variables": variables
                })
                self.reply(201, {"id": result["id"]})
            elif route.startswith("/api/tasks/"):
                task_id = route.removeprefix("/api/tasks/")
                step = data.get("step")
                if step == "approve":
                    approved = bool(data.get("aprobado"))
                    if approved and (not data.get("destinatario") or not data.get("mensajeFinal")):
                        self.reply(400, {"error": "Completa destinatario y mensaje."})
                        return
                    variables = [var("aprobado", approved)]
                    if approved:
                        variables += [var("destinatario", str(data["destinatario"]).strip()),
                                      var("mensajeFinal", str(data["mensajeFinal"]).strip())]
                elif step == "follow":
                    result = data.get("resultado")
                    if result not in ("COMPRA", "NO_CONCRETADA"):
                        self.reply(400, {"error": "Selecciona Compra o No concretada."})
                        return
                    variables = [var("resultado", result)]
                else:
                    self.reply(400, {"error": "Paso no reconocido"})
                    return
                task = flowable(f"/runtime/tasks/{task_id}")
                if task["taskDefinitionKey"] != step:
                    self.reply(409, {"error": "La tarea cambió. Actualiza la pantalla."})
                    return
                current = flowable(f"/runtime/process-instances/{task['processInstanceId']}/variables")
                form_values = {item["name"]: item.get("value") for item in current}
                form_values.update({item["name"]: item["value"] for item in variables})
                form_api("/form/form-instances", {
                    "formDefinitionKey": task["formKey"],
                    "taskId": task_id,
                    "processInstanceId": task["processInstanceId"],
                    "processDefinitionId": task["processDefinitionId"],
                    "variables": form_values
                })
                flowable(f"/runtime/tasks/{task_id}", {"action": "complete", "variables": variables})
                self.reply(200, {"ok": True})
            else:
                self.reply(404, {"error": "Ruta no encontrada"})
        except urllib.error.HTTPError as error:
            self.reply(error.code, {"error": error.read().decode("utf-8", "replace")})
        except urllib.error.URLError as error:
            self.reply(503, {"error": f"Flowable REST no responde en {FLOWABLE}. Inicia el motor en el puerto 8080 y vuelve a intentarlo."})
        except Exception as error:
            self.reply(500, {"error": str(error)})


# Impide abrir dos versiones del panel en el mismo puerto en Windows.
class PanelServer(ThreadingHTTPServer):
    allow_reuse_address = False

    def server_bind(self):
        if hasattr(socket, "SO_EXCLUSIVEADDRUSE"):
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_EXCLUSIVEADDRUSE, 1)
        super().server_bind()


if __name__ == "__main__":
    port = int(os.getenv("PELUDITOS_UI_PORT", "8092"))
    try:
        server = PanelServer(("127.0.0.1", port), Handler)
    except OSError as error:
        if getattr(error, "winerror", None) == 10048:
            raise SystemExit(f"El puerto {port} ya está ocupado. Cierra el panel anterior con Ctrl+C y vuelve a iniciar.") from None
        raise
    print(f"Panel de tareas: http://127.0.0.1:{port}", flush=True)
    server.serve_forever()

