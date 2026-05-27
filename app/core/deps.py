##   - deps.py — contiene las dependencias de autenticación: get_current_user lee y valida el JWT del cookie, y get_current_active_user verifica además que el usuario no esté eliminado.
from typing import Optional

from fastapi import Cookie, Depends, HTTPException, status
from jose import JWTError, jwt
from sqlmodel import Session

from app.core.config import settings
from app.core.database import get_session
from app.modules.usuario.model import Usuario
from app.modules.usuario.repository import UsuarioRepository


ACCESS_COOKIE_NAME = "access_token"
REFRESH_COOKIE_NAME = "refresh_token"


_credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="No se pudieron validar las credenciales.",
)


def get_current_user(
    access_token: Optional[str] = Cookie(default=None, alias=ACCESS_COOKIE_NAME),
    session: Session = Depends(get_session),
) -> Usuario:
    if not access_token:
        raise _credentials_exception

    try:
        payload = jwt.decode(
            access_token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
        )
        email: Optional[str] = payload.get("sub")
        if email is None:
            raise _credentials_exception
    except JWTError:
        raise _credentials_exception

    usuario = UsuarioRepository(session).get_by_email(email)
    if usuario is None:
        raise _credentials_exception
    return usuario


def get_current_active_user(
    current_user: Usuario = Depends(get_current_user),
) -> Usuario:
    if current_user.deleted_at is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Usuario inactivo.",
        )
    return current_user
