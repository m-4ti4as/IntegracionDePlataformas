"""Empaqueta los dos BPMN ejecutables para desplegarlos en Flowable."""
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

proyecto = Path(__file__).resolve().parents[1]
modelos = proyecto / "BPMN"
destino = proyecto / ".runtime" / "despliegue-proceso-720.bar"
destino.parent.mkdir(exist_ok=True)

with ZipFile(destino, "w", compression=ZIP_DEFLATED) as paquete:
    for nombre in ("gestion-leads.bpmn", "oportunidades-fechas.bpmn"):
        paquete.write(modelos / nombre, arcname=nombre)
