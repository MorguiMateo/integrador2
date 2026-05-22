import hashlib

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from app.core.deps import get_current_active_user
from app.core.uow import UnitOfWork
from app.modules.auth.schema import RefreshRequest, Token
from app.modules.auth.service import issue_tokens, revoke_refresh_token, rotate_refresh_token
from app.modules.usuario.model import Usuario
from app.modules.usuario.service import authenticate_user

router = APIRouter(
    prefix="/auth",
    tags=["Auth"],
)


# -----------------------------------------------------------------------------
# Login
# -----------------------------------------------------------------------------

@router.post(
    "/token",
    response_model=Token,
)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    uow: UnitOfWork = Depends(),
):
    """
    Autentica al usuario y emite access + refresh token.

    Recibe credenciales como form-data (OAuth2 estándar):
    - ``username``: email del usuario.
    - ``password``: contraseña en texto plano.

    Seguridad:
    El mensaje de error es siempre el mismo independientemente
    de si el email no existe o la contraseña es incorrecta.
    Esto evita la enumeración de usuarios registrados.
    """

    with uow:
        usuario = authenticate_user(
            uow=uow,
            email=form_data.username,
            password=form_data.password,
        )

        if not usuario:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Credenciales incorrectas.",
                headers={"WWW-Authenticate": "Bearer"},
            )

        tokens = issue_tokens(uow=uow, usuario=usuario)

        return tokens


# -----------------------------------------------------------------------------
# Refresh
# -----------------------------------------------------------------------------

@router.post(
    "/refresh",
    response_model=Token,
)
def refresh(
    body: RefreshRequest,
    uow: UnitOfWork = Depends(),
):
    """
    Rota el refresh token y emite un nuevo par de tokens.

    Recibe el ``refresh_token`` raw en el body JSON.

    Si el token es inválido, expirado o ya fue revocado
    devuelve 401. Esto también cubre el caso de replay attack:
    un token robado y ya rotado será rechazado.
    """

    with uow:
        try:
            tokens = rotate_refresh_token(
                uow=uow,
                token_raw=body.refresh_token,
            )
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Refresh token inválido o expirado.",
                headers={"WWW-Authenticate": "Bearer"},
            )

        return tokens


# -----------------------------------------------------------------------------
# Logout
# -----------------------------------------------------------------------------

@router.post(
    "/logout",
    status_code=status.HTTP_204_NO_CONTENT,
)
def logout(
    body: RefreshRequest,
    uow: UnitOfWork = Depends(),
    _: Usuario = Depends(get_current_active_user),
):
    """
    Revoca el refresh token del cliente.

    Requiere autenticación (access token válido en header)
    y el ``refresh_token`` raw en el body JSON.

    Si el token ya estaba revocado o no existe
    devuelve 204 igualmente — no hay información útil
    que darle a un posible atacante.
    """

    token_hash = hashlib.sha256(body.refresh_token.encode()).hexdigest()

    with uow:
        revoke_refresh_token(uow=uow, token_hash=token_hash)