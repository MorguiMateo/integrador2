from datetime import datetime

from pydantic import EmailStr
from sqlmodel import SQLModel


class UserCreate(SQLModel):
    """
    Schema utilizado para crear usuarios.

    La contraseña entra en texto plano y debe:
    - hashearse en el service
    - descartarse inmediatamente

    Nunca debe persistirse directamente.
    """

    nombre: str

    apellido: str

    email: EmailStr

    password: str

    celular: str | None = None


class UserPublic(SQLModel):
    """
    Schema público de usuario.

    Utilizado como response_model en FastAPI.

    IMPORTANTE:
    Nunca incluye:
    - password
    - password_hash
    """

    id: int

    nombre: str

    apellido: str

    email: EmailStr

    celular: str | None = None

    roles: list[str]

    created_at: datetime


class UserUpdate(SQLModel):
    """
    Schema para actualización parcial de usuarios.

    Todos los campos son opcionales.

    IMPORTANTE:
    email y password se actualizan mediante
    endpoints específicos por seguridad.
    """

    nombre: str | None = None

    apellido: str | None = None

    celular: str | None = None