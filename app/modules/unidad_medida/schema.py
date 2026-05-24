from __future__ import annotations
from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field


class UnidadMedidaCreate(BaseModel):
    nombre: str = Field(max_length=50)
    simbolo: str = Field(max_length=10)
    tipo: str = Field(max_length=20)


class UnidadMedidaRead(BaseModel):
    id: int
    nombre: str = Field(max_length=50)
    simbolo: str = Field(max_length=10)
    tipo: str = Field(max_length=20)
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
