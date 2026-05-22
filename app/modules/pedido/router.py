from __future__ import annotations
from typing import Annotated
from fastapi import APIRouter, HTTPException, Path, status
from app.core.uow import UnitOfWork
from app.modules.pedido import service
from app.modules.pedido.schema import (PedidoCreate, PedidoRead,AvanzarEstadoRequest, DetallePedidoRead, HistorialRead)

router = APIRouter(prefix="/pedidos", tags=["pedidos"])

@router.post("", response_model=PedidoRead, status_code=status.HTTP_201_CREATED)
def crear_pedido(payload: PedidoCreate, usuario_id: int = 1):
    try:
        with UnitOfWork() as uow:
            return service.create_pedido(uow, payload, usuario_id)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    

@router.get("", response_model=list[PedidoRead])
def listar_pedidos():
    with UnitOfWork() as uow:
        
        from sqlmodel import select
        from app.modules.pedido.model import Pedido
        pedidos = uow.session.exec(select(Pedido)).all()
        return pedidos



@router.get("/{pedido_id}", response_model=PedidoRead)
def obtener_pedido(pedido_id: Annotated[int, Path(ge=1)]):
    with UnitOfWork() as uow:
        from app.modules.pedido.model import Pedido
        pedido = uow.session.get(Pedido, pedido_id)
        if pedido is None:
            raise HTTPException(status_code=404, detail="Pedido no encontrado")
        return pedido
    


@router.post("/{pedido_id}/avanzar", response_model=PedidoRead)
def avanzar_estado(pedido_id: Annotated[int, Path(ge=1)], payload: AvanzarEstadoRequest, usuario_id: int = 1):
    try:
        with UnitOfWork() as uow:
            return service.avanzar_estado(uow, pedido_id, payload.estado_hacia, usuario_id, payload.motivo)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    


@router.get("/{pedido_id}/detalles", response_model=list[DetallePedidoRead])
def listar_detalles(pedido_id: Annotated[int, Path(ge=1)]):
    with UnitOfWork() as uow:
        from app.modules.pedido.model import Pedido
        pedido = uow.session.get(Pedido, pedido_id)
        if pedido is None:
            raise HTTPException(status_code=404, detail="El pedidoo no se encontro")
        return pedido.detalles
    


@router.get("/{pedido_id}/historial", response_model=list[HistorialRead])
def listar_historial(pedido_id: Annotated[int, Path(ge=1)]):
    with UnitOfWork() as uow:
        from app.modules.pedido.model import Pedido
        pedido = uow.session.get(Pedido, pedido_id)
        if pedido is None:
            raise HTTPException(status_code=404, detail="El pedido nos sse encontro")
        return pedido.historial