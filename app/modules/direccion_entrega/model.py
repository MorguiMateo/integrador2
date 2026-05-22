from __future__ import annotations

from datetime import datetime, timezone
from typing import TYPE_CHECKING

from sqlalchemy import Column
from sqlalchemy.dialects.postgresql import TIMESTAMPTZ
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from app.modules.usuario.model import Usuario


class DireccionEntrega(SQLModel, table=True):
    """
    Dirección de entrega asociada a un usuario.

    Un usuario puede tener múltiples direcciones,
    pero solo una puede estar marcada como principal.
    """

    __tablename__ = "direccion_entrega"

    # -------------------------------------------------------------------------
    # Primary Key
    # -------------------------------------------------------------------------

    id: int | None = Field(
        default=None,
        primary_key=True,
    )

    # -------------------------------------------------------------------------
    # Foreign Key
    # -------------------------------------------------------------------------

    usuario_id: int = Field(
        foreign_key="usuario.id",
        nullable=False,
        index=True,
    )

    # -------------------------------------------------------------------------
    # Datos de dirección
    # -------------------------------------------------------------------------

    alias: str | None = Field(
        default=None,
        max_length=60,
        nullable=True,
    )

    linea1: str = Field(
        max_length=120,
        nullable=False,
    )

    linea2: str | None = Field(
        default=None,
        max_length=120,
        nullable=True,
    )

    ciudad: str = Field(
        max_length=80,
        nullable=False,
    )

    provincia: str | None = Field(
        default=None,
        max_length=80,
        nullable=True,
    )

    codigo_postal: str | None = Field(
        default=None,
        max_length=10,
        nullable=True,
    )

    # -------------------------------------------------------------------------
    # Geolocalización
    # -------------------------------------------------------------------------

    latitud: float | None = Field(
        default=None,
        nullable=True,
    )

    longitud: float | None = Field(
        default=None,
        nullable=True,
    )

    # -------------------------------------------------------------------------
    # Principal
    # -------------------------------------------------------------------------

    es_principal: bool = Field(
        default=False,
        nullable=False,
    )

    # -------------------------------------------------------------------------
    # Auditoría
    # -------------------------------------------------------------------------

    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=Column(TIMESTAMPTZ(timezone=True), nullable=False),
    )

    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=Column(TIMESTAMPTZ(timezone=True), nullable=False),
    )

    deleted_at: datetime | None = Field(
        default=None,
        sa_column=Column(TIMESTAMPTZ(timezone=True), nullable=True),
    )

    # -------------------------------------------------------------------------
    # Relaciones
    # -------------------------------------------------------------------------

    usuario: "Usuario" = Relationship(
        back_populates="direcciones"
    )