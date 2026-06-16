from __future__ import annotations

from datetime import date
from typing import Annotated, Literal, Optional

from fastapi import APIRouter, Depends, Query

from app.modules.auth.dependencies import require_admin
from app.modules.estadisticas import service
from app.modules.estadisticas.schemas import (
    IngresosResponse,
    PedidosEstadoItem,
    ProductoTopItem,
    ResumenResponse,
    VentasPeriodoItem,
)


router = APIRouter(
    prefix="/estadisticas",
    tags=["estadisticas"],
    dependencies=[Depends(require_admin)],
)


@router.get("/ventas", response_model=list[VentasPeriodoItem])
def ventas(
    desde: Annotated[Optional[date], Query()] = None,
    hasta: Annotated[Optional[date], Query()] = None,
    agrupacion: Annotated[Literal["day", "week", "month"], Query()] = "day",
) -> list[VentasPeriodoItem]:
    return service.ventas_periodo(desde, hasta, agrupacion)


@router.get("/productos-top", response_model=list[ProductoTopItem])
def productos_top(
    limit: Annotated[int, Query(ge=1, le=50)] = 5,
) -> list[ProductoTopItem]:
    return service.productos_top(limit)


@router.get("/pedidos-por-estado", response_model=list[PedidosEstadoItem])
def pedidos_por_estado() -> list[PedidosEstadoItem]:
    return service.pedidos_por_estado()


@router.get("/ingresos", response_model=list[IngresosResponse])
def ingresos(
    desde: Annotated[Optional[date], Query()] = None,
    hasta: Annotated[Optional[date], Query()] = None,
) -> list[IngresosResponse]:
    return service.ingresos_por_forma_pago(desde, hasta)


@router.get("/resumen", response_model=ResumenResponse)
def resumen() -> ResumenResponse:
    return service.resumen()
