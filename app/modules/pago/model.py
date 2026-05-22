from sqlmodel import SQLModel, Field
from datetime import datetime
from decimal import Decimal
from sqlalchemy import Column, DateTime, Numeric, func


class Pago(SQLModel, table=True):
    
    __tablename__="pagos"
    id: int | None = Field(default=None, primary_key=True)
    pedido_id: int = Field(foreign_key="pedidos.id", nullable=False)
    mp_payment_id: int | None = Field(unique=True, default=None)
    mp_status: str = Field(max_length=30, nullable=False)
    mp_status_detail: str | None = Field(max_length=100, default=None)
    idempotency_key: str = Field(max_length=100, unique=True, nullable=False)
    transaction_amount: Decimal = Field(sa_column=Column(Numeric(10, 2), nullable=False))
    payment_method_id: str | None = Field(max_length=50)
    created_at: datetime = Field(sa_column=Column(DateTime(timezone=True), nullable=False, server_default=func.now()))
    external_reference: str = Field(max_length=100, unique=True, nullable=False)






