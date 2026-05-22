from __future__ import annotations
from fastapi import APIRouter, HTTPException
from app.core.uow import UnitOfWork
from app.modules.pedido.service import avanzar_estado
from app.modules.pago.model import Pago
from sqlmodel import select

router = APIRouter(prefix="/pagos", tags=["pagos"])

@router.post("/webhook")
def webhook_mercadopago(payload: dict):
    topic = payload.get("topic")
    if topic != "payment":
        return {"status": "ignored"}
    
    mp_payment_id = payload.get("resource")

    with UnitOfWork() as uow:
        pago = uow.session.exec(
            select(Pago).where(Pago.mp_payment_id == mp_payment_id)
        ).first()

        if pago is None:
            raise HTTPException(status_code=404, detail="Pago no encontrado")
        
        pago.mp_status = "approved"
        uow.session.add(pago)

        avanzar_estado(uow, pago.pedido_id, "CONFIRMADO", None, None)

    return {"status": "ok"}