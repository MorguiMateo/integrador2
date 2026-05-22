from fastapi import APIRouter, Depends, HTTPException, status

from app.core.uow import UnitOfWork
from app.modules.auth.dependencies import (
    get_current_active_user,
    require_admin,
)
from app.modules.usuario.model import Usuario
from app.modules.usuario.schemas import (
    UserCreate,
    UserPublic,
)
from app.modules.usuario.service import (
    create_usuario,
    get_usuario,
    list_usuarios,
)

router = APIRouter(
    prefix="/usuarios",
    tags=["Usuarios"],
)


# -----------------------------------------------------------------------------
# Registro publico
# -----------------------------------------------------------------------------

@router.post(
    "/",
    response_model=UserPublic,
    status_code=status.HTTP_201_CREATED,
)
def register_usuario(
    data: UserCreate,
    uow: UnitOfWork = Depends(),
):
    """
    Registro publico de usuarios.

    No requiere autenticacion.
    """

    with uow:
        usuario = create_usuario(
            uow=uow,
            data=data,
        )

        return usuario


# -----------------------------------------------------------------------------
# Usuario autenticado actual
# -----------------------------------------------------------------------------

@router.get(
    "/me",
    response_model=UserPublic,
)
def get_me(
    current_user: Usuario = Depends(get_current_active_user),
):
    """
    Devuelve el usuario autenticado actual.

    Requiere autenticacion.
    """

    return current_user


# -----------------------------------------------------------------------------
# Listado de usuarios
# -----------------------------------------------------------------------------

@router.get(
    "/",
    response_model=list[UserPublic],
)
def get_usuarios(
    skip: int = 0,
    limit: int = 100,
    uow: UnitOfWork = Depends(),
    _: Usuario = Depends(require_admin),
):
    """
    Lista usuarios.

    Requiere rol ADMIN.
    """

    with uow:
        return list_usuarios(
            uow=uow,
            skip=skip,
            limit=limit,
        )


# -----------------------------------------------------------------------------
# Detalle de usuario
# -----------------------------------------------------------------------------

@router.get(
    "/{usuario_id}",
    response_model=UserPublic,
)
def get_usuario_by_id(
    usuario_id: int,
    uow: UnitOfWork = Depends(),
    _: Usuario = Depends(get_current_active_user),
):
    """
    Obtiene detalle de usuario.

    Requiere autenticacion.
    """

    with uow:
        usuario = get_usuario(
            uow=uow,
            usuario_id=usuario_id,
        )

        if not usuario:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuario not found.",
            )

        return usuario


# -----------------------------------------------------------------------------
# Gestion de roles
# -----------------------------------------------------------------------------

@router.patch(
    "/{usuario_id}/roles",
    response_model=UserPublic,
)
def update_usuario_roles(
    usuario_id: int,
    _: Usuario = Depends(require_admin),
):
    """
    Asigna o remueve roles de usuario.

    Requiere rol ADMIN.
    """

    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Role management not implemented yet.",
    )
