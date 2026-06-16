from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import Column, DateTime, func
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from app.modules.usuario.model import Usuario


class UsuarioRol(SQLModel, table=True):
    __tablename__ = "usuarios_roles"

    usuario_id: int = Field(
        foreign_key="usuarios.id",
        primary_key=True,
    )

    rol_codigo: str = Field(
        foreign_key="roles.codigo",
        primary_key=True,
        max_length=20,
    )

    asignado_por_id: Optional[int] = Field(
        default=None,
        foreign_key="usuarios.id",
        nullable=True,
    )

    expires_at: Optional[datetime] = Field(
        default=None,
        nullable=True,
    )

    created_at: datetime = Field(
        sa_column=Column(
            DateTime(timezone=True),
            nullable=False,
            server_default=func.now(),
        ),
    )

    usuario: "Usuario" = Relationship(
        back_populates="roles_link",
        sa_relationship_kwargs={"foreign_keys": "[UsuarioRol.usuario_id]"},
    )