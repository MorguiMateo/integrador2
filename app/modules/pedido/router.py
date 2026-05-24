from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, Path, status

from app.modules.auth.dependencies import get_current_active_user
from app.modules.pedido import service
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
def crear_pedido(payload: PedidoCreate, current_user: Usuario = Depends(get_current_active_user)) -> PedidoRead:
    return service.create_pedido(payload, current_user.id)


@router.get("", response_model=list[PedidoRead])
def listar_pedidos(current_user: Usuario = Depends(get_current_active_user)) -> list[PedidoRead]:
    return service.list_pedidos(current_user.id, current_user.roles)


@router.get("/{pedido_id}", response_model=PedidoRead)
def obtener_pedido(pedido_id: Annotated[int, Path(ge=1)], current_user: Usuario = Depends(get_current_active_user)) -> PedidoRead:
    return service.get_pedido(pedido_id, current_user.id, current_user.roles)


@router.post("/{pedido_id}/avanzar", response_model=PedidoRead)
def avanzar_estado(pedido_id: Annotated[int, Path(ge=1)], payload: AvanzarEstadoRequest, current_user: Usuario = Depends(get_current_active_user)) -> PedidoRead:
    return service.avanzar_estado(pedido_id, payload.estado_hacia, current_user.id, payload.motivo)


@router.get("/{pedido_id}/detalles", response_model=list[DetallePedidoRead])
def listar_detalles(pedido_id: Annotated[int, Path(ge=1)], current_user: Usuario = Depends(get_current_active_user)) -> list[DetallePedidoRead]:
    return service.list_detalles(pedido_id)


@router.get("/{pedido_id}/historial", response_model=list[HistorialRead])
def listar_historial(pedido_id: Annotated[int, Path(ge=1)], current_user: Usuario = Depends(get_current_active_user)) -> list[HistorialRead]:
    return service.list_historial(pedido_id)
