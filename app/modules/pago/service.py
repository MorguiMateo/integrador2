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
from app.modules.pago.schemas import (
    PagoCreate,
    PagoResponse,
    PreferenciaCreate,
    PreferenciaResponse,
)
from app.modules.pedido.model import Pedido
from app.modules.pedido.service import _aplicar_transicion
from app.modules.usuario.model import Usuario


ROLES_GESTION_PEDIDOS = {"ADMIN", "PEDIDOS"}


def _get_sdk() -> mercadopago.SDK:
    if not settings.MP_ACCESS_TOKEN:
        raise HTTPException(status_code=503, detail="MercadoPago no está configurado.")
    return mercadopago.SDK(settings.MP_ACCESS_TOKEN)


def _evento_pago_confirmado(pedido_id: int, owner_id: Optional[int]) -> dict:
    # Mismo evento que usa el módulo pedido para que el Store (cliente dueño) y el
    # panel admin lo reciban y refresquen: ambos escuchan ORDER_STATE_CHANGED.
    return {
        "event": "ORDER_STATE_CHANGED",
        "pedido_id": pedido_id,
        "owner_id": owner_id,
        "estado_anterior": "PENDIENTE",
        "estado_nuevo": "CONFIRMADO",
    }


def _items_preferencia(pedido: Pedido) -> list[dict]:
    # Si hay descuento, una sola línea con el total garantiza que el monto cobrado
    # coincida con Pedido.total. Si no, se itemiza producto por producto + envío.
    if pedido.descuento and pedido.descuento > 0:
        return [
            {
                "title": f"Pedido #{pedido.id}",
                "quantity": 1,
                "currency_id": "ARS",
                "unit_price": float(pedido.total),
            }
        ]

    items = [
        {
            "title": det.nombre_snapshot,
            "quantity": det.cantidad,
            "currency_id": "ARS",
            "unit_price": float(det.precio_snapshot),
        }
        for det in pedido.detalles
    ]
    if pedido.costo_envio and pedido.costo_envio > 0:
        items.append(
            {
                "title": "Envío",
                "quantity": 1,
                "currency_id": "ARS",
                "unit_price": float(pedido.costo_envio),
            }
        )
    return items


def crear_preferencia(data: PreferenciaCreate, current_user: Usuario) -> PreferenciaResponse:
    with UnitOfWork() as uow:
        pedido = uow.session.get(Pedido, data.pedido_id)
        if pedido is None or pedido.deleted_at is not None:
            raise HTTPException(status_code=404, detail="Pedido no encontrado")
        if pedido.usuario_id != current_user.id:
            raise HTTPException(status_code=403, detail="Sin acceso a este pedido")
        if pedido.estado_codigo != "PENDIENTE":
            raise HTTPException(status_code=409, detail="El pedido no está pendiente de pago.")

        # Reutiliza el pago si ya se generó una preferencia para este pedido.
        repo = PagoRepository(uow.session)
        pago = repo.get_by_pedido(pedido.id)
        if pago is None:
            pago = Pago(
                pedido_id=pedido.id,
                mp_status="pending",
                idempotency_key=str(uuid4()),
                transaction_amount=pedido.total,
                external_reference=str(uuid4()),
            )
            uow.session.add(pago)
            uow.session.flush()

        preference_data = {
            "items": _items_preferencia(pedido),
            "external_reference": pago.external_reference,
            "payer": {"email": current_user.email},
            "back_urls": {
                "success": f"{settings.FRONTEND_URL}/orders/{pedido.id}?pago=success",
                "failure": f"{settings.FRONTEND_URL}/orders/{pedido.id}?pago=failure",
                "pending": f"{settings.FRONTEND_URL}/orders/{pedido.id}?pago=pending",
            },
            "metadata": {"pedido_id": pedido.id},
        }
        # MercadoPago rechaza auto_return si la back_url de éxito no es pública
        # (con localhost devuelve "invalid_auto_return"). En dev queda sin auto_return
        # (el usuario vuelve con el botón "Volver al sitio"); en prod redirige solo.
        if not any(host in settings.FRONTEND_URL for host in ("localhost", "127.0.0.1")):
            preference_data["auto_return"] = "approved"
        if settings.MP_NOTIFICATION_URL:
            preference_data["notification_url"] = settings.MP_NOTIFICATION_URL

        resultado = _get_sdk().preference().create(preference_data)
        mp = resultado.get("response", {})
        init_point = mp.get("init_point") or mp.get("sandbox_init_point")
        preference_id = mp.get("id")
        if not init_point or not preference_id:
            raise HTTPException(status_code=502, detail="MercadoPago no devolvió la preferencia.")

        return PreferenciaResponse(
            pago_id=pago.id,
            pedido_id=pedido.id,
            preference_id=str(preference_id),
            init_point=init_point,
        )


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
    owner_id: Optional[int] = None

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
            owner_id = pedido.usuario_id

    if pedido_confirmado is not None:
        websocket_manager.broadcast(_evento_pago_confirmado(pedido_confirmado, owner_id))


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
