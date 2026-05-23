from __future__ import annotations
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Path, status
from sqlmodel import select

from app.core.uow import UnitOfWork
from app.modules.auth.dependencies import get_current_active_user
from app.modules.pedido import service
from app.modules.pedido.model import Pedido
from app.modules.pedido.schema import (
    AvanzarEstadoRequest,
    DetallePedidoRead,
    HistorialRead,
    PedidoCreate,
    PedidoRead,
)
from app.modules.usuario.model import Usuario

router = APIRouter(prefix="/pedidos", tags=["pedidos"])


@router.post("", response_model=PedidoRead, status_code=status.HTTP_201_CREATED)
def crear_pedido(
    payload: PedidoCreate,
    current_user: Usuario = Depends(get_current_active_user),
):
    try:
        with UnitOfWork() as uow:
            return service.create_pedido(uow, payload, current_user.id)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))


@router.get("", response_model=list[PedidoRead])
def listar_pedidos(
    current_user: Usuario = Depends(get_current_active_user),
):
    with UnitOfWork() as uow:
        stmt = select(Pedido).where(Pedido.deleted_at.is_(None))

        es_admin_o_pedidos = any(r in current_user.roles for r in ("ADMIN", "PEDIDOS"))
        if not es_admin_o_pedidos:
            stmt = stmt.where(Pedido.usuario_id == current_user.id)

        return uow.session.exec(stmt).all()


@router.get("/{pedido_id}", response_model=PedidoRead)
def obtener_pedido(
    pedido_id: Annotated[int, Path(ge=1)],
    current_user: Usuario = Depends(get_current_active_user),
):
    with UnitOfWork() as uow:
        pedido = uow.session.get(Pedido, pedido_id)
        if pedido is None:
            raise HTTPException(status_code=404, detail="Pedido no encontrado")

        if "ADMIN" not in current_user.roles and "PEDIDOS" not in current_user.roles:
            if pedido.usuario_id != current_user.id:
                raise HTTPException(status_code=403, detail="Sin acceso a este pedido")

        return pedido


@router.post("/{pedido_id}/avanzar", response_model=PedidoRead)
def avanzar_estado(
    pedido_id: Annotated[int, Path(ge=1)],
    payload: AvanzarEstadoRequest,
    current_user: Usuario = Depends(get_current_active_user),
):
    try:
        with UnitOfWork() as uow:
            return service.avanzar_estado(
                uow, pedido_id, payload.estado_hacia, current_user.id, payload.motivo
            )
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))


@router.get("/{pedido_id}/detalles", response_model=list[DetallePedidoRead])
def listar_detalles(
    pedido_id: Annotated[int, Path(ge=1)],
    current_user: Usuario = Depends(get_current_active_user),
):
    with UnitOfWork() as uow:
        pedido = uow.session.get(Pedido, pedido_id)
        if pedido is None:
            raise HTTPException(status_code=404, detail="Pedido nno encontrado")
        return pedido.detalles


@router.get("/{pedido_id}/historial", response_model=list[HistorialRead])
def listar_historial(
    pedido_id: Annotated[int, Path(ge=1)],
    current_user: Usuario = Depends(get_current_active_user),
):
    with UnitOfWork() as uow:
        pedido = uow.session.get(Pedido, pedido_id)
        if pedido is None:
            raise HTTPException(status_code=404, detail="Pedido no encontradoo")
        return pedido.historial
