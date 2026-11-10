CREATE TABLE IF NOT EXISTS clientes (
    id TEXT PRIMARY KEY NOT NULL,
    nombre TEXT NOT NULL DEFAULT '',
    wsp TEXT NOT NULL DEFAULT '',
    email TEXT NOT NULL DEFAULT '',
    canal TEXT NOT NULL DEFAULT '',
    mascota TEXT NOT NULL DEFAULT '',
    tipoMascota TEXT NOT NULL DEFAULT '',
    cumple TEXT NOT NULL DEFAULT '',
    estado TEXT NOT NULL DEFAULT 'PENDIENTE'
        CHECK (estado IN ('PENDIENTE', 'CLIENTE', 'NO CONCRETADO')),
    cupon TEXT NOT NULL DEFAULT '',
    motivo TEXT NOT NULL DEFAULT '',
    actividad TEXT NOT NULL DEFAULT '',
    ejemplo INTEGER NOT NULL DEFAULT 0 CHECK (ejemplo IN (0, 1))
);

CREATE TABLE IF NOT EXISTS eventos (
    id TEXT PRIMARY KEY NOT NULL,
    nombre TEXT NOT NULL,
    fecha TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS ventas (
    id INTEGER PRIMARY KEY,
    -- Cada venta pertenece a una ficha y se elimina junto con ella.
    cliente_id TEXT NOT NULL REFERENCES clientes(id) ON DELETE CASCADE,
    -- La instancia de Flowable identifica la venta en los reintentos del worker.
    origen TEXT UNIQUE,
    fecha TEXT NOT NULL,
    producto TEXT NOT NULL,
    monto INTEGER NOT NULL CHECK (monto >= 0),
    cupon INTEGER NOT NULL CHECK (cupon IN (0, 1))
);

CREATE INDEX IF NOT EXISTS ventas_cliente ON ventas(cliente_id);
