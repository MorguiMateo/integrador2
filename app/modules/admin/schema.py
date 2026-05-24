from typing import Literal, Optional

from pydantic import BaseModel, Field


RoleCode = Literal["ADMIN", "STOCK", "PEDIDOS", "CLIENT"]


class UsuarioAdminUpdate(BaseModel):
    nombre: Optional[str] = Field(default=None, min_length=1, max_length=80)
    apellido: Optional[str] = Field(default=None, min_length=1, max_length=80)
    celular: Optional[str] = Field(default=None, max_length=20)


class RolesUpdate(BaseModel):
    roles: list[RoleCode] = Field(
        description="Lista completa de roles a aplicar al usuario (reemplaza los existentes).",
        min_length=1,
    )
