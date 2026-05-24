from __future__ import annotations
from datetime import datetime
from typing import TYPE_CHECKING, Optional
from sqlalchemy import CHAR, Column, DateTime, func
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from app.modules.usuario.model import Usuario


class RefreshToken(SQLModel, table=True):
    __tablename__ = "refresh_token"

    id: Optional[int] = Field(default=None, primary_key=True)

    usuario_id: int = Field(
        foreign_key="usuarios.id",
        nullable=False,
    )

    token_hash: str = Field(
        sa_column=Column(
            CHAR(64),
            unique=True,
            nullable=False,
        ),
    )

    expires_at: datetime = Field(
        nullable=False,
    )

    revoked_at: Optional[datetime] = Field(default=None, nullable=True)

    created_at: datetime = Field(
        sa_column=Column(
            DateTime(timezone=True),
            nullable=False,
            server_default=func.now(),
        ),
    )

    # -------------------------------------------------------------------------
    # Relaciones
    # -------------------------------------------------------------------------

    usuario: "Usuario" = Relationship(
        back_populates="refresh_tokens"
    )