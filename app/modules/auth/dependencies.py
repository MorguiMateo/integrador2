from fastapi import Depends, HTTPException, status

from app.core.deps import get_current_active_user, get_current_user
from app.modules.usuario.model import Usuario


def require_admin(
    current_user: Usuario = Depends(get_current_active_user),
) -> Usuario:
    if "ADMIN" not in current_user.roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required.",
        )

    return current_user
