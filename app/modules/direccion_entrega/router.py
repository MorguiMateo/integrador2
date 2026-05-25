from typing import Annotated

from fastapi import APIRouter, Depends, Path, status

from app.core.deps import get_current_active_user
from app.core.uow import UnitOfWork
from app.modules.direccion_entrega.schema import (
    DireccionCreate,
    DireccionPublic,
    DireccionUpdate,
)
from app.modules.direccion_entrega.service import (
    create_direccion,
    delete_direccion,
    list_direcciones,
    set_principal,
    update_direccion,
)
from app.modules.usuario.model import Usuario


router = APIRouter(
    prefix="/direcciones",
    tags=["Direcciones"],
)


@router.get(
    "",
    response_model=list[DireccionPublic],
)
def get_direcciones(
    uow: UnitOfWork = Depends(),
    current_user: Usuario = Depends(get_current_active_user),
):

    with uow:
        return list_direcciones(uow=uow, usuario_id=current_user.id)


@router.post(
    "",
    response_model=DireccionPublic,
    status_code=status.HTTP_201_CREATED,
)
def add_direccion(
    data: DireccionCreate,
    uow: UnitOfWork = Depends(),
    current_user: Usuario = Depends(get_current_active_user),
):

    with uow:
        return create_direccion(uow=uow, usuario_id=current_user.id, data=data)


@router.put(
    "/{direccion_id}",
    response_model=DireccionPublic,
)
def edit_direccion(
    direccion_id: Annotated[int, Path(ge=1)],
    data: DireccionUpdate,
    uow: UnitOfWork = Depends(),
    current_user: Usuario = Depends(get_current_active_user),
):
    with uow:
        return update_direccion(
            uow=uow,
            usuario_id=current_user.id,
            direccion_id=direccion_id,
            data=data,
        )


@router.delete(
    "/{direccion_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def remove_direccion(
    direccion_id: Annotated[int, Path(ge=1)],
    uow: UnitOfWork = Depends(),
    current_user: Usuario = Depends(get_current_active_user),
):
    with uow:
        delete_direccion(
            uow=uow,
            usuario_id=current_user.id,
            direccion_id=direccion_id,
        )


@router.patch(
    "/{direccion_id}/principal",
    response_model=DireccionPublic,
)
def mark_as_principal(
    direccion_id: Annotated[int, Path(ge=1)],
    uow: UnitOfWork = Depends(),
    current_user: Usuario = Depends(get_current_active_user),
):
    with uow:
        return set_principal(
            uow=uow,
            usuario_id=current_user.id,
            direccion_id=direccion_id,
        )
