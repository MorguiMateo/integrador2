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

    # El float binario tiene errores de redondeo; 5500.10 puede terminar
    #  como 5500.0999999... Decimal lo evita, por eso los precios siempre usan este tipo.
    precio_base: Decimal = Field(
        default=Decimal("0"),
        sa_column=Column(Numeric(10, 2), nullable=False),
    )

    # ARRAY(Text) de Postgres guarda todas las URLs en una sola columna,
    # sin necesitar una tabla producto_imagenes separada.
    imagenes_url: list[str] = Field(
        default_factory=list,
        sa_column=Column(ARRAY(Text), nullable=False, server_default="{}"),
    )
    stock_cantidad: int = Field(default=0, ge=0, nullable=False)
    disponible: bool = Field(default=True, nullable=False)

    # server_default -> Postgres pone la fecha al insertar.
    # onupdate -> Postgres la actualiza en cada UPDATE.
    # Python no toca estas fechas; las maneja la DB directamente.
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
    # deleted_at NULL = registro activo. Con fecha = soft delete.
    # El BaseRepository filtra deleted_at IS NULL en todas las queries.
    deleted_at: datetime | None = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True), nullable=True),
    )

    # Producto no apunta directo a Categoria ni a Ingrediente.
    # La relación pasa por las tablas intermedias ProductoCategoria y
    # ProductoIngrediente, que además guardan campos extra (es_principal,
    # es_removible). back_populates conecta ambos lados del vínculo.
    categoria_links: list[ProductoCategoria] = Relationship(
        back_populates="producto",
    )
    ingrediente_links: list[ProductoIngrediente] = Relationship(
        back_populates="producto",
    )
