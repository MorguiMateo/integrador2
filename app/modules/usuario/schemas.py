from datetime import datetime
from typing import Optional
from pydantic import EmailStr
from sqlmodel import SQLModel


class UserCreate(SQLModel):
    nombre: str
    apellido: str
    email: EmailStr
    password: str
    celular: Optional[str] = None


class UserPublic(SQLModel):
    id: int
    nombre: str
    apellido: str
    email: EmailStr
    celular: Optional[str] = None
    roles: list[str]
    created_at: datetime


class UserUpdate(SQLModel):
    nombre: Optional[str] = None
    apellido: Optional[str] = None
    celular: Optional[str] = None
