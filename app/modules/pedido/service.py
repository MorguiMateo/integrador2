from __future__ import annotations

from decimal import Decimal
from typing import Iterable, Optional

from fastapi import HTTPException
from sqlmodel import select

from app.core.uow import UnitOfWork
from app.core.websocket import manager as websocket_manager
from app.modules.pedido.model import DetallePedido, HistorialEstadoPedido, Pedido
from app.modules.pedido.schema import (
    DetallePedidoRead,
    HistorialRead,
    PedidoCreate,
    PedidoRead,
)
from app.modules.producto.model import Producto
from app.modules.usuario.model import Usuario


FSM_TRANSITIONS = {
    "PENDIENTE": ["CONFIRMADO", "CANCELADO"],
    "CONFIRMADO": ["EN_PREP", "CANCELADO"],
    # Desde cocina (EN_PREP) el pedido se entrega o se cancela. Se eliminó EN_CAMINO.
    "EN_PREP": ["ENTREGADO", "CANCELADO"],
    "ENTREGADO": [],
    "CANCELADO": [],
}

ROLES_GESTION_PEDIDOS = {"ADMIN", "PEDIDOS"}
ESTADOS_CANCELABLES_POR_CLIENTE = {"PENDIENTE", "CONFIRMADO"}


def _puede_ver_todos(roles: Iterable[str]) -> bool:
    return any(r in ROLES_GESTION_PEDIDOS for r in roles)


def _puede_avanzar(roles: Iterable[str]) -> bool:
    return any(r in ROLES_GESTION_PEDIDOS for r in roles)


def _assert_puede_ver(pedido: Pedido, current_user_id: int, roles: Iterable[str]) -> None:
    if _puede_ver_todos(roles):
        return
    if pedido.usuario_id != current_user_id:
        raise HTTPException(status_code=403, detail="Sin acceso a este pedido")


def create_pedido(data: PedidoCreate, usuario_id: int) -> PedidoRead:
    with UnitOfWork() as uow:
        detalles: list[DetallePedido] = []

        for item in data.items:

            # with_for_update bloquea la fila del producto hasta el commit del
            # pedido, así dos checkouts simultáneos del mismo producto se
            # serializan y no se puede sobrevender el stock.

            producto = uow.session.get(Producto, item.producto_id, with_for_update=True)
            if producto is None or producto.deleted_at is not None:
                raise HTTPException(
                    status_code=422,
                    detail=f"Producto {item.producto_id} no encontrado",
                )
            if not producto.disponible:
                raise HTTPException(
                    status_code=409,
                    detail=f"Producto '{producto.nombre}' no está disponible.",
                )
            if producto.stock_cantidad < item.cantidad:
                raise HTTPException(
                    status_code=409,
                    detail=(
                        f"Stock insuficiente para '{producto.nombre}': "
                        f"disponible {producto.stock_cantidad}, solicitado {item.cantidad}."
                    ),
                )

            precio_unit = Decimal(str(producto.precio_base))
            subtotal_item = precio_unit * item.cantidad
            producto.stock_cantidad -= item.cantidad
            uow.session.add(producto)

            detalles.append(
                DetallePedido(
                    producto_id=item.producto_id,
                    cantidad=item.cantidad,
                    nombre_snapshot=producto.nombre,
                    precio_snapshot=precio_unit,
                    subtotal_snap=subtotal_item,
                    personalizacion=item.personalizacion or [],
                )
            )

        subtotal = sum((d.subtotal_snap for d in detalles), Decimal("0.00"))
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

        uow.session.add(
            HistorialEstadoPedido(
                pedido_id=pedido.id,
                estado_desde=None,
                estado_hacia="PENDIENTE",
                usuario_id=usuario_id,
            )
        )
        uow.session.flush()
        pedido_read = PedidoRead.model_validate(pedido)

    websocket_manager.broadcast(
        {
            "event": "ORDER_CREATED",
            "pedido_id": pedido_read.id,
            "owner_id": pedido_read.usuario_id,
            "estado": pedido_read.estado_codigo,
            "usuario_id": pedido_read.usuario_id,
        }
    )
    return pedido_read


def list_pedidos(
    usuario_id: int,
    roles: Iterable[str],
    *,
    skip: int = 0,
    limit: int = 50,
    estado: Optional[str] = None,
) -> list[PedidoRead]:
    with UnitOfWork() as uow:
        stmt = select(Pedido).where(Pedido.deleted_at.is_(None))
        if not _puede_ver_todos(roles):
            stmt = stmt.where(Pedido.usuario_id == usuario_id)
        if estado:
            stmt = stmt.where(Pedido.estado_codigo == estado)

        # Orden estable y determinista: sin esto, PostgreSQL reordena las filas
        # tras cada UPDATE y en la tabla del admin los pedidos "saltan" de lugar.
        stmt = stmt.order_by(Pedido.created_at.desc(), Pedido.id.desc()).offset(skip).limit(limit)
        stmt = (
            stmt.order_by(Pedido.created_at.desc(), Pedido.id.desc())
            .offset(skip)
            .limit(limit)
        )
        pedidos = uow.session.exec(stmt).all()
        return [PedidoRead.model_validate(p) for p in pedidos]


def get_pedido(pedido_id: int, usuario_id: int, roles: Iterable[str]) -> PedidoRead:
    with UnitOfWork() as uow:
        pedido = uow.session.get(Pedido, pedido_id)
        if pedido is None:
            raise HTTPException(status_code=404, detail="Pedido no encontrado")
        _assert_puede_ver(pedido, usuario_id, roles)
        return PedidoRead.model_validate(pedido)



