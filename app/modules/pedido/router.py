from __future__ import annotations

from typing import Annotated, Optional

from fastapi import APIRouter, Depends, Path, Query, WebSocket, WebSocketDisconnect, status

from app.core.deps import get_current_active_user
from app.core.websocket import get_current_websocket_user, manager
from app.modules.pedido import service
from app.modules.pedido.schema import (
    AvanzarEstadoRequest,
    CancelarPedidoRequest,
    DetallePedidoRead,
    HistorialRead,
    PedidoCreate,
    PedidoRead,
)
from app.modules.usuario.model import Usuario

router = APIRouter(prefix="/pedidos", tags=["pedidos"])


@router.post(
    "",
    response_model=PedidoRead,
    status_code=status.HTTP_201_CREATED,
)
def crear_pedido(
    payload: PedidoCreate,
    current_user: Usuario = Depends(get_current_active_user),
) -> PedidoRead:
    return service.create_pedido(payload, current_user.id)


@router.get(
    "",
    response_model=list[PedidoRead],
)
def listar_pedidos(
    current_user: Usuario = Depends(get_current_active_user),
    skip: Annotated[int, Query(ge=0, description="Registros a saltar")] = 0,
    limit: Annotated[int, Query(ge=1, le=1000, description="Máximo por página")] = 50,
    estado: Annotated[Optional[str], Query(description="Filtrar por estado")] = None,
) -> list[PedidoRead]:
    return service.list_pedidos(
        current_user.id,
        current_user.roles,
        skip=skip,
        limit=limit,
        estado=estado,
    )


@router.get(
    "/{pedido_id}",
    response_model=PedidoRead,
)
def obtener_pedido(
    pedido_id: Annotated[int, Path(ge=1)],
    current_user: Usuario = Depends(get_current_active_user),
) -> PedidoRead:
    return service.get_pedido(pedido_id, current_user.id, current_user.roles)


@router.post(
    "/{pedido_id}/avanzar",
    response_model=PedidoRead,
)
def avanzar_estado(
    pedido_id: Annotated[int, Path(ge=1)],
    payload: AvanzarEstadoRequest,
    current_user: Usuario = Depends(get_current_active_user),
) -> PedidoRead:

    return service.avanzar_estado(
        pedido_id=pedido_id,
        estado_hacia=payload.estado_hacia,
        current_user=current_user,
        motivo=payload.motivo,
    )


@router.post(
    "/{pedido_id}/cancelar",
    response_model=PedidoRead,
)
def cancelar_pedido(
    pedido_id: Annotated[int, Path(ge=1)],
    payload: CancelarPedidoRequest,
    current_user: Usuario = Depends(get_current_active_user),
) -> PedidoRead:

    return service.cancelar_pedido(
        pedido_id=pedido_id,
        current_user=current_user,
        motivo=payload.motivo,
    )


@router.get(
    "/{pedido_id}/detalles",
    response_model=list[DetallePedidoRead],
)
def listar_detalles(
    pedido_id: Annotated[int, Path(ge=1)],
    current_user: Usuario = Depends(get_current_active_user),
) -> list[DetallePedidoRead]:
    return service.list_detalles(pedido_id, current_user.id, current_user.roles)


@router.get(
    "/{pedido_id}/historial",
    response_model=list[HistorialRead],
)
def listar_historial(
    pedido_id: Annotated[int, Path(ge=1)],
    current_user: Usuario = Depends(get_current_active_user),
) -> list[HistorialRead]:
    return service.list_historial(pedido_id, current_user.id, current_user.roles)


@router.websocket("/ws")
async def pedidos_ws(websocket: WebSocket) -> None:
    usuario = await get_current_websocket_user(websocket)
    await manager.connect(websocket, user_id=usuario.id, roles=set(usuario.roles))
    try:
        while True:
            await websocket.receive()
    except WebSocketDisconnect:
        pass
    finally:
        manager.disconnect(websocket)
