from typing import Optional

from fastapi import APIRouter, Cookie, Depends, HTTPException, Request, Response, status
from jose import JWTError

from app.core.config import settings
from app.core.deps import (
    ACCESS_COOKIE_NAME,
    REFRESH_COOKIE_NAME,
    get_current_active_user,
)
from app.core.rate_limit import get_client_ip, login_rate_limiter
from app.core.uow import UnitOfWork
from app.modules.auth.schema import LoginRequest, RegisterRequest
from app.modules.auth.service import (
    create_access_token,
    create_refresh_token,
    decode_refresh_token,
)
from app.modules.usuario.model import Usuario
from app.modules.usuario.schemas import UserCreate, UserPublic, UserUpdate
from app.modules.usuario.service import (
    authenticate_user,
    create_usuario,
    update_usuario,
)


router = APIRouter(
    prefix="/auth",
    tags=["Auth"],
)


def _set_access_cookie(response: Response, token: str) -> None:
    response.set_cookie(
        key=ACCESS_COOKIE_NAME,
        value=token,
        httponly=True,
        samesite="lax",
        secure=False,
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        path="/",
    )


def _set_refresh_cookie(response: Response, token: str) -> None:
    response.set_cookie(
        key=REFRESH_COOKIE_NAME,
        value=token,
        httponly=True,
        samesite="lax",
        secure=False,
        max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
        path="/",
    )


@router.post(
    "/register",
    response_model=UserPublic,
    status_code=status.HTTP_201_CREATED,
)
def register(
    data: RegisterRequest,
    request: Request,
    uow: UnitOfWork = Depends(),
):
    ip = get_client_ip(request)
    login_rate_limiter.enforce(ip)
    try:
        with uow:
            return create_usuario(
                uow=uow,
                data=UserCreate(**data.model_dump()),
            )
    except Exception:
        ##si el registro falla (ej: email repetido) tambien cuenta como intento fallido
        login_rate_limiter.record_failure(ip)
        raise


@router.post(
    "/login",
    response_model=UserPublic,
)
def login(
    data: LoginRequest,
    response: Response,
    request: Request,
    uow: UnitOfWork = Depends(),
):
    ip = get_client_ip(request)
    login_rate_limiter.enforce(ip)

    with uow:
        usuario = authenticate_user(
            uow=uow,
            email=data.email,
            password=data.password,
        )

        if not usuario:
            login_rate_limiter.record_failure(ip)
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Credenciales incorrectas.",
            )

        _set_access_cookie(response, create_access_token(usuario))
        _set_refresh_cookie(response, create_refresh_token(usuario))

        return usuario


@router.post(
    "/refresh",
    response_model=UserPublic,
)
def refresh(
    response: Response,
    refresh_token: Optional[str] = Cookie(default=None, alias=REFRESH_COOKIE_NAME),
    uow: UnitOfWork = Depends(),
):
    if not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No hay refresh token.",
        )

    try:
        email = decode_refresh_token(refresh_token)
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token inválido o expirado.",
        )

    with uow:
        usuario = uow.usuarios.get_by_email(email)
        if usuario is None or usuario.deleted_at is not None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Usuario inválido.",
            )

        _set_access_cookie(response, create_access_token(usuario))

        return usuario



@router.post(
    "/logout",
    status_code=status.HTTP_204_NO_CONTENT,
)
def logout(
    response: Response,
    _: Usuario = Depends(get_current_active_user),
):
    response.delete_cookie(key=ACCESS_COOKIE_NAME, path="/")
    response.delete_cookie(key=REFRESH_COOKIE_NAME, path="/")



@router.get(
    "/me",
    response_model=UserPublic,
)
def me(
    current_user: Usuario = Depends(get_current_active_user),
):
    return current_user


@router.patch(
    "/me",
    response_model=UserPublic,
)
def update_me(
    data: UserUpdate,
    current_user: Usuario = Depends(get_current_active_user),
    uow: UnitOfWork = Depends(),
):
    with uow:
        return update_usuario(
            uow=uow,
            usuario_id=current_user.id,
            data=data,
        )
