from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import Column, DateTime, Float, Text, func
from sqlalchemy.dialects.postgresql import ARRAY
from sqlmodel import Field, Relationship, SQLModel

from app.modules.producto.link_models import ProductoCategoria, ProductoIngrediente

if TYPE_CHECKING:
    from app.modules.unidad_medida.model import UnidadMedida


class Producto(SQLModel, table=True):
    __tablename__ = "productos"

    id: Optional[int] = Field(default=None, primary_key=True)
    nombre: str = Field(index=True, min_length=2, max_length=150)
    descripcion: Optional[str] = Field(default=None, sa_column=Column(Text, nullable=True))

    precio_base: float = Field(
        default=0.0,
        sa_column=Column(Float, nullable=False),
    )

    imagenes_url: list[str] = Field(
        default=[],
        sa_column=Column(ARRAY(Text), nullable=False, server_default="{}"),
    )
    stock_cantidad: int = Field(default=0, ge=0, nullable=False)
    disponible: bool = Field(default=True, nullable=False)

    created_at: datetime = Field(
        sa_column=Column(DateTime(timezone=True), nullable=False, server_default=func.now()),
    )
    updated_at: datetime = Field(
        sa_column=Column(
            DateTime(timezone=True),
            nullable=False,
            server_default=func.now(),
            onupdate=func.now(),
        ),
    )
    deleted_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True), nullable=True),
    )

    unidad_venta_id: Optional[int] = Field(
        default=None,
        foreign_key="unidad_medidas.id",
        nullable=True,
    )

    unidad_venta: Optional["UnidadMedida"] = Relationship()

    categoria_links: list[ProductoCategoria] = Relationship(back_populates="producto")
    ingrediente_links: list[ProductoIngrediente] = Relationship(back_populates="producto")
