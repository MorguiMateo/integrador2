from decimal import Decimal
from app.core.uow import UnitOfWork
from app.modules.pedido.model import Pedido, DetallePedido, HistorialEstadoPedido
from app.modules.pedido.schema import PedidoCreate
from app.modules.producto.model import Producto


FSM_TRANSITIONS = {
    "PENDIENTE":  ["CONFIRMADO", "CANCELADO"],
    "CONFIRMADO": ["EN_PREP",    "CANCELADO"],
    "EN_PREP":    ["EN_CAMINO"],
    "EN_CAMINO":  ["ENTREGADO"],
    "ENTREGADO":  [],
    "CANCELADO":  [],
}


def create_pedido(uow, data: PedidoCreate, usuario_id: int) -> Pedido:
    detalles = []
    for item in data.items:

        producto = uow.session.get(Producto, item.producto_id)
        if producto is None:
            raise ValueError(f"Producto{item.producto_id} no se ha encontraado")
        

        det = DetallePedido(
        producto_id=item.producto_id,
        cantidad=item.cantidad,
        nombre_snapshot=producto.nombre,
        precio_snapshot=producto.precio_base,
        subtotal_snap=producto.precio_base * item.cantidad,
        personalizacion=item.personalizacion or [],
        )
        detalles.append(det)


    subtotal = sum(d.subtotal_snap for d in detalles)
    descuento = Decimal("0.00")
    costo_envio = Decimal("50.00")
    total = subtotal - descuento + costo_envio


    pedido = Pedido(
        usuario_id=usuario_id,
        direccion_id=data.direccion_id,
        forma_pago_codigo=data.forma_pago_codigo,
        notas=data.notas,
        subtotal=subtotal,
        descuento=descuento,
        costo_envio=costo_envio,
        total=total,
    )
    uow.session.add(pedido)
    uow.session.flush()


    for det in detalles:
        det.pedido_id = pedido.id
        uow.session.add(det)


    historial = HistorialEstadoPedido(
        pedido_id=pedido.id,
        estado_desde=None,
        estado_hacia="PENDIENTE",
        usuario_id=usuario_id,
    )
    uow.session.add(historial)
    uow.session.flush()

    return pedido
    


def avanzar_estado(uow: UnitOfWork, pedido_id: int, estado_hacia: str, usuario_id: int, motivo: str | None) -> Pedido:

    pedido = uow.session.get(Pedido, pedido_id)
    if pedido is None:
        raise ValueError("Pedido no ha siddo encontado")
        
    if estado_hacia not in FSM_TRANSITIONS[pedido.estado_codigo]:
        raise ValueError(f"Transicion invalida: {pedido.estado_codigo} -> {estado_hacia}")
        
    if estado_hacia == "CANCELADO" and motivo is None:
        raise ValueError("Motivo obligatorio para cancelar el pedidoo")
        
    estado_anterior = pedido.estado_codigo
    pedido.estado_codigo = estado_hacia
    uow.session.add(pedido)

    historial = HistorialEstadoPedido(
        pedido_id=pedido.id,
        estado_desde=estado_anterior,
        estado_hacia=estado_hacia,
        usuario_id=usuario_id,
        motivo=motivo,
    )
    uow.session.add(historial)
    uow.session.flush()

    return pedido

        
                       





