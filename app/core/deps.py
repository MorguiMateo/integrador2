from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlmodel import Session

from app.core.config import settings
from app.core.database import get_session
from app.modules.usuario.model import Usuario
from app.modules.usuario.repository import UsuarioRepository

# -----------------------------------------------------------------------------
# Scheme
# -----------------------------------------------------------------------------

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")

# -----------------------------------------------------------------------------
# Excepciones reutilizables
# -----------------------------------------------------------------------------

_credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="No se pudieron validar las credenciales.",
    headers={"WWW-Authenticate": "Bearer"},
)

# -----------------------------------------------------------------------------
# Dependencias
# -----------------------------------------------------------------------------


def get_current_user(
    token: str = Depends(oauth2_scheme),
    session: Session = Depends(get_session),
) -> Usuario:
    """
    Decodifica el JWT y devuelve el usuario autenticado.

    Flujo:
    1. Decodifica el token con la clave secreta y el algoritmo configurado.
    2. Extrae el campo ``sub`` (email del usuario) del payload.
    3. Busca el usuario en la base de datos por email.
    4. Lanza 401 si el token es inválido, expirado o el usuario no existe.

    Args:
        token (str):
            Bearer token extraído del header ``Authorization``.
        session (Session):
            Sesión de base de datos inyectada.

    Returns:
        Usuario:
            Usuario correspondiente al token.

    Raises:
        HTTPException 401:
            Token inválido, expirado, o usuario no encontrado.
    """

    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
        )

        email: str | None = payload.get("sub")

        if email is None:
            raise _credentials_exception

    except JWTError:
        raise _credentials_exception

    repository = UsuarioRepository(session)
    usuario = repository.get_by_email(email)

    if usuario is None:
        raise _credentials_exception

    return usuario


def get_current_active_user(
    current_user: Usuario = Depends(get_current_user),
) -> Usuario:
    """
    Verifica que el usuario autenticado no esté eliminado (soft-delete).

    Args:
        current_user (Usuario):
            Usuario autenticado, inyectado desde ``get_current_user``.

    Returns:
        Usuario:
            El mismo usuario si está activo.

    Raises:
        HTTPException 400:
            El usuario fue eliminado (``deleted_at`` no es None).
    """

    if current_user.deleted_at is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Usuario inactivo.",
        )

    return current_user