from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel


class DireccionCreate(SQLModel):
    alias: Optional[str] = None
    linea1: str
    linea2: Optional[str] = None
    ciudad: str
    provincia: Optional[str] = None
    codigo_postal: Optional[str] = None
    latitud: Optional[float] = None
    longitud: Optional[float] = None
    es_principal: bool = False


class DireccionUpdate(SQLModel):
    alias: Optional[str] = None
    linea1: Optional[str] = None
    linea2: Optional[str] = None
    ciudad: Optional[str] = None
    provincia: Optional[str] = None
    codigo_postal: Optional[str] = None
    latitud: Optional[float] = None
    longitud: Optional[float] = None
    es_principal: Optional[bool] = None


class DireccionPublic(SQLModel):
    id: int
    usuario_id: int
    alias: Optional[str]
    linea1: str
    linea2: Optional[str]
    ciudad: str
    provincia: Optional[str]
    codigo_postal: Optional[str]
    latitud: Optional[float]
    longitud: Optional[float]
    es_principal: bool
    created_at: datetime
