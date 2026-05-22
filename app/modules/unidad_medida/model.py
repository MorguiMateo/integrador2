from __future__ import annotations

from datetime import datetime

from sqlalchemy import func, Column, DateTime

from sqlmodel import Field, SQLModel


class UnidadMedida(SQLModel, table=True):
    __tablenam__ = "unidad_medidas"

    id: int | None = Field(default=None, primary_key=True)
    nombre: str = Field(unique=True, max_length=50, nullable=False)
    simbolo: str = Field(unique=True, max_length=10, nullable=False)
    tipo: str = Field(max_length=20, nullable=False)
    created_at: datetime = Field(
        sa_column=Column(DateTime(timezone=True), nullable=False, server_default=func.now()),
    )

    # cree una tabla  de catalogo llamada "unidad_medidas"
