from fastapi import APIRouter, Depends, HTTPException, Response, status

from app.core.config import settings
from app.core.deps import ACCESS_COOKIE_NAME, get_current_active_user
from app.core.uow import UnitOfWork
from app.modules.auth.schema import LoginRequest, RegisterRequest
from app.modules.auth.service import create_access_token
from app.modules.usuario.model import Usuario
from app.modules.usuario.schemas import UserCreate, UserPublic
from app.modules.usuario.service import authenticate_user, create_usuario


router = APIRouter(
    prefix="/auth",
    tags=["Auth"],
)


# -----------------------------------------------------------------------------
# Registro público — siempre asigna rol CLIENT
# -----------------------------------------------------------------------------

@router.post(
    "/register",
    response_model=UserPublic,
    status_code=status.HTTP_201_CREATED,
)
def register(
    data: RegisterRequest,
    uow: UnitOfWork = Depends(),
):
    with uow:
        return create_usuario(
            uow=uow,
            data=UserCreate(**data.model_dump()),
        )


# -----------------------------------------------------------------------------
# Login — setea cookie httpOnly con el JWT
# -----------------------------------------------------------------------------

@router.post(
    "/login",
    response_model=UserPublic,
)
def login(
    data: LoginRequest,
    response: Response,
    uow: UnitOfWork = Depends(),
):
    with uow:
        usuario = authenticate_user(
            uow=uow,
            email=data.email,
            password=data.password,
        )

        if not usuario:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Credenciales incorrectas.",
            )

        token = create_access_token(usuario)

        response.set_cookie(
            key=ACCESS_COOKIE_NAME,
            value=token,
            httponly=True,
            samesite="lax",
            secure=False,
            max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            path="/",
        )

        return usuario


# -----------------------------------------------------------------------------
# Logout — borra cookie
# -----------------------------------------------------------------------------

@router.post(
    "/logout",
    status_code=status.HTTP_204_NO_CONTENT,
)
def logout(
    response: Response,
    _: Usuario = Depends(get_current_active_user),
):
    response.delete_cookie(key=ACCESS_COOKIE_NAME, path="/")


# -----------------------------------------------------------------------------
# Usuario autenticado
# -----------------------------------------------------------------------------

@router.get(
    "/me",
    response_model=UserPublic,
)
def me(
    current_user: Usuario = Depends(get_current_active_user),
):
    return current_user
