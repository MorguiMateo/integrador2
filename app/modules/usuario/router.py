from fastapi import APIRouter, Depends, HTTPException, status

from app.core.uow import UnitOfWork
from app.modules.usuario.schemas import (
    UserCreate,
    UserPublic,
)
from app.modules.usuario.service import (
    create_usuario,
    get_usuario,
    list_usuarios,
)

# -----------------------------------------------------------------------------
# TODO:
# Estas dependencias deben implementarse en el módulo auth.
# Se dejan comentadas para evitar romper imports mientras
# el sistema de autenticación todavía no existe.
# -----------------------------------------------------------------------------

# from app.modules.auth.dependencies import (
#     get_current_active_user,
#     require_admin,
# )

router = APIRouter(
    prefix="/usuarios",
    tags=["Usuarios"],
)


# -----------------------------------------------------------------------------
# Registro público
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
    Registro público de usuarios.

    No requiere autenticación.
    """

    with uow:
        usuario = create_usuario(
            uow=uow,
            data=data,
        )

        uow.commit()

        return usuario


# -----------------------------------------------------------------------------
# Usuario autenticado actual
# -----------------------------------------------------------------------------

@router.get(
    "/me",
    response_model=UserPublic,
)
def get_me(
    # current_user = Depends(get_current_active_user),
):
    """
    Devuelve el usuario autenticado actual.

    Requiere autenticación.
    """

    # TODO:
    # Reemplazar cuando exista auth real.
    #
    # return current_user

    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Authentication system not implemented yet.",
    )


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

    # _: Usuario = Depends(require_admin),
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

    # current_user = Depends(get_current_active_user),
):
    """
    Obtiene detalle de usuario.

    Requiere autenticación.
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
# Gestión de roles
# -----------------------------------------------------------------------------

@router.patch(
    "/{usuario_id}/roles",
    response_model=UserPublic,
)
def update_usuario_roles(
    usuario_id: int,

    # _: Usuario = Depends(require_admin),
):
    """
    Asigna o remueve roles de usuario.

    Requiere rol ADMIN.
    """

    # TODO:
    # Implementar lógica de roles.
    # Depende de:
    # - UsuarioRol
    # - Rol
    # - auth/permissions

    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Role management not implemented yet.",
    )