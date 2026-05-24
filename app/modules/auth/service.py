from datetime import datetime, timedelta, timezone

from jose import jwt

from app.core.config import settings
from app.modules.usuario.model import Usuario


def create_access_token(usuario: Usuario) -> str:
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    payload = {
        "sub": usuario.email,
        "roles": usuario.roles,
        "exp": expire,
    }
    return jwt.encode(
        payload,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM,
    )
