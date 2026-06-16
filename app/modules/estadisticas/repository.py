from __future__ import annotations

from datetime import date

from sqlalchemy import func
from sqlmodel import Session, select

from app.modules.pago.model import Pago
from app.modules.pedido.model import DetallePedido, Pedido


ESTADO_CANCELADO = "CANCELADO"
ESTADOS_ACTIVOS = ["PENDIENTE", "CONFIRMADO", "EN_PREP"]


class EstadisticasRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def ventas_periodo(self, desde: date, hasta: date, agrupacion: str):
        periodo = func.date(func.date_trunc(agrupacion, Pedido.created_at)).label("periodo")
        stmt = (
            select(
                periodo,
                func.coalesce(func.sum(Pedido.total), 0).label("total_ventas"),
                func.count(Pedido.id).label("cantidad_pedidos"),
            )
            .where(Pedido.deleted_at.is_(None))
            .where(Pedido.estado_codigo != ESTADO_CANCELADO)
            .where(func.date(Pedido.created_at).between(desde, hasta))
            .group_by(periodo)
            .order_by(periodo)
        )
        return self.session.exec(stmt).all()

    def productos_top(self, limit: int):
        stmt = (
            select(
                DetallePedido.nombre_snapshot.label("nombre"),
                func.sum(DetallePedido.cantidad).label("cantidad_vendida"),
                func.sum(DetallePedido.subtotal_snap).label("ingresos"),
            )
            .join(Pedido, Pedido.id == DetallePedido.pedido_id)
            .where(Pedido.deleted_at.is_(None))
            .where(Pedido.estado_codigo != ESTADO_CANCELADO)
            .group_by(DetallePedido.nombre_snapshot)
            .order_by(func.sum(DetallePedido.subtotal_snap).desc())
            .limit(limit)
        )
        return self.session.exec(stmt).all()

    def pedidos_por_estado(self):
        stmt = (
            select(Pedido.estado_codigo, func.count(Pedido.id).label("cantidad"))
            .where(Pedido.deleted_at.is_(None))
            .group_by(Pedido.estado_codigo)
        )
        return self.session.exec(stmt).all()

    def ingresos_por_forma_pago(self, desde: date, hasta: date):
        stmt = (
            select(
                Pedido.forma_pago_codigo,
                func.coalesce(func.sum(Pedido.total), 0).label("total"),
                func.count(Pedido.id).label("cantidad"),
            )
            .join(Pago, Pago.pedido_id == Pedido.id)
            .where(Pedido.deleted_at.is_(None))
            .where(Pedido.estado_codigo != ESTADO_CANCELADO)
            .where(Pago.mp_status == "approved")
            .where(func.date(Pedido.created_at).between(desde, hasta))
            .group_by(Pedido.forma_pago_codigo)
        )
        return self.session.exec(stmt).all()

    def total_ventas_entre(self, desde: date, hasta: date):
        stmt = (
            select(func.coalesce(func.sum(Pedido.total), 0))
            .where(Pedido.deleted_at.is_(None))
            .where(Pedido.estado_codigo != ESTADO_CANCELADO)
            .where(func.date(Pedido.created_at).between(desde, hasta))
        )
        return self.session.exec(stmt).one()

    def ticket_promedio(self):
        stmt = (
            select(func.coalesce(func.avg(Pedido.total), 0))
            .where(Pedido.deleted_at.is_(None))
            .where(Pedido.estado_codigo != ESTADO_CANCELADO)
        )
        return self.session.exec(stmt).one()

    def pedidos_activos(self):
        stmt = (
            select(func.count(Pedido.id))
            .where(Pedido.deleted_at.is_(None))
            .where(Pedido.estado_codigo.in_(ESTADOS_ACTIVOS))
        )
        return self.session.exec(stmt).one()
