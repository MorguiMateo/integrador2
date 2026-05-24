from datetime import datetime
from decimal import Decimal
from typing import Optional
from sqlalchemy import Column, DateTime, Integer, Numeric, Text, func
from sqlalchemy.dialects.postgresql import ARRAY
from sqlmodel import Field, Relationship, SQLModel


class Pedido(SQLModel, table=True):
    __tablename__ = "pedidos"

    id: Optional[int] = Field(default=None, primary_key=True)
    usuario_id: int = Field(foreign_key="usuarios.id", nullable=False)
    direccion_id: Optional[int] = Field(foreign_key="direcciones_entrega.id")
    estado_codigo: str = Field(foreign_key="estados_pedido.codigo", nullable=False, default="PENDIENTE", max_length=20)
    forma_pago_codigo: str = Field(foreign_key="formas_pago.codigo", nullable=False)
    subtotal: Decimal = Field(sa_column=Column(Numeric(10, 2), nullable=False))
    descuento: Decimal = Field(default=Decimal("0.00"), sa_column=Column(Numeric(10, 2), nullable=False))
    costo_envio: Decimal = Field(default=Decimal("50.00"), sa_column=Column(Numeric(10, 2), nullable=False))
    total: Decimal = Field(sa_column=Column(Numeric(10, 2), nullable=False))
    notas: Optional[str] = Field(default=None, sa_column=Column(Text, nullable=True))
    created_at: datetime = Field(sa_column=Column(DateTime(timezone=True), nullable=False, server_default=func.now()))
    updated_at: datetime = Field(sa_column=Column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()))
    deleted_at: Optional[datetime] = Field(sa_column=Column(DateTime(timezone=True), nullable=True), default=None)
    detalles: list["DetallePedido"] = Relationship(sa_relationship_kwargs={"lazy": "selectin"})
    historial: list["HistorialEstadoPedido"] = Relationship(sa_relationship_kwargs={"lazy": "selectin"})


class DetallePedido(SQLModel, table=True):
    __tablename__ = "detalles_pedido"

    pedido_id: int = Field(primary_key=True, foreign_key="pedidos.id")
    producto_id: int = Field(primary_key=True, foreign_key="productos.id")
    cantidad: int = Field(nullable=False)
    nombre_snapshot: str = Field(max_length=150, nullable=False)
    precio_snapshot: Decimal = Field(sa_column=Column(Numeric(10, 2), nullable=False))
    subtotal_snap: Decimal = Field(sa_column=Column(Numeric(10, 2), nullable=False))
    personalizacion: list[int] = Field(sa_column=Column(ARRAY(Integer)))
    created_at: datetime = Field(sa_column=Column(DateTime(timezone=True), nullable=False, server_default=func.now()))


class HistorialEstadoPedido(SQLModel, table=True):
    __tablename__ = "historial_estados_pedido"

    id: Optional[int] = Field(default=None, primary_key=True)
    pedido_id: int = Field(foreign_key="pedidos.id", nullable=False)
    estado_desde: Optional[str] = Field(foreign_key="estados_pedido.codigo")
    estado_hacia: str = Field(foreign_key="estados_pedido.codigo", nullable=False)
    usuario_id: Optional[int] = Field(foreign_key="usuarios.id")
    motivo: Optional[str] = Field(default=None)
    created_at: datetime = Field(sa_column=Column(DateTime(timezone=True), nullable=False, server_default=func.now()))
