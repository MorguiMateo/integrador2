from typing import Optional

from pydantic import Field
from sqlmodel import SQLModel


class IngredienteBase(SQLModel):
    nombre: str = Field(min_length=2, max_length=60)
    descripcion: Optional[str] = Field(default=None, max_length=200)
    es_alergeno: bool = False
    activo: bool = True


class IngredienteCreate(IngredienteBase):
    pass


class IngredienteUpdate(SQLModel):
    nombre: Optional[str] = Field(default=None, min_length=2, max_length=60)
    descripcion: Optional[str] = Field(default=None, max_length=200)
    es_alergeno: Optional[bool] = None
    activo: Optional[bool] = None


class IngredienteRead(IngredienteBase):
    id: int
