from __future__ import annotations
import hashlib
import secrets
from datetime import datetime, timedelta, timezone
from jose import jwt
from app.core.config import settings
from app.modules.refresh_token.model import RefreshToken
from app.modules.refresh_token.repository import RefreshTokenRepository
from app.modules.usuario.model import Usuario
from typing import Optional

# -----------------------------------------------------------------------------
# Access Token
# -----------------------------------------------------------------------------


def create_access_token(
    data: dict,
    expires_delta: Optional[timedelta] = None,
) -> str:

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

    token_hash = hashlib.sha256(token_raw.encode()).hexdigest()

    repository = RefreshTokenRepository(uow.session)
    record = repository.get_by_hash(token_hash)

    if not record:
        raise ValueError("Refresh token inválido, expirado o ya revocado.")

    repository.revoke(record)

    return issue_tokens(uow, record.usuario)