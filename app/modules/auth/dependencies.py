from typing import Iterable

from fastapi import Depends, HTTPException, status

from app.core.deps import get_current_active_user, get_current_user
from app.modules.usuario.model import Usuario


def _ensure_roles(usuario: Usuario, allowed: Iterable[str]) -> None:
    allowed_set = set(allowed)
    if not allowed_set.intersection(usuario.roles):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permisos insuficientes para esta operación.",
        )


def require_roles(*allowed: str):

    def _dependency(
        current_user: Usuario = Depends(get_current_active_user),
    ) -> Usuario:
        _ensure_roles(current_user, allowed)
        return current_user

    return _dependency


def require_admin(
    current_user: Usuario = Depends(get_current_active_user),
) -> Usuario:
    _ensure_roles(current_user, ["ADMIN"])
    return current_user


def require_admin_or_stock(
    current_user: Usuario = Depends(get_current_active_user),
) -> Usuario:
    _ensure_roles(current_user, ["ADMIN", "STOCK"])
    return current_user


def require_admin_or_pedidos(
    current_user: Usuario = Depends(get_current_active_user),
) -> Usuario:
    _ensure_roles(current_user, ["ADMIN", "PEDIDOS"])
    return current_user
