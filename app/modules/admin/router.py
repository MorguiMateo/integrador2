from typing import Annotated, Optional

from fastapi import APIRouter, Depends, Path, Query, status

from app.core.uow import UnitOfWork
from app.modules.admin import service
from app.modules.admin.schema import RolesUpdate, UsuarioAdminUpdate
from app.modules.auth.dependencies import require_admin
from app.modules.usuario.model import Usuario
from app.modules.usuario.schemas import UserPublic


router = APIRouter(
    prefix="/admin",
    tags=["Admin"],
    dependencies=[Depends(require_admin)],
)


@router.get(
    "/usuarios",
    response_model=list[UserPublic],
)
def listar_usuarios(
    skip: Annotated[int, Query(ge=0, description="Registros a saltar")] = 0,
    limit: Annotated[int, Query(ge=1, le=100, description="Máximo por página")] = 50,
    rol: Annotated[Optional[str], Query(description="Filtrar por código de rol")] = None,
    q: Annotated[Optional[str], Query(max_length=120, description="Búsqueda por email/nombre/apellido")] = None,
    uow: UnitOfWork = Depends(),
):
    with uow:
        return service.list_usuarios(uow, skip=skip, limit=limit, rol=rol, q=q)


@router.get(
    "/usuarios/{usuario_id}",
    response_model=UserPublic,
)
def obtener_usuario(
    usuario_id: Annotated[int, Path(ge=1)],
    uow: UnitOfWork = Depends(),
):
    with uow:
        return service.get_usuario(uow, usuario_id)


@router.put(
    "/usuarios/{usuario_id}",
    response_model=UserPublic,
)
def actualizar_usuario(
    usuario_id: Annotated[int, Path(ge=1)],
    payload: UsuarioAdminUpdate,
    uow: UnitOfWork = Depends(),
):
    with uow:
        return service.update_usuario(uow, usuario_id, payload)


@router.delete(
    "/usuarios/{usuario_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def eliminar_usuario(
    usuario_id: Annotated[int, Path(ge=1)],
    uow: UnitOfWork = Depends(),
    current_user: Usuario = Depends(require_admin),
):
    with uow:
        service.delete_usuario(uow, usuario_id, current_user_id=current_user.id)


@router.patch(
    "/usuarios/{usuario_id}/roles",
    response_model=UserPublic,
)
def asignar_roles(
    usuario_id: Annotated[int, Path(ge=1)],
    payload: RolesUpdate,
    uow: UnitOfWork = Depends(),
    current_user: Usuario = Depends(require_admin),
):
    with uow:
        return service.set_roles(
            uow,
            usuario_id,
            payload,
            current_user_id=current_user.id,
        )
