from datetime import datetime

from sqlalchemy import Column, DateTime, Text, func
from sqlmodel import Field, Relationship, SQLModel

from app.modules.producto.link_models import ProductoIngrediente


class Ingrediente(SQLModel, table=True):
    __tablename__ = "ingredientes"

    id: int | None = Field(default=None, primary_key=True)
    nombre: str = Field(index=True, unique=True, min_length=2, max_length=100)
    descripcion: str | None = Field(default=None, sa_column=Column(Text, nullable=True))
    es_alergeno: bool = Field(default=False, nullable=False)

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

    producto_links: list[ProductoIngrediente] = Relationship(
        back_populates="ingrediente",
    )

##elimine: deleted_at y su Column(DateTime...)