[README.md](https://github.com/user-attachments/files/34608472/README.md)
# Arquitectura de Peluditos Pet Chile

diagrama en Mermaid 

```mermaid
flowchart LR
    persona["Cliente o dueña"]
    ui["Interfaz propia<br/>HTML, CSS y JavaScript"]
    panel["API del panel<br/>Python · 8092"]
    flow["Flowable OSS 7.2 REST<br/>BPMN de leads y oportunidades · 8080"]
    worker["External worker<br/>Python"]
    java["Servicios Java<br/>Jakarta REST · 8091"]
    h2[("H2 · base del motor")]
    sqlite[("SQLite · datos de negocio")]
    plan["Planificador de campañas a 15 días"]
    social["Registro desde redes sociales"]
    mail["Envío de correo real"]

    persona --> ui
    ui -->|HTTP y JSON| panel
    panel -->|Inicia procesos y gestiona tareas| flow
    panel -->|SQL: fichas, ventas y eventos| sqlite
    flow -->|JDBC: tareas, procesos e historial| h2
    worker -->|Consulta y completa tareas externas| flow
    worker -->|REST: cupón, sugerencia, estado y envío simulado| java
    worker -->|REST: registra y actualiza fichas y ventas| panel
    plan -.-> flow
    social -.-> panel
    java -.-> mail

    classDef previsto stroke-dasharray: 6 4,stroke:#777,fill:#fafafa,color:#222;
    class plan,social,mail previsto;
```

Las cajas de borde continuo son componentes implementados. Las cajas y flechas discontinuas representan ampliaciones planificadas. El recorrido de oportunidades se inicia desde el panel y el servicio Java simula el envío.

H2 conserva las definiciones, instancias, tareas e historial del motor. SQLite conserva los datos comerciales. El panel es el único componente que abre SQLite. El worker actualiza los datos mediante la API del panel. Consulta [las decisiones de almacenamiento y la prueba](../docs/persistencia.md).
