from datetime import datetime, timezone
from typing import TYPE_CHECKING, Optional
from sqlalchemy import Column
from sqlalchemy.dialects.postgresql import TIMESTAMP
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from app.modules.usuario.model import Usuario


class DireccionEntrega(SQLModel, table=True):

    __tablename__ = "direcciones_entrega"


    id: Optional[int] = Field(default=None, primary_key=True)

    usuario_id: int = Field(
        foreign_key="usuarios.id",
        nullable=False,
        index=True,
    )


    alias: Optional[str] = Field(default=None, max_length=60, nullable=True)

    linea1: str = Field(
        max_length=120,
        nullable=False,
    )

    linea2: Optional[str] = Field(default=None, max_length=120, nullable=True)

    ciudad: str = Field(
        max_length=80,
        nullable=False,
    )

    provincia: Optional[str] = Field(default=None, max_length=80, nullable=True)

    codigo_postal: Optional[str] = Field(default=None, max_length=10, nullable=True)


    latitud: Optional[float] = Field(default=None, nullable=True)

    longitud: Optional[float] = Field(default=None, nullable=True)


    es_principal: bool = Field(
        default=False,
        nullable=False,
    )


    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=Column(TIMESTAMP(timezone=True), nullable=False),
    )

    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=Column(TIMESTAMP(timezone=True), nullable=False),
    )

    deleted_at: Optional[datetime] = Field(default=None, sa_column=Column(TIMESTAMP(timezone=True), nullable=True))


    usuario: "Usuario" = Relationship(
        back_populates="direcciones"
    )