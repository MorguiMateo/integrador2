from datetime import datetime

from sqlmodel import SQLModel


class DireccionCreate(SQLModel):
    """
    Schema para crear una dirección de entrega.
    """

    alias: str | None = None
    linea1: str
    linea2: str | None = None
    ciudad: str
    provincia: str | None = None
    codigo_postal: str | None = None
    latitud: float | None = None
    longitud: float | None = None
    es_principal: bool = False


class DireccionUpdate(SQLModel):
    """
    Schema para actualización parcial de una dirección.

    Todos los campos son opcionales.
    """

    alias: str | None = None
    linea1: str | None = None
    linea2: str | None = None
    ciudad: str | None = None
    provincia: str | None = None
    codigo_postal: str | None = None
    latitud: float | None = None
    longitud: float | None = None
    es_principal: bool | None = None


class DireccionPublic(SQLModel):
    """
    Schema público de dirección de entrega.

    Utilizado como response_model en FastAPI.
    """

    id: int
    usuario_id: int
    alias: str | None
    linea1: str
    linea2: str | None
    ciudad: str
    provincia: str | None
    codigo_postal: str | None
    latitud: float | None
    longitud: float | None
    es_principal: bool
    created_at: datetime