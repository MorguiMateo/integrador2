from datetime import datetime
from typing import Optional

from sqlalchemy import CHAR, Column, DateTime, func
from sqlmodel import Field, SQLModel


class RefreshToken(SQLModel, table=True):
    __tablename__ = "refresh_tokens"

    id: Optional[int] = Field(#ID autoincremental del refresh token
        default=None,
        primary_key=True,
    )

    usuario_id: int = Field(#Usuario propietario del refresh token
        foreign_key="usuarios.id",
        nullable=False,
    )

    token_hash: str = Field(#Hash SHA-256 del refresh token
        sa_column=Column(
            CHAR(64),
            unique=True,
            nullable=False,
        ),
    )

    expires_at: datetime = Field(#Fecha y hora de expiración del refresh token
        nullable=False,
    )

    revoked_at: Optional[datetime] = Field(#"""Fecha de revocación del token. NULL indica que el token sigue activo
        default=None,
        nullable=True,
    )

    created_at: datetime = Field(#echa de creación del refresh token
        sa_column=Column(
            DateTime(timezone=True),
            nullable=False,
            server_default=func.now(),
        ),
    )