##   - database.py — crea el engine de conexión a PostgreSQL, define create_db_and_tables para crear todas las tablas al arrancar, y provee get_session para inyectar sesiones vía Depends.
import os

from dotenv import load_dotenv
from sqlmodel import SQLModel, Session, create_engine

load_dotenv()

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg2://postgres@localhost:5432/parcial",
)

engine = create_engine(DATABASE_URL, echo=True)


def create_db_and_tables() -> None:
    from app.modules.rol.model import Rol
    from app.modules.usuario.model import Usuario
    from app.modules.usuario_rol.model import UsuarioRol
    from app.modules.direccion_entrega.model import DireccionEntrega
    from app.modules.unidad_medida.model import UnidadMedida
    from app.modules.estado_pedido.model import EstadoPedido
    from app.modules.forma_pago.model import FormaPago
    from app.modules.pedido.model import Pedido, DetallePedido, HistorialEstadoPedido
    from app.modules.categoria.model import Categoria
    from app.modules.ingrediente.model import Ingrediente
    from app.modules.producto.link_models import (
        ProductoCategoria,
        ProductoIngrediente,
    )
    from app.modules.producto.model import Producto

    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session
