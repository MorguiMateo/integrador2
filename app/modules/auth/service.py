from datetime import datetime, timedelta, timezone

from jose import JWTError, jwt

from app.core.config import settings
from app.modules.usuario.model import Usuario


def create_access_token(usuario: Usuario) -> str:
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    payload = {
        "sub": usuario.email,
        "roles": usuario.roles,
        "type": "access",
        "exp": expire,
    }
    return jwt.encode(
        payload,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM,
    )


def create_refresh_token(usuario: Usuario) -> str:
    expire = datetime.now(timezone.utc) + timedelta(
        days=settings.REFRESH_TOKEN_EXPIRE_DAYS
    )
    payload = {
        "sub": usuario.email,
        "type": "refresh",
        "exp": expire,
    }
    return jwt.encode(
        payload,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM,
    )


def decode_refresh_token(token: str) -> str:
    """
    Valida un refresh token y devuelve el email (claim `sub`).

    Lanza `JWTError` si el token está expirado, mal firmado, o no es de
    tipo `refresh` (p. ej. si intentan usar un access token acá).
    """
    payload = jwt.decode(
        token,
        settings.SECRET_KEY,
        algorithms=[settings.ALGORITHM],
    )
    if payload.get("type") != "refresh":
        raise JWTError("El token no es de tipo refresh.")
    email = payload.get("sub")
    if not email:
        raise JWTError("El token no contiene `sub`.")
    return email
