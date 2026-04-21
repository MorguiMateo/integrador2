from __future__ import annotations

from typing import TYPE_CHECKING, List, Optional

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from app.producto.link_models import ProductoIngrediente


class Ingrediente(SQLModel, table=True):
    __tablename__ = "ingredientes"

    id: Optional[int] = Field(default=None, primary_key=True)
    nombre: str = Field(index=True, unique=True, max_length=60)
    descripcion: Optional[str] = Field(default=None, max_length=200)
    es_alergeno: bool = Field(default=False)
    activo: bool = Field(default=True)

    productos_link: List["ProductoIngrediente"] = Relationship(
        back_populates="ingrediente",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"},
    )
