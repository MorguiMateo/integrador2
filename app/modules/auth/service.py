from __future__ import annotations

import hashlib
import secrets
from datetime import datetime, timedelta, timezone

from jose import jwt

from app.core.config import settings
from app.modules.refresh_token.model import RefreshToken
from app.modules.refresh_token.repository import RefreshTokenRepository
from app.modules.usuario.model import Usuario

# -----------------------------------------------------------------------------
# Access Token
# -----------------------------------------------------------------------------


def create_access_token(
    data: dict,
    expires_delta: timedelta | None = None,
) -> str:
    """
    Genera un JWT de acceso firmado con HS256.

    El payload incluye:
    - Los datos recibidos (``sub``, ``roles``, etc.)
    - ``exp``: fecha de expiración calculada desde utcnow()

    Args:
        data (dict):
            Payload base del token. Debe incluir ``sub`` (email).

        expires_delta (timedelta | None):
            Duración del token. Si es None se usa
            ``settings.ACCESS_TOKEN_EXPIRE_MINUTES``.

    Returns:
        str: JWT firmado.
    """

    payload = data.copy()

    delta = expires_delta or timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )

    expire = datetime.utcnow() + delta

    payload.update({"exp": expire})

    return jwt.encode(
        payload,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM,
    )


# -----------------------------------------------------------------------------
# Refresh Token
# -----------------------------------------------------------------------------


def create_refresh_token() -> tuple[str, str]:
    """
    Genera un par (token_raw, token_hash) para refresh.

    Flujo:
    - ``token_raw``: 32 bytes aleatorios en base64 URL-safe.
      Se envía al cliente y NO se persiste.
    - ``token_hash``: SHA-256 de token_raw en hexadecimal.
      Es lo único que se almacena en DB.

    Returns:
        tuple[str, str]: (token_raw, token_hash)
    """

    token_raw = secrets.token_urlsafe(32)
    token_hash = hashlib.sha256(token_raw.encode()).hexdigest()

    return token_raw, token_hash


# -----------------------------------------------------------------------------
# Emisión combinada
# -----------------------------------------------------------------------------


def issue_tokens(
    uow,
    usuario: Usuario,
) -> dict:
    """
    Emite un access token y un refresh token para el usuario.

    Flujo:
    1. Crea el JWT con sub=email y roles del usuario.
    2. Genera el par (raw, hash) del refresh token.
    3. Persiste el RefreshToken en DB (sin commit).
    4. Devuelve ambos tokens para la respuesta HTTP.

    Args:
        uow:
            Unit of Work activo.

        usuario (Usuario):
            Usuario autenticado.

    Returns:
        dict:
            ``access_token``, ``refresh_token``, ``token_type``.
    """

    access_token = create_access_token(
        data={
            "sub": usuario.email,
            "roles": usuario.roles,
        }
    )

    token_raw, token_hash = create_refresh_token()

    expires_at = datetime.now(timezone.utc) + timedelta(
        days=settings.REFRESH_TOKEN_EXPIRE_DAYS
    )

    refresh_token_record = RefreshToken(
        usuario_id=usuario.id,
        token_hash=token_hash,
        expires_at=expires_at,
    )

    repository = RefreshTokenRepository(uow.session)
    repository.save(refresh_token_record)

    return {
        "access_token": access_token,
        "refresh_token": token_raw,
        "token_type": "bearer",
    }


# -----------------------------------------------------------------------------
# Revocación
# -----------------------------------------------------------------------------


def revoke_refresh_token(
    uow,
    token_hash: str,
) -> bool:
    """
    Revoca un RefreshToken buscándolo por su hash.

    Args:
        uow:
            Unit of Work activo.

        token_hash (str):
            Hash SHA-256 del token a revocar.

    Returns:
        bool:
            True si se encontró y revocó, False si no existía.
    """

    repository = RefreshTokenRepository(uow.session)
    record = repository.get_by_hash(token_hash)

    if not record:
        return False

    repository.revoke(record)

    return True


# -----------------------------------------------------------------------------
# Rotación
# -----------------------------------------------------------------------------


def rotate_refresh_token(
    uow,
    token_raw: str,
) -> dict:
    """
    Invalida el refresh token actual y emite uno nuevo.

    Implementa refresh token rotation:
    - Si el token no existe, está expirado o ya fue revocado → 401.
    - Si es válido → se revoca y se emiten tokens frescos.

    Esto detecta reutilización de tokens robados:
    un token revocado que se intenta usar de nuevo
    indica posible replay attack.

    Args:
        uow:
            Unit of Work activo.

        token_raw (str):
            Token raw enviado por el cliente.

    Returns:
        dict:
            ``access_token``, ``refresh_token``, ``token_type``.

    Raises:
        ValueError:
            Si el token no es válido o ya fue revocado.
    """

    token_hash = hashlib.sha256(token_raw.encode()).hexdigest()

    repository = RefreshTokenRepository(uow.session)
    record = repository.get_by_hash(token_hash)

    if not record:
        raise ValueError("Refresh token inválido, expirado o ya revocado.")

    repository.revoke(record)

    return issue_tokens(uow, record.usuario)