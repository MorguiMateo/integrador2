from __future__ import annotations
from datetime import datetime
from decimal import Decimal
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class ItemPedidoRequest(BaseModel):
    producto_id: int
    cantidad: int = Field(ge=1)
    personalizacion: Optional[list[int]] = None


class PedidoCreate(BaseModel):
    direccion_id: Optional[int] = None
    forma_pago_codigo: str
    notas: Optional[str] = None
    items: list[ItemPedidoRequest] = Field(min_length=1)


class AvanzarEstadoRequest(BaseModel):
    estado_hacia: str
    motivo: Optional[str] = None


class DetallePedidoRead(BaseModel):
    pedido_id: int
    producto_id: int
    cantidad: int
    nombre_snapshot: str
    precio_snapshot: Decimal
    subtotal_snap: Decimal
    personalizacion: list[int]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class HistorialRead(BaseModel):
    id: int
    estado_desde: Optional[str]
    estado_hacia: str
    usuario_id: Optional[int]
    motivo: Optional[str]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class PedidoRead(BaseModel):
    id: int
    usuario_id: int
    direccion_id: Optional[int]
    estado_codigo: str
    forma_pago_codigo: str
    subtotal: Decimal
    descuento: Decimal
    costo_envio: Decimal
    total: Decimal
    notas: Optional[str]
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime]
    detalles: list[DetallePedidoRead] = []
    historial: list[HistorialRead] = []

    model_config = ConfigDict(from_attributes=True)
