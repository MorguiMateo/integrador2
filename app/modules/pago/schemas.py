from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.core.types import MoneyDecimal


class PagoCreate(BaseModel):
    pedido_id: int = Field(ge=1)
    token: str
    payment_method_id: str
    installments: int = Field(default=1, ge=1)
    issuer_id: Optional[str] = None
    email: Optional[EmailStr] = None


class PagoResponse(BaseModel):
    id: int
    pedido_id: int
    mp_payment_id: Optional[int] = None
    mp_status: str
    mp_status_detail: Optional[str] = None
    transaction_amount: MoneyDecimal
    payment_method_id: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)
