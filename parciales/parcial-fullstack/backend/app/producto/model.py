from __future__ import annotations

from typing import List, Optional

from sqlmodel import Field, Relationship, SQLModel

from app.categoria.model import Categoria
from app.producto.link_models import ProductoCategoria, ProductoIngrediente


class Producto(SQLModel, table=True):
    __tablename__ = "productos"

    id: Optional[int] = Field(default=None, primary_key=True)
    nombre: str = Field(index=True, max_length=80)
    descripcion: Optional[str] = Field(default=None, max_length=255)
    precio: float = Field(gt=0)
    stock: int = Field(default=0, ge=0)
    activo: bool = Field(default=True)

    categorias: List[Categoria] = Relationship(
        back_populates="productos",
        link_model=ProductoCategoria,
    )

    ingredientes_link: List[ProductoIngrediente] = Relationship(
        back_populates="producto",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"},
    )
