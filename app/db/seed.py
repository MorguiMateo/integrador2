
from sqlmodel import Session, select
from app.core.database import engine
from app.modules.rol.model import Rol
from app.modules.unidad_medida.model import UnidadMedida
from app.modules.estado_pedido.model import EstadoPedido
from app.modules.forma_pago.model import FormaPago
from app.modules.usuario.model import Usuario
from app.modules.usuario_rol.model import UsuarioRol
from app.core.security import get_password_hash



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

ESTADOS_PEDIDO = [
    {"codigo": "PENDIENTE",  "descripcion": "Pedido recibido", "orden": 1, "es_terminal": False},
    {"codigo": "CONFIRMADO", "descripcion": "Pedido confirmado", "orden": 2, "es_terminal": False},
    {"codigo": "EN_PREP",    "descripcion": "En preparación", "orden": 3, "es_terminal": False},
    {"codigo": "EN_CAMINO",  "descripcion": "En camino", "orden": 4, "es_terminal": False},
    {"codigo": "ENTREGADO",  "descripcion": "Entregado", "orden": 5, "es_terminal": True},
    {"codigo": "CANCELADO",  "descripcion": "Cancelado", "orden": 6, "es_terminal": True},
]

FORMAS_PAGO = [
    {"codigo": "EFECTIVO",     "descripcion": "Pago en efectivo", "habilitado": True},
    {"codigo": "MERCADOPAGO",  "descripcion": "Pago por MercadoPago", "habilitado": True},
]




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


def _seed_estados_pedido(session: Session) -> None:
    for data in ESTADOS_PEDIDO:
        existing = session.get(EstadoPedido, data["codigo"])

        if existing:
            continue

        session.add(EstadoPedido(**data))
    session.flush()



def _seed_formas_pago(session: Session) -> None:
    for data in FORMAS_PAGO:
        existing = session.get(FormaPago, data["codigo"])

        if existing:
            continue

        session.add(FormaPago(**data))
    session.flush()

def _seed_admin(session: Session) -> None:
    existing = session.exec(
        select(Usuario).where(Usuario.email == "admin@foodstore.com")
    ).first()

    if existing:
        return

    admin = Usuario(
        nombre="Admin",
        apellido="Sistema",
        email="admin@foodstore.com",
        password_hash=get_password_hash("admin123"),
    )
    session.add(admin)
    session.flush()

    session.add(UsuarioRol(usuario_id=admin.id, rol_codigo="ADMIN"))
    session.flush()




def run_seed(session: Session) -> None:

    _seed_roles(session)
    _seed_unidades_medida(session)
    _seed_estados_pedido(session)
    _seed_formas_pago(session)
    _seed_admin(session)

if __name__ == "__main__":
    with Session(engine) as session:
        run_seed(session)
        session.commit()

    print("✓ Seed completado.")

