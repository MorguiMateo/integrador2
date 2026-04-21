from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from app.ingrediente.model import Ingrediente
    from app.producto.model import Producto


class ProductoCategoria(SQLModel, table=True):
    """Tabla puente N:N entre Producto y Categoría."""

    __tablename__ = "producto_categoria"

    producto_id: Optional[int] = Field(
        default=None, foreign_key="productos.id", primary_key=True
    )
    categoria_id: Optional[int] = Field(
        default=None, foreign_key="categorias.id", primary_key=True
    )


class ProductoIngrediente(SQLModel, table=True):
    """Objeto de asociación con datos propios.

    Relaciona productos e ingredientes y guarda la cantidad
    y la unidad de medida para la receta.
    Genera dos relaciones 1:N (desde Producto y desde Ingrediente).
    """

    __tablename__ = "producto_ingrediente"

    producto_id: Optional[int] = Field(
        default=None, foreign_key="productos.id", primary_key=True
    )
    ingrediente_id: Optional[int] = Field(
        default=None, foreign_key="ingredientes.id", primary_key=True
    )
    cantidad: float = Field(gt=0)
    unidad: str = Field(max_length=15, default="unidad")

    producto: "Producto" = Relationship(back_populates="ingredientes_link")
    ingrediente: "Ingrediente" = Relationship(back_populates="productos_link")
