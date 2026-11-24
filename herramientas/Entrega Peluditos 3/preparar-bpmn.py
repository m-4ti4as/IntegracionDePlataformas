"""Empaqueta los dos BPMN ejecutables para desplegarlos en Flowable."""
import argparse
import os
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

def empaquetar():
    proyecto = Path(__file__).resolve().parents[1]
    modelos = proyecto / "BPMN"
    destino = proyecto / ".runtime" / "despliegue-proceso-720.bar"
    destino.parent.mkdir(exist_ok=True)
    with ZipFile(destino, "w", compression=ZIP_DEFLATED) as paquete:
        for nombre in ("gestion-leads.bpmn", "oportunidades-fechas.bpmn"):
            paquete.write(modelos / nombre, arcname=nombre)
    return destino


def desplegar(archivo):
    import requests

    base = os.getenv("FLOWABLE_BASE", "http://127.0.0.1:8080/flowable-rest").rstrip("/")
    auth = (os.getenv("FLOWABLE_USER", "rest-admin"), os.getenv("FLOWABLE_PASSWORD", "test"))
    try:
        with archivo.open("rb") as paquete:
            respuesta = requests.post(base + "/service/repository/deployments", auth=auth,
                                       files={"file": (archivo.name, paquete)}, timeout=30)
            respuesta.raise_for_status()
    except requests.RequestException as error:
        raise SystemExit(f"No se pudieron desplegar los BPMN en {base}. Revisa Flowable y las credenciales.") from error
    print("Procesos desplegados en Flowable 7.2.")


if __name__ == "__main__":
    argumentos = argparse.ArgumentParser()
    argumentos.add_argument("--desplegar", action="store_true")
    archivo = empaquetar()
    if argumentos.parse_args().desplegar:
        desplegar(archivo)
