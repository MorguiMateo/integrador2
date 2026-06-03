from typing import Optional

from sqlalchemy import Column, Text
from sqlmodel import Field, SQLModel


class Rol(SQLModel, table=True):
    __tablename__ = "roles"

    codigo: str = Field(
        primary_key=True,
        max_length=20,
    )

    nombre: str = Field(
        max_length=50,
        unique=True,
        nullable=False,
    )

    descripcion: Optional[str] = Field(
        default=None,
        sa_column=Column(Text, nullable=True),
    )