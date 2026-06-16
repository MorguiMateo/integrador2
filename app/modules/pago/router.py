from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, Path, Request, status

from app.core.deps import get_current_active_user
from app.modules.pago import service
from app.modules.pago.schemas import PagoCreate, PagoResponse
from app.modules.usuario.model import Usuario


router = APIRouter(prefix="/pagos", tags=["pagos"])


@router.post("/crear", response_model=PagoResponse, status_code=status.HTTP_201_CREATED)
def crear_pago(
    payload: PagoCreate,
    current_user: Usuario = Depends(get_current_active_user),
) -> PagoResponse:
    return service.crear_pago(payload, current_user)


@router.post("/webhook")
async def webhook(request: Request) -> dict:
    body: dict = {}
    try:
        body = await request.json()
    except Exception:
        body = {}

    params = request.query_params
    tipo = body.get("type") or body.get("topic") or params.get("type") or params.get("topic")

    data_id = None
    if isinstance(body.get("data"), dict):
        data_id = body["data"].get("id")
    data_id = data_id or params.get("data.id") or params.get("id")

    service.procesar_webhook(tipo, str(data_id) if data_id else None)
    return {"status": "ok"}


@router.get("/{pedido_id}", response_model=PagoResponse)
def obtener_pago(
    pedido_id: Annotated[int, Path(ge=1)],
    current_user: Usuario = Depends(get_current_active_user),
) -> PagoResponse:
    return service.get_pago_por_pedido(pedido_id, current_user, current_user.roles)
