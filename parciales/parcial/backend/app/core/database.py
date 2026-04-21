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
    # Importaciones necesarias para que SQLModel.metadata registre cada tabla
    # antes de llamar a create_all. Sin esto, create_all no conoce los modelos.
    from app.modules.categoria.model import Categoria  # noqa: F401
    from app.modules.ingrediente.model import Ingrediente  # noqa: F401
    from app.modules.producto.link_models import (  # noqa: F401
        ProductoCategoria,
        ProductoIngrediente,
    )
    from app.modules.producto.model import Producto  # noqa: F401

    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session
