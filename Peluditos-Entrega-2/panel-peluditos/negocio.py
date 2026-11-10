"""Datos de negocio. Cada operación usa una conexión y su propia transacción."""
import json
import sqlite3
from contextlib import contextmanager
from pathlib import Path

DATA = Path(__file__).resolve().parents[1] / "data"
DB = DATA / "negocio.sqlite3"
FIELDS = ("nombre", "wsp", "email", "canal", "mascota", "tipoMascota", "cumple",
          "estado", "cupon", "motivo", "actividad", "ejemplo")
PROFILE = ("nombre", "wsp", "email", "canal", "mascota", "tipoMascota", "cumple", "motivo")
TRACKING = ("estado", "cupon", "motivo", "actividad")


@contextmanager
def connection():
    db = sqlite3.connect(DB, timeout=10)
    db.row_factory = sqlite3.Row
    db.execute("PRAGMA foreign_keys = ON")
    try:
        with db:
            yield db
    finally:
        db.close()


def insert_client(db, client):
    keys = ("id",) + tuple(k for k in FIELDS if k in client)
    db.execute(
        f"INSERT INTO clientes ({', '.join(keys)}) VALUES ({', '.join('?' for _ in keys)}) "
        "ON CONFLICT(id) DO NOTHING",
        tuple(client[k] for k in keys),
    )


def insert_sale(db, client_id, sale, origin=None):
    # Si el worker reintenta la misma instancia, la restricción UNIQUE de origen evita una segunda venta.
    db.execute(
        """INSERT INTO ventas (cliente_id, origen, fecha, producto, monto, cupon)
           VALUES (?, ?, ?, ?, ?, ?) ON CONFLICT(origen) DO NOTHING""",
        (client_id, origin, sale["fecha"], sale["producto"], sale["monto"], bool(sale.get("cupon"))),
    )


def insert_event(db, event):
    db.execute("INSERT INTO eventos (id, nombre, fecha) VALUES (?, ?, ?) ON CONFLICT(id) DO NOTHING",
               (event["id"], event["nombre"], event["fecha"]))


def initialize():
    DATA.mkdir(exist_ok=True)
    with connection() as db:
        db.executescript(Path(__file__).with_name("esquema.sql").read_text(encoding="utf-8"))
        db.execute("BEGIN IMMEDIATE")
        # Importa el JSON anterior al crear la base. La versión marca que la importación ya se procesó.
        if db.execute("PRAGMA user_version").fetchone()[0] == 0:
            legacy = DATA / "panel.json"
            if legacy.exists():
                old = json.loads(legacy.read_text(encoding="utf-8"))
                for client in old["clientes"]:
                    insert_client(db, client)
                    for sale in client.get("ventas", []):
                        insert_sale(db, client["id"], sale)
                for event in old["eventos"]:
                    insert_event(db, event)
            db.execute("PRAGMA user_version = 1")


def read_state():
    with connection() as db:
        db.execute("BEGIN")
        clients = {row["id"]: dict(row, ventas=[]) for row in
                   db.execute("SELECT * FROM clientes ORDER BY rowid DESC")}
        for client in clients.values():
            client["ejemplo"] = bool(client["ejemplo"])
        for row in db.execute("SELECT cliente_id, fecha, producto, monto, cupon FROM ventas ORDER BY id"):
            sale = dict(row)
            client_id = sale.pop("cliente_id")
            sale["cupon"] = bool(sale["cupon"])
            clients[client_id]["ventas"].append(sale)
        events = [dict(row) for row in db.execute("SELECT * FROM eventos ORDER BY rowid")]
        return {"clientes": list(clients.values()), "eventos": events}


def create_client(client):
    with connection() as db:
        insert_client(db, client)


def patch_client(client_id, changes, fields=TRACKING, sale=None, origin=None):
    keys = [k for k in fields if k in changes]
    if not keys:
        raise ValueError("Faltan campos para actualizar")
    # Si hay una venta, se guarda junto al cambio de estado. Si falla una operación, se revierten ambas.
    with connection() as db:
        changed = db.execute(
            f"UPDATE clientes SET {', '.join(k + ' = ?' for k in keys)} WHERE id = ?",
            [changes[k] for k in keys] + [client_id],
        )
        if not changed.rowcount:
            raise KeyError("Cliente no encontrado")
        if sale is not None:
            insert_sale(db, client_id, sale, origin)
        return dict(db.execute("SELECT * FROM clientes WHERE id = ?", (client_id,)).fetchone())


def create_event(event):
    if any(not isinstance(event.get(k), str) or not event[k].strip() for k in ("id", "nombre", "fecha")):
        raise ValueError("Completa el nombre y la fecha del evento")
    with connection() as db:
        insert_event(db, event)


def delete_client(client_id):
    with connection() as db:
        db.execute("DELETE FROM clientes WHERE id = ?", (client_id,))


def delete_event(event_id):
    with connection() as db:
        db.execute("DELETE FROM eventos WHERE id = ?", (event_id,))


def delete_examples():
    with connection() as db:
        db.execute("DELETE FROM clientes WHERE ejemplo = 1")
