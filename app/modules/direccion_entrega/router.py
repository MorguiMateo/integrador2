from fastapi import APIRouter, Depends, status

from app.core.deps import get_current_active_user
from app.core.uow import UnitOfWork
from app.modules.direccion_entrega.schema import DireccionCreate, DireccionPublic
from app.modules.direccion_entrega.service import (
    create_direccion,
    delete_direccion,
    set_principal,
    list_direcciones,
)
from app.modules.usuario.model import Usuario

router = APIRouter(
    prefix="/usuarios/{usuario_id}/direcciones",
    tags=["Direcciones"],
)


# -----------------------------------------------------------------------------
# Listar
# -----------------------------------------------------------------------------

@router.get(
    "/",
    response_model=list[DireccionPublic],
)
def get_direcciones(
    usuario_id: int,
    uow: UnitOfWork = Depends(),
    current_user: Usuario = Depends(get_current_active_user),
):
    """
    Lista las direcciones de entrega de un usuario.

    Requiere autenticación.
    Solo el propio usuario o un ADMIN pueden acceder.
    """

    with uow:
        return list_direcciones(
            uow=uow,
            usuario_id=usuario_id,
            current_user=current_user,
        )


# -----------------------------------------------------------------------------
# Crear
# -----------------------------------------------------------------------------

@router.post(
    "/",
    response_model=DireccionPublic,
    status_code=status.HTTP_201_CREATED,
)
def add_direccion(
    usuario_id: int,
    data: DireccionCreate,
    uow: UnitOfWork = Depends(),
    current_user: Usuario = Depends(get_current_active_user),
):
    """
    Agrega una dirección de entrega a un usuario.

    Si ``es_principal=true``, la dirección principal
    anterior queda desmarcada automáticamente.

    Requiere autenticación.
    Solo el propio usuario o un ADMIN pueden agregar.
    """

    with uow:
        direccion = create_direccion(
            uow=uow,
            usuario_id=usuario_id,
            data=data,
            current_user=current_user,
        )

        return direccion


# -----------------------------------------------------------------------------
# Eliminar
# -----------------------------------------------------------------------------

@router.delete(
    "/{direccion_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def remove_direccion(
    usuario_id: int,
    direccion_id: int,
    uow: UnitOfWork = Depends(),
    current_user: Usuario = Depends(get_current_active_user),
):
    """
    Elimina (soft-delete) una dirección de entrega.

    Requiere autenticación.
    Solo el propio usuario o un ADMIN pueden eliminar.
    """

    with uow:
        delete_direccion(
            uow=uow,
            usuario_id=usuario_id,
            direccion_id=direccion_id,
            current_user=current_user,
        )

# -----------------------------------------------------------------------------
# Marcar como principal
# -----------------------------------------------------------------------------

@router.patch(
    "/{direccion_id}/principal",
    response_model=DireccionPublic,
)
def mark_as_principal(
    usuario_id: int,
    direccion_id: int,
    uow: UnitOfWork = Depends(),
    current_user: Usuario = Depends(get_current_active_user),
):
    with uow:
        return set_principal(
            uow=uow,
            usuario_id=usuario_id,
            direccion_id=direccion_id,
            current_user=current_user,
        )
