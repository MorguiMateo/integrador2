from datetime import datetime
from typing import Optional

from sqlalchemy import Column, DateTime, Text, func
from sqlmodel import Field, Relationship, SQLModel

from app.modules.producto.link_models import ProductoCategoria


class Categoria(SQLModel, table=True):
    __tablename__ = "categorias"

    id: int | None = Field(default=None, primary_key=True)
    parent_id: int | None = Field(
        default=None,
        foreign_key="categorias.id",
        nullable=True,
    )
    nombre: str = Field(index=True, unique=True, min_length=2, max_length=100)
    descripcion: str | None = Field(default=None, sa_column=Column(Text, nullable=True))
    imagen_url: str | None = Field(default=None, sa_column=Column(Text, nullable=True))

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

    parent: Optional["Categoria"] = Relationship(
        back_populates="children",
        sa_relationship_kwargs={"remote_side": "Categoria.id"},
    )
    children: list["Categoria"] = Relationship(back_populates="parent")

    producto_links: list[ProductoCategoria] = Relationship(
        back_populates="categoria",
    )
