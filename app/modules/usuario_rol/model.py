from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import Column, DateTime, func
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from app.modules.usuario.model import Usuario


class UsuarioRol(SQLModel, table=True):

    #Tabla intermedia entre usuarios y roles.
    __tablename__ = "usuarios_roles"
    """
    Los roles utlizan una PK compuesta para representar el JSON del usuario
    de forma más simple:
    {
    "roles": ["CAJA", "STOCK"]
    }
    """
    usuario_id: int = Field(#ID del usuario al que pertenece el rol
        foreign_key="usuarios.id",
        primary_key=True,
    )

    rol_codigo: str = Field(#Código del rol asignado al usuario
        foreign_key="roles.codigo",
        primary_key=True,
        max_length=20,
    )

    asignado_por_id: Optional[int] = Field(#Usuario que asignó el rol, puede ser NULL si fue asignado automáticamente por el sistema
        default=None,
        foreign_key="usuarios.id",
        nullable=True,
    )

    expires_at: Optional[datetime] = Field(#Fecha de expiración del rol. NULL indica que no vence
        default=None,
        nullable=True,
    )

    created_at: datetime = Field(#Fecha de creación del registro
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