def _reponer_stock(uow: UnitOfWork, pedido: Pedido) -> None:
    """Devuelve al stock las cantidades de cada línea del pedido."""

def _reponer_stock(uow, pedido: Pedido) -> None:

    for det in pedido.detalles:
        producto = uow.session.get(Producto, det.producto_id, with_for_update=True)
        if producto is not None:
            producto.stock_cantidad += det.cantidad
            uow.session.add(producto)


def _aplicar_transicion(
    uow: UnitOfWork,
    pedido: Pedido,
    estado_hacia: str,
    usuario_id: Optional[int],
    motivo: Optional[str],
) -> Pedido:

    siguientes = FSM_TRANSITIONS.get(pedido.estado_codigo)
    if not siguientes or estado_hacia not in siguientes:
        raise HTTPException(
            status_code=422,
            detail=f"Transicion invalida: {pedido.estado_codigo} -> {estado_hacia}",
        )

    if estado_hacia == "CANCELADO":
        _reponer_stock(uow, pedido)

    estado_anterior = pedido.estado_codigo
    pedido.estado_codigo = estado_hacia

    uow.session.add(pedido)
    uow.session.add(
        HistorialEstadoPedido(
            pedido_id=pedido.id,
            estado_desde=estado_anterior,
            estado_hacia=estado_hacia,
            usuario_id=usuario_id,
            motivo=motivo,
        )
    )
    uow.session.flush()
    return pedido


def avanzar_estado(
    pedido_id: int,
    estado_hacia: str,
    current_user: Usuario,
    motivo: Optional[str],
) -> PedidoRead:
    if not _puede_avanzar(current_user.roles):
        raise HTTPException(
            status_code=403,
            detail="Solo ADMIN o PEDIDOS pueden avanzar el estado del pedido.",
        )

    if estado_hacia == "CANCELADO" and not motivo:
        raise HTTPException(
            status_code=422,
            detail="Motivo obligatorio para cancelar el pedido.",
        )

    pedido_read: Optional[PedidoRead] = None
    estado_anterior: Optional[str] = None

    with UnitOfWork() as uow:
        pedido = uow.session.get(Pedido, pedido_id)
        if pedido is None:
            raise HTTPException(status_code=404, detail="Pedido no encontrado")

        estado_anterior = pedido.estado_codigo
        pedido = _aplicar_transicion(
            uow=uow,
            pedido=pedido,
            estado_hacia=estado_hacia,
            usuario_id=current_user.id,
            motivo=motivo,
        )
        pedido_read = PedidoRead.model_validate(pedido)

    websocket_manager.broadcast(
        {
            "event": "ORDER_STATE_CHANGED",
            "pedido_id": pedido_read.id if pedido_read else pedido_id,
            "owner_id": pedido_read.usuario_id if pedido_read else None,
            "estado_anterior": estado_anterior,
            "estado_nuevo": estado_hacia,
            "usuario_id": current_user.id,
            "motivo": motivo,
        }
    )
    return pedido_read


def cancelar_pedido(
    pedido_id: int,
    current_user: Usuario,
    motivo: str,
) -> PedidoRead:
    pedido_read: Optional[PedidoRead] = None
    estado_anterior: Optional[str] = None

    with UnitOfWork() as uow:
        pedido = uow.session.get(Pedido, pedido_id)
        if pedido is None:
            raise HTTPException(status_code=404, detail="Pedido no encontrado")

        es_dueno = pedido.usuario_id == current_user.id
        es_gestor = _puede_avanzar(current_user.roles)
        if not es_dueno and not es_gestor:
            raise HTTPException(status_code=403, detail="Sin acceso a este pedido")

        if es_dueno and not es_gestor and pedido.estado_codigo not in ESTADOS_CANCELABLES_POR_CLIENTE:
            raise HTTPException(
                status_code=409,
                detail="El pedido ya no puede cancelarse por el cliente.",
            )

        estado_anterior = pedido.estado_codigo
        pedido = _aplicar_transicion(
            uow=uow,
            pedido=pedido,
            estado_hacia="CANCELADO",
            usuario_id=current_user.id,
            motivo=motivo,
        )
        pedido_read = PedidoRead.model_validate(pedido)

    websocket_manager.broadcast(
        {
            "event": "ORDER_STATE_CHANGED",
            "pedido_id": pedido_read.id if pedido_read else pedido_id,
            "owner_id": pedido_read.usuario_id if pedido_read else None,
            "estado_anterior": estado_anterior,
            "estado_nuevo": "CANCELADO",
            "usuario_id": current_user.id,
            "motivo": motivo,
        }
    )
    return pedido_read


def list_detalles(pedido_id: int, usuario_id: int, roles: Iterable[str]) -> list[DetallePedidoRead]:
    with UnitOfWork() as uow:
        pedido = uow.session.get(Pedido, pedido_id)
        if pedido is None:
            raise HTTPException(status_code=404, detail="Pedido no encontrado")
        _assert_puede_ver(pedido, usuario_id, roles)
        return [DetallePedidoRead.model_validate(d) for d in pedido.detalles]


def list_historial(pedido_id: int, usuario_id: int, roles: Iterable[str]) -> list[HistorialRead]:
    with UnitOfWork() as uow:
        pedido = uow.session.get(Pedido, pedido_id)
        if pedido is None:
            raise HTTPException(status_code=404, detail="Pedido no encontrado")
        _assert_puede_ver(pedido, usuario_id, roles)
        return [HistorialRead.model_validate(h) for h in pedido.historial]
