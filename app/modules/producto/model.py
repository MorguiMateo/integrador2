from datetime import datetime
from decimal import Decimal

from sqlalchemy import CheckConstraint, Column, DateTime, Numeric, Text, func
from sqlalchemy.dialects.postgresql import ARRAY
from sqlmodel import Field, Relationship, SQLModel

from app.modules.producto.link_models import ProductoCategoria, ProductoIngrediente


class Producto(SQLModel, table=True):
    __tablename__ = "productos"
    __table_args__ = (
        CheckConstraint("precio_base >= 0", name="ck_productos_precio_base_nonneg"),
        CheckConstraint("stock_cantidad >= 0", name="ck_productos_stock_nonneg"),
    )

    id: int | None = Field(default=None, primary_key=True)
    nombre: str = Field(index=True, min_length=2, max_length=150)
    descripcion: str | None = Field(default=None, sa_column=Column(Text, nullable=True))

    precio_base: Decimal = Field(
        default=Decimal("0"),
        sa_column=Column(Numeric(10, 2), nullable=False),
    )

    imagenes_url: list[str] = Field(
        default_factory=list,
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

    deleted_at: datetime | None = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True), nullable=True),
    )

    # sumee un campo nuevo al modelo Producto llamado "unidad_venta_id" que sirve como foreign key para la tabla "unidad_medidas".

    unidad_venta_id: int | None = Field(
        default=None, 
        foreign_key="unidad_medidas.id",
        nullable=True
    )

    categoria_links: list[ProductoCategoria] = Relationship(
        back_populates="producto",
    )
    ingrediente_links: list[ProductoIngrediente] = Relationship(
        back_populates="producto",
    )

