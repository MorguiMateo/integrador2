import os

from dotenv import load_dotenv
from sqlmodel import SQLModel, Session, create_engine

load_dotenv()

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg2://postgres:postgres@localhost:5432/parcial_fullstack",
)

engine = create_engine(DATABASE_URL, echo=False)


def create_db_and_tables() -> None:
    from app.categoria.model import Categoria  # noqa: F401
    from app.ingrediente.model import Ingrediente  # noqa: F401
    from app.producto.model import (  # noqa: F401
        Producto,
        ProductoCategoria,
        ProductoIngrediente,
    )

    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session
