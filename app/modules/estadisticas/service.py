from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import Optional

from app.core.uow import UnitOfWork
from app.modules.estadisticas.repository import EstadisticasRepository
from app.modules.estadisticas.schemas import (
    IngresosResponse,
    PedidosEstadoItem,
    ProductoTopItem,
    ResumenResponse,
    VentasPeriodoItem,
)


def _money(value) -> Decimal:
    return Decimal(str(value or 0)).quantize(Decimal("0.01"))


def _rango(desde: Optional[date], hasta: Optional[date]) -> tuple[date, date]:
    hoy = date.today()
    return desde or hoy.replace(day=1), hasta or hoy


def ventas_periodo(desde: Optional[date], hasta: Optional[date], agrupacion: str) -> list[VentasPeriodoItem]:
    inicio, fin = _rango(desde, hasta)
    with UnitOfWork() as uow:
        filas = EstadisticasRepository(uow.session).ventas_periodo(inicio, fin, agrupacion)
        return [
            VentasPeriodoItem(
                periodo=fila.periodo,
                total_ventas=_money(fila.total_ventas),
                cantidad_pedidos=fila.cantidad_pedidos,
            )
            for fila in filas
        ]


def productos_top(limit: int) -> list[ProductoTopItem]:
    with UnitOfWork() as uow:
        filas = EstadisticasRepository(uow.session).productos_top(limit)
        return [
            ProductoTopItem(
                nombre=fila.nombre,
                cantidad_vendida=fila.cantidad_vendida,
                ingresos=_money(fila.ingresos),
            )
            for fila in filas
        ]


def pedidos_por_estado() -> list[PedidosEstadoItem]:
    with UnitOfWork() as uow:
        filas = EstadisticasRepository(uow.session).pedidos_por_estado()
        return [
            PedidosEstadoItem(estado_codigo=fila.estado_codigo, cantidad=fila.cantidad)
            for fila in filas
        ]


def ingresos_por_forma_pago(desde: Optional[date], hasta: Optional[date]) -> list[IngresosResponse]:
    inicio, fin = _rango(desde, hasta)
    with UnitOfWork() as uow:
        filas = EstadisticasRepository(uow.session).ingresos_por_forma_pago(inicio, fin)
        return [
            IngresosResponse(
                forma_pago_codigo=fila.forma_pago_codigo,
                total=_money(fila.total),
                cantidad=fila.cantidad,
            )
            for fila in filas
        ]


def resumen() -> ResumenResponse:
    hoy = date.today()
    inicio_mes = hoy.replace(day=1)
    with UnitOfWork() as uow:
        repo = EstadisticasRepository(uow.session)
        return ResumenResponse(
            ventas_hoy=_money(repo.total_ventas_entre(hoy, hoy)),
            ticket_promedio=_money(repo.ticket_promedio()),
            pedidos_activos=repo.pedidos_activos(),
            ventas_mes=_money(repo.total_ventas_entre(inicio_mes, hoy)),
        )
