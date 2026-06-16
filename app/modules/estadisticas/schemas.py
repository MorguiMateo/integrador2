from __future__ import annotations

from datetime import date

from pydantic import BaseModel

from app.core.types import MoneyDecimal


class VentasPeriodoItem(BaseModel):
    periodo: date
    total_ventas: MoneyDecimal
    cantidad_pedidos: int


class ProductoTopItem(BaseModel):
    nombre: str
    cantidad_vendida: int
    ingresos: MoneyDecimal


class PedidosEstadoItem(BaseModel):
    estado_codigo: str
    cantidad: int


class IngresosResponse(BaseModel):
    forma_pago_codigo: str
    total: MoneyDecimal
    cantidad: int


class ResumenResponse(BaseModel):
    ventas_hoy: MoneyDecimal
    ticket_promedio: MoneyDecimal
    pedidos_activos: int
    ventas_mes: MoneyDecimal
