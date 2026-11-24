"""Importa respuestas privadas de Google Forms mediante el Apps Script del proyecto."""
import hashlib
import json
import os
import re
from datetime import date
from pathlib import Path
from threading import Lock
from urllib.error import URLError
from urllib.parse import urlparse
from urllib.request import Request, urlopen

import negocio

SYNC_LOCK = Lock()
# La copia privada lleva la conexión del formulario junto al proyecto.
# El paso 08 gestiona PostgreSQL en config.local de forma independiente.
def conexion_formulario():
    campos = ("GOOGLE_FORMS_PUBLIC_URL", "GOOGLE_FORMS_EXEC_URL", "GOOGLE_FORMS_SYNC_KEY")
    archivo = Path(__file__).resolve().parents[1] / "config.local.forms"
    try:
        lineas = archivo.read_text(encoding="utf-8-sig").splitlines()
    except FileNotFoundError:
        return tuple(os.getenv(campo, "").strip() for campo in campos)
    valores = {}
    for linea in lineas:
        nombre, separador, valor = linea.partition("=")
        if separador and nombre.strip() in campos:
            valores[nombre.strip()] = valor.strip()
    return tuple(valores.get(campo, "") for campo in campos)


PUBLIC_URL, EXEC_URL, SYNC_KEY = conexion_formulario()
LIMIT = 30


class SyncError(Exception):
    pass


def valid_url(value, paths, query=False):
    url = urlparse(value)
    return (url.scheme == "https" and url.netloc in paths and
            re.fullmatch(paths[url.netloc], url.path) is not None and
            (query or not url.query) and not url.fragment)


def public_config():
    public = valid_url(PUBLIC_URL, {"docs.google.com": r"/forms/(?:u/\d+/)?(?:d/e|d)/[\w-]+/viewform",
                                    "forms.gle": r"/[\w-]+"}, query=True)
    return {"publicUrl": PUBLIC_URL if public else "", "configured": bool(EXEC_URL and SYNC_KEY)}


def fetch(cursor):
    if not valid_url(EXEC_URL, {"script.google.com": r"/macros/s/[\w-]+/exec"}):
        raise SyncError("Revisa la URL de Apps Script en la configuración del formulario.")
    if len(SYNC_KEY) < 32:
        raise SyncError("La clave de sincronización debe tener al menos 32 caracteres.")
    payload = json.dumps({"clave": SYNC_KEY, "fechaMs": cursor[0], "respuesta": cursor[1],
                          "limite": LIMIT}).encode("utf-8")
    request = Request(EXEC_URL, data=payload, headers={"Content-Type": "application/json"})
    try:
        with urlopen(request, timeout=18) as response:
            batch = json.loads(response.read(1_000_000))
    except (URLError, TimeoutError, ValueError) as error:
        raise SyncError("No se pudieron leer las respuestas. Revisa la conexión y el despliegue de Apps Script.") from error
    if not isinstance(batch, dict) or batch.get("ok") is not True:
        raise SyncError("Apps Script rechazó la sincronización. Revisa la clave y el formulario configurado.")
    return batch


def lead_for(form_id, answer):
    lead = {}
    for field in ("nombre", "wsp", "email", "canal", "tipoMascota", "mascota", "cumple"):
        value = answer.get(field)
        if not isinstance(value, str) or not value.strip() or len(value) > 300:
            raise ValueError("Respuesta incompleta")
        lead[field] = value.strip()
    if not re.fullmatch(r"[^\s@]+@[^\s@]+\.[^\s@]+", lead["email"]):
        raise ValueError("Correo inválido")
    lead["cumple"] = date.fromisoformat(lead["cumple"]).isoformat()
    if lead["tipoMascota"] not in ("Perro", "Gato"):
        raise ValueError("Tipo de mascota inválido")
    lead["id"] = "google-" + hashlib.sha256(f"{form_id}/{answer['id']}".encode()).hexdigest()
    lead["motivo"] = "Registro recibido por Google Forms."
    return lead


def synchronize(start_lead):
    if not EXEC_URL and not SYNC_KEY:
        return {"status": "disabled"}
    if not EXEC_URL or not SYNC_KEY:
        raise SyncError("Completa la URL /exec y la clave de Apps Script en config.local.")
    if not SYNC_LOCK.acquire(blocking=False):
        return {"status": "busy"}
    try:
        source = hashlib.sha256(EXEC_URL.encode()).hexdigest()
        cursor = negocio.google_cursor(source)
        batch = fetch(cursor)
        form_id, answers = batch.get("formId"), batch.get("respuestas")
        if not isinstance(form_id, str) or not form_id or not isinstance(answers, list) or len(answers) > LIMIT:
            raise SyncError("Apps Script no devolvió un lote válido.")
        imported = skipped = 0
        for answer in answers:
            if (not isinstance(answer, dict) or type(answer.get("fechaMs")) is not int or
                    not isinstance(answer.get("id"), str) or not answer["id"]):
                raise SyncError("Apps Script devolvió una respuesta sin identificador o fecha.")
            position = (answer["fechaMs"], answer["id"])
            if position <= cursor:
                continue
            try:
                lead = lead_for(form_id, answer)
            except ValueError:
                skipped += 1
            else:
                # La misma clave también permite recuperar un inicio que Flowable alcanzó a confirmar.
                if start_lead(lead, deduplicate=True)[1]:
                    imported += 1
            negocio.save_google_cursor(source, *position)
            cursor = position
        return {"status": "ok", "imported": imported, "skipped": skipped,
                "more": bool(batch.get("hayMas")) and bool(answers)}
    finally:
        SYNC_LOCK.release()
