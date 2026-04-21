from typing import Optional

from pydantic import Field
from sqlmodel import SQLModel


class CategoriaBase(SQLModel):
    codigo: str = Field(min_length=2, max_length=15)
    descripcion: str = Field(min_length=3, max_length=120)
    activo: bool = True


class CategoriaCreate(CategoriaBase):
    pass


class CategoriaUpdate(SQLModel):
    codigo: Optional[str] = Field(default=None, min_length=2, max_length=15)
    descripcion: Optional[str] = Field(default=None, min_length=3, max_length=120)
    activo: Optional[bool] = None


class CategoriaRead(CategoriaBase):
    id: int
