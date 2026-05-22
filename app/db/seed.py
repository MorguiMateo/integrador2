"""
app/db/seed.py

Pobla la base de datos con datos iniciales del sistema.

Idempotente: puede ejecutarse múltiples veces sin duplicar datos
ni lanzar errores. Usa session.get() para verificar existencia
antes de insertar.

Uso manual:
    python -m app.db.seed
"""

from sqlmodel import Session, select

from app.core.database import engine
from app.modules.rol.model import Rol
from app.modules.unidad_medida.model import UnidadMedida

# -----------------------------------------------------------------------------
# Datos
# -----------------------------------------------------------------------------

ROLES = [
    {
        "codigo": "ADMIN",
        "nombre": "Administrador",
        "descripcion": "Acceso total sin restricciones.",
    },
    {
        "codigo": "STOCK",
        "nombre": "Gestor de Stock",
        "descripcion": "Actualiza stock y disponibilidad.",
    },
    {
        "codigo": "PEDIDOS",
        "nombre": "Gestor de Pedidos",
        "descripcion": "Avanza estados de pedidos (CONFIRMADO → ENTREGADO).",
    },
    {
        "codigo": "CLIENT",
        "nombre": "Cliente",
        "descripcion": "Opera solo sus propios datos.",
    },
]

UNIDADES_MEDIDA = [
    {"nombre": "kilogramo",      "simbolo": "kg",  "tipo": "masa"},
    {"nombre": "gramo",          "simbolo": "g",   "tipo": "masa"},
    {"nombre": "litro",          "simbolo": "L",   "tipo": "volumen"},
    {"nombre": "mililitro",      "simbolo": "mL",  "tipo": "volumen"},
    {"nombre": "pieza",          "simbolo": "u",   "tipo": "unidad"},
    {"nombre": "docena",         "simbolo": "doc", "tipo": "unidad"},
    {"nombre": "metro cuadrado", "simbolo": "m²",  "tipo": "area"},
]

# -----------------------------------------------------------------------------
# Seeders
# -----------------------------------------------------------------------------


def _seed_roles(session: Session) -> None:
    for data in ROLES:
        existing = session.get(Rol, data["codigo"])

        if existing:
            continue

        session.add(Rol(**data))

    session.flush()


def _seed_unidades_medida(session: Session) -> None:
    for data in UNIDADES_MEDIDA:
        statement = (
            select(UnidadMedida)
            .where(UnidadMedida.simbolo == data["simbolo"])
        )

        existing = session.exec(statement).first()

        if existing:
            continue

        session.add(UnidadMedida(**data))

    session.flush()


# -----------------------------------------------------------------------------
# Entry point
# -----------------------------------------------------------------------------


def run_seed(session: Session) -> None:
    """
    Ejecuta todos los seeders en orden.

    Idempotente: verifica existencia antes de insertar.
    No hace commit — el llamador es responsable del commit.

    Args:
        session (Session):
            Sesión de base de datos activa.
    """

    _seed_roles(session)
    _seed_unidades_medida(session)

    session.commit()

    print("✓ Seed completado.")


if __name__ == "__main__":
    with Session(engine) as session:
        run_seed(session)