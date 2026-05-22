from typing import Optional

from sqlalchemy import Column, Text
from sqlmodel import Field, SQLModel


class Rol(SQLModel, table=True):
    """Usamos PK semánticos en lugar de ID numérico para
      evitar consultas adicionales a la BD"""
    __tablename__ = "roles"

    codigo: str = Field(#Código único del rol (ej: ADMIN, USER, MODERATOR)
        primary_key=True,
        max_length=20,
    )

    nombre: str = Field(#Nombre descriptivo y único del rol
        max_length=50,
        unique=True,
        nullable=False,
    )

    descripcion: Optional[str] = Field(#Descripción opcional del rol y sus permisos
        default=None,
        sa_column=Column(Text, nullable=True),
    )