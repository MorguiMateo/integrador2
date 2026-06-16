from datetime import datetime, timezone
from typing import TYPE_CHECKING, Optional
from sqlalchemy import CHAR, Column
from sqlalchemy.dialects.postgresql import TIMESTAMP
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from app.modules.usuario_rol.model import UsuarioRol
    from app.modules.direccion_entrega.model import DireccionEntrega


class Usuario(SQLModel, table=True):
    __tablename__ = "usuarios"

    id: Optional[int] = Field(default=None, primary_key=True)

    nombre: str = Field(max_length=80, nullable=False)
    apellido: str = Field(max_length=80, nullable=False)
    email: str = Field(max_length=254, nullable=False, unique=True, index=True)
    celular: Optional[str] = Field(default=None, max_length=20, nullable=True)


    password_hash: str = Field(
        sa_column=Column(CHAR(60), nullable=False)
    )


    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=Column(TIMESTAMP(timezone=True), nullable=False)
    )

    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=Column(TIMESTAMP(timezone=True), nullable=False)
    )

    deleted_at: Optional[datetime] = Field(default=None, sa_column=Column(TIMESTAMP(timezone=True), nullable=True))


    roles_link: list["UsuarioRol"] = Relationship(
        back_populates="usuario",
        sa_relationship_kwargs={
            "lazy": "selectin",
            "foreign_keys": "[UsuarioRol.usuario_id]",
        },
    )
    direcciones: list["DireccionEntrega"] = Relationship(back_populates="usuario")

    @property
    def roles(self) -> list[str]:
        return [ur.rol_codigo for ur in self.roles_link]