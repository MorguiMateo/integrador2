from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING
from decimal import Decimal

from sqlalchemy import Column, DateTime, func, Numeric, CheckConstraint
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from app.modules.categoria.model import Categoria
    from app.modules.ingrediente.model import Ingrediente
    from app.modules.producto.model import Producto


class ProductoCategoria(SQLModel, table=True):
    __tablename__ = "producto_categoria"

    producto_id: int = Field(foreign_key="productos.id", primary_key=True)
    categoria_id: int = Field(foreign_key="categorias.id", primary_key=True)
    es_principal: bool = Field(default=False, nullable=False)
    created_at: datetime = Field(
        sa_column=Column(DateTime(timezone=True), nullable=False, server_default=func.now()),
    )

    producto: Producto = Relationship(back_populates="categoria_links")
    categoria: Categoria = Relationship(back_populates="producto_links")


class ProductoIngrediente(SQLModel, table=True):
    __tablename__ = "producto_ingrediente"

    producto_id: int = Field(foreign_key="productos.id", primary_key=True)
    ingrediente_id: int = Field(foreign_key="ingredientes.id", primary_key=True)
    
    es_removible: bool = Field(default=False, nullable=False)

    #meti un nuevo campo llamado "cantidad". Eeste campo indica la cantidad del ingrediente que se usa en el producto, medida en la unidad de venta del producto (unidad_venta_id).

    unidad_medida_id: int = Field(foreign_key="unidad_medidas.id", nullable=False)
    cantidad: Decimal = Field(
        sa_column=Column(Numeric(10, 3), CheckConstraint("cantidad > 0"), nullable=False)
    )

    producto: Producto = Relationship(back_populates="ingrediente_links")
    ingrediente: Ingrediente = Relationship(back_populates="producto_links")

