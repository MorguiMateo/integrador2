from __future__ import annotations
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field

class IngredienteBase(BaseModel):
    nombre: str = Field(min_length=2, max_length=100)
    stock_cantidad: int = Field(default=0, ge=0)
    descripcion: Optional[str] = None
    es_alergeno: bool = False


class IngredienteCreate(IngredienteBase):
    pass


class IngredienteUpdate(BaseModel):
    nombre: Optional[str] = Field(default=None, min_length=2, max_length=100)
    stock_cantidad: Optional[int] = Field(default=None, ge=0)
    descripcion: Optional[str] = None
    es_alergeno: Optional[bool] = None


class IngredienteRead(IngredienteBase):
    id: int
    created_at: datetime
    updated_at: datetime

    ##asi pydantic lee los datos directo del objeto ORM (objeto.atributo)
    model_config = ConfigDict(from_attributes=True)
