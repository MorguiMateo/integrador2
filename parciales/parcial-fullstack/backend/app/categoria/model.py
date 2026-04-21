from __future__ import annotations

from typing import TYPE_CHECKING, List, Optional

from sqlmodel import Field, Relationship, SQLModel

from app.producto.link_models import ProductoCategoria

if TYPE_CHECKING:
    from app.producto.model import Producto


class Categoria(SQLModel, table=True):
    __tablename__ = "categorias"

    id: Optional[int] = Field(default=None, primary_key=True)
    codigo: str = Field(index=True, unique=True, max_length=15)
    descripcion: str = Field(max_length=120)
    activo: bool = Field(default=True)

    productos: List["Producto"] = Relationship(
        back_populates="categorias",
        link_model=ProductoCategoria,
    )
