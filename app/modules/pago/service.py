from __future__ import annotations

from typing import Iterable, Optional
from uuid import uuid4

import mercadopago
from fastapi import HTTPException

from app.core.config import settings
from app.core.uow import UnitOfWork
from app.core.websocket import manager as websocket_manager
from app.modules.pago.model import Pago
from app.modules.pago.repository import PagoRepository
from app.modules.pago.schemas import PagoCreate, PagoResponse
from app.modules.pedido.model import Pedido
from app.modules.pedido.service import _aplicar_transicion
from app.modules.usuario.model import Usuario


ROLES_GESTION_PEDIDOS = {"ADMIN", "PEDIDOS"}


def _get_sdk() -> mercadopago.SDK:
    if not settings.MP_ACCESS_TOKEN:
        raise HTTPException(status_code=503, detail="MercadoPago no está configurado.")
    return mercadopago.SDK(settings.MP_ACCESS_TOKEN)


def _evento_pago_confirmado(pedido_id: int, usuario_id: Optional[int]) -> dict:
    return {
        "event": "pago_confirmado",
        "pedido_id": pedido_id,
        "estado_anterior": "PENDIENTE",
        "estado_nuevo": "CONFIRMADO",
        "usuario_id": usuario_id,
    }


def crear_pago(data: PagoCreate, current_user: Usuario) -> PagoResponse:
    confirmado = False

    with UnitOfWork() as uow:
        pedido = uow.session.get(Pedido, data.pedido_id)
        if pedido is None or pedido.deleted_at is not None:
            raise HTTPException(status_code=404, detail="Pedido no encontrado")
        if pedido.usuario_id != current_user.id:
            raise HTTPException(status_code=403, detail="Sin acceso a este pedido")
        if pedido.estado_codigo != "PENDIENTE":
            raise HTTPException(status_code=409, detail="El pedido no está pendiente de pago.")

        idempotency_key = str(uuid4())
        external_reference = str(uuid4())

        payment_data = {
            "transaction_amount": float(pedido.total),
            "token": data.token,
            "installments": data.installments,
            "payment_method_id": data.payment_method_id,
            "external_reference": external_reference,
            "payer": {"email": data.email or current_user.email},
        }
        if data.issuer_id:
            payment_data["issuer_id"] = data.issuer_id

        resultado = _get_sdk().payment().create(payment_data, {"x-idempotency-key": idempotency_key})
        mp = resultado.get("response", {})
        estado_mp = mp.get("status")
        if not estado_mp:
            raise HTTPException(status_code=502, detail="MercadoPago no devolvió un estado de pago.")

        pago = Pago(
            pedido_id=pedido.id,
            mp_payment_id=mp.get("id"),
            mp_status=estado_mp,
            mp_status_detail=mp.get("status_detail"),
            idempotency_key=idempotency_key,
            transaction_amount=pedido.total,
            payment_method_id=mp.get("payment_method_id"),
            external_reference=external_reference,
        )
        uow.session.add(pago)

        confirmado = estado_mp == "approved"
        if confirmado:
            _aplicar_transicion(uow, pedido, "CONFIRMADO", current_user.id, None)

        uow.session.flush()
        pago_read = PagoResponse.model_validate(pago)

    if confirmado:
        websocket_manager.broadcast(_evento_pago_confirmado(pago_read.pedido_id, current_user.id))
    return pago_read


def procesar_webhook(tipo: Optional[str], data_id: Optional[str]) -> None:
    if tipo != "payment" or not data_id:
        return

    pedido_confirmado: Optional[int] = None

    with UnitOfWork() as uow:
        resultado = _get_sdk().payment().get(data_id)
        mp = resultado.get("response", {})
        estado_mp = mp.get("status")

        repo = PagoRepository(uow.session)
        pago = None
        if mp.get("id"):
            pago = repo.get_by_mp_payment_id(mp["id"])
        if pago is None and mp.get("external_reference"):
            pago = repo.get_by_external_reference(mp["external_reference"])
        if pago is None:
            return

        pago.mp_status = estado_mp or pago.mp_status
        pago.mp_status_detail = mp.get("status_detail")
        uow.session.add(pago)

        pedido = uow.session.get(Pedido, pago.pedido_id)
        if estado_mp == "approved" and pedido is not None and pedido.estado_codigo == "PENDIENTE":
            _aplicar_transicion(uow, pedido, "CONFIRMADO", None, None)
            pedido_confirmado = pedido.id

    if pedido_confirmado is not None:
        websocket_manager.broadcast(_evento_pago_confirmado(pedido_confirmado, None))


def get_pago_por_pedido(pedido_id: int, current_user: Usuario, roles: Iterable[str]) -> PagoResponse:
    with UnitOfWork() as uow:
        pedido = uow.session.get(Pedido, pedido_id)
        if pedido is None:
            raise HTTPException(status_code=404, detail="Pedido no encontrado")

        es_gestor = any(r in ROLES_GESTION_PEDIDOS for r in roles)
        if not es_gestor and pedido.usuario_id != current_user.id:
            raise HTTPException(status_code=403, detail="Sin acceso a este pedido")

        pago = PagoRepository(uow.session).get_by_pedido(pedido_id)
        if pago is None:
            raise HTTPException(status_code=404, detail="No hay pago registrado para este pedido")
        return PagoResponse.model_validate(pago)
