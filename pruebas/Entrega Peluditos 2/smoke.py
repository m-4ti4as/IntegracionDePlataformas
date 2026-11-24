"""Prueba de extremo a extremo con Flowable, panel, Java y worker ya iniciados."""
import os
os.environ.pop("SSLKEYLOGFILE", None)
import time
import uuid
import requests

BASE = os.getenv("PELUDITOS_PANEL", "http://127.0.0.1:8092")
JAVA = os.getenv("PELUDITOS_API", "http://127.0.0.1:8091")
SESSION = requests.Session()
SESSION.trust_env = False


def call(method, path, **kwargs):
    response = SESSION.request(method, BASE + path, timeout=20, **kwargs)
    response.raise_for_status()
    return response.json()


def wait_task(process, step, client_id, timeout=45):
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        tasks = call("GET", "/api/tasks")["tasks"]
        for task in tasks:
            if (task["process"] == process and task["step"] == step and
                    (task["variables"].get("id") == client_id or task["variables"].get("clientId") == client_id)):
                return task
        time.sleep(1)
    raise AssertionError(f"No apareció la tarea {process}/{step}")


def wait_state(client_id, expected, timeout=45):
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        clients = call("GET", "/api/state")["clientes"]
        client = next((c for c in clients if c["id"] == client_id), None)
        if client and client["estado"] == expected:
            return client
        time.sleep(1)
    raise AssertionError(f"El cliente {client_id} no llegó a {expected}")


assert call("GET", "/api/health")["flowable"] == "ok"
for endpoint, data in (
    ("/health", None),
    ("/api/sugerencia", {"nombre": "Ana", "mascota": "Luna", "tipo": "Perro", "evento": "CUMPLEANOS"}),
    ("/api/cupon", {"clienteId": "prueba123"}),
    ("/api/estado", {"resultado": "COMPRA"}),
    ("/api/envio", {"destinatario": "demo@example.com", "mensaje": "Prueba"}),
):
    response = SESSION.get(JAVA + endpoint, timeout=10) if data is None else SESSION.post(JAVA + endpoint, data=data, timeout=10)
    response.raise_for_status()
    assert response.json()
print("Servicios Jakarta REST: OK")

for result, expected in (("COMPRA", "CLIENTE"), ("NO_CONCRETADA", "NO CONCRETADO")):
    client_id = uuid.uuid4().hex[:12]
    lead = {"id": client_id, "nombre": "Prueba " + result, "wsp": "+56912345678",
            "email": "prueba@example.com", "canal": "Instagram", "mascota": "Luna",
            "tipoMascota": "Perro", "cumple": "2022-11-21", "motivo": "Prueba automatizada"}
    instance = call("POST", "/api/lead/start", json=lead)["id"]
    task = wait_task("gestionLeads", "follow", client_id)
    assert wait_state(client_id, "PENDIENTE")["cupon"]
    datos = {"resultado": result}
    if result == "COMPRA":
        datos["venta"] = {"producto": "Torta de prueba", "monto": 14990, "cupon": True}
    call("POST", "/api/tasks/" + task["id"], json=datos)
    cliente = wait_state(client_id, expected)
    if result == "COMPRA":
        assert len(cliente["ventas"]) == 1
        assert cliente["ventas"][0]["monto"] == 14990
        assert cliente["ventas"][0]["cupon"] is True
    deadline = time.monotonic() + 30
    while time.monotonic() < deadline:
        history = call("GET", "/api/history/" + instance)
        if history.get("endTime"):
            break
        time.sleep(1)
    assert history.get("endTime"), "El proceso de leads no terminó"
    print("Gestión de Leads:", result, "OK")
    if result == "COMPRA":
        sale_client = lead

instance = call("POST", "/api/start", json={
    "clientId": sale_client["id"], "nombreCliente": sale_client["nombre"],
    "correoCliente": sale_client["email"], "nombreMascota": sale_client["mascota"],
    "tipoMascota": sale_client["tipoMascota"], "fechaEvento": sale_client["cumple"],
    "evento": "CUMPLEANOS", "asunto": "Cumpleaños", "mensajePropuesto": "Feliz cumpleaños, Luna."
})["id"]
task = wait_task("oportunidadesFechas", "approve", sale_client["id"])
assert task["variables"].get("mensajeSugerido")
call("POST", "/api/tasks/" + task["id"], json={
    "aprobado": True, "destinatario": sale_client["email"], "mensajeFinal": "Feliz cumpleaños, Luna."})
task = wait_task("oportunidadesFechas", "follow", sale_client["id"])
assert wait_state(sale_client["id"], "PENDIENTE")
call("POST", "/api/tasks/" + task["id"], json={"resultado": "COMPRA"})
assert wait_state(sale_client["id"], "CLIENTE")
deadline = time.monotonic() + 30
while time.monotonic() < deadline:
    history = call("GET", "/api/history/" + instance)
    if history.get("endTime"):
        break
    time.sleep(1)
assert history.get("endTime"), "El proceso de oportunidad no terminó"
print("Oportunidad de cumpleaños: OK")
print("Prueba completa: OK")
