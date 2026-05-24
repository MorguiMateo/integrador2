from __future__ import annotations
from decimal import Decimal
from typing import Optional
from fastapi import HTTPException
from sqlmodel import select

from app.core.uow import UnitOfWork
from app.modules.pedido.model import Pedido, DetallePedido, HistorialEstadoPedido
from app.modules.pedido.schema import DetallePedidoRead, HistorialRead, PedidoCreate, PedidoRead
from app.modules.producto.model import Producto


FSM_TRANSITIONS = {
    "PENDIENTE":  ["CONFIRMADO", "CANCELADO"],
    "CONFIRMADO": ["EN_PREP", "CANCELADO"],
    "EN_PREP":    ["EN_CAMINO"],
    "EN_CAMINO":  ["ENTREGADO"],
    "ENTREGADO":  [],
    "CANCELADO":  [],
}


def _puede_ver_todos(roles) -> bool:
    return any(r in roles for r in ("ADMIN", "PEDIDOS"))


def create_pedido(data: PedidoCreate, usuario_id: int) -> PedidoRead:
    with UnitOfWork() as uow:
        detalles = []
        for item in data.items:
            producto = uow.session.get(Producto, item.producto_id)
            if producto is None:
                raise HTTPException(status_code=422, detail=f"Producto {item.producto_id} no encontrado")
            detalles.append(DetallePedido(
                producto_id=item.producto_id,
                cantidad=item.cantidad,
                nombre_snapshot=producto.nombre,
                precio_snapshot=producto.precio_base,
                subtotal_snap=producto.precio_base * item.cantidad,
                personalizacion=item.personalizacion or [],
            ))

        subtotal = sum(d.subtotal_snap for d in detalles)
        descuento = Decimal("0.00")
        costo_envio = Decimal("50.00")

        pedido = Pedido(
            usuario_id=usuario_id,
            direccion_id=data.direccion_id,
            forma_pago_codigo=data.forma_pago_codigo,
            notas=data.notas,
            subtotal=subtotal,
            descuento=descuento,
            costo_envio=costo_envio,
            total=subtotal - descuento + costo_envio,
        )
        uow.session.add(pedido)
        uow.session.flush()

        for det in detalles:
            det.pedido_id = pedido.id
            uow.session.add(det)

        uow.session.add(HistorialEstadoPedido(
            pedido_id=pedido.id, estado_desde=None, estado_hacia="PENDIENTE", usuario_id=usuario_id,
        ))
        uow.session.flush()
        return PedidoRead.model_validate(pedido)


def list_pedidos(usuario_id: int, roles) -> list[PedidoRead]:
    with UnitOfWork() as uow:
        stmt = select(Pedido).where(Pedido.deleted_at.is_(None))
        if not _puede_ver_todos(roles):
            stmt = stmt.where(Pedido.usuario_id == usuario_id)
        pedidos = uow.session.exec(stmt).all()
        return [PedidoRead.model_validate(p) for p in pedidos]


def get_pedido(pedido_id: int, usuario_id: int, roles) -> PedidoRead:
    with UnitOfWork() as uow:
        pedido = uow.session.get(Pedido, pedido_id)
        if pedido is None:
            raise HTTPException(status_code=404, detail="Pedido no encontrado")
        if not _puede_ver_todos(roles) and pedido.usuario_id != usuario_id:
            raise HTTPException(status_code=403, detail="Sin acceso a este pedido")
        return PedidoRead.model_validate(pedido)


def avanzar_estado(pedido_id: int, estado_hacia: str, usuario_id: int, motivo: Optional[str]) -> PedidoRead:
    with UnitOfWork() as uow:
        pedido = uow.session.get(Pedido, pedido_id)
        if pedido is None:
            raise HTTPException(status_code=404, detail="Pedido no encontrado")
        if estado_hacia not in FSM_TRANSITIONS[pedido.estado_codigo]:
            raise HTTPException(status_code=422, detail=f"Transicion invalida: {pedido.estado_codigo} -> {estado_hacia}")
        if estado_hacia == "CANCELADO" and motivo is None:
            raise HTTPException(status_code=422, detail="Motivo obligatorio para cancelar el pedido")

        estado_anterior = pedido.estado_codigo
        pedido.estado_codigo = estado_hacia
        uow.session.add(pedido)
        uow.session.add(HistorialEstadoPedido(
            pedido_id=pedido.id, estado_desde=estado_anterior, estado_hacia=estado_hacia,
            usuario_id=usuario_id, motivo=motivo,
        ))
        uow.session.flush()
        return PedidoRead.model_validate(pedido)


def list_detalles(pedido_id: int) -> list[DetallePedidoRead]:
    with UnitOfWork() as uow:
        pedido = uow.session.get(Pedido, pedido_id)
        if pedido is None:
            raise HTTPException(status_code=404, detail="Pedido no encontrado")
        return [DetallePedidoRead.model_validate(d) for d in pedido.detalles]


def list_historial(pedido_id: int) -> list[HistorialRead]:
    with UnitOfWork() as uow:
        pedido = uow.session.get(Pedido, pedido_id)
        if pedido is None:
            raise HTTPException(status_code=404, detail="Pedido no encontrado")
        return [HistorialRead.model_validate(h) for h in pedido.historial]
