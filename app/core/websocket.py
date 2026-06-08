from __future__ import annotations

import asyncio
from typing import Any, Iterable, Optional

from fastapi import WebSocket, WebSocketException, status
from jose import JWTError, jwt
from sqlmodel import Session

from app.core.config import settings
from app.core.database import engine
from app.core.deps import ACCESS_COOKIE_NAME
from app.modules.usuario.model import Usuario
from app.modules.usuario.repository import UsuarioRepository


class ConnectionManager:
    def __init__(self) -> None:
        self.active_connections: set[WebSocket] = set()
        self._loop: asyncio.AbstractEventLoop | None = None

    async def connect(self, websocket: WebSocket) -> None:
        await websocket.accept()
        self._loop = asyncio.get_running_loop()
        self.active_connections.add(websocket)

    def disconnect(self, websocket: WebSocket) -> None:
        self.active_connections.discard(websocket)

    async def _broadcast_async(self, message: Any) -> None:
        stale_connections: list[WebSocket] = []

        for websocket in list(self.active_connections):
            try:
                await websocket.send_json(message)
            except Exception:
                stale_connections.append(websocket)

        for websocket in stale_connections:
            self.active_connections.discard(websocket)

    def broadcast(self, message: Any) -> None:
        if self._loop is None or self._loop.is_closed():
            return

        asyncio.run_coroutine_threadsafe(self._broadcast_async(message), self._loop)


manager = ConnectionManager()


def _decode_access_token(token: str) -> str:
    payload = jwt.decode(
        token,
        settings.SECRET_KEY,
        algorithms=[settings.ALGORITHM],
    )
    if payload.get("type") != "access":
        raise JWTError("El token no es de tipo access.")
    email = payload.get("sub")
    if not email:
        raise JWTError("El token no contiene sub.")
    return email


async def get_current_websocket_user(
    websocket: WebSocket,
    allowed_roles: Optional[Iterable[str]] = None,
) -> Usuario:
    token = websocket.cookies.get(ACCESS_COOKIE_NAME) or websocket.query_params.get("token")

    authorization = websocket.headers.get("authorization")
    if not token and authorization and authorization.lower().startswith("bearer "):
        token = authorization[7:].strip()

    if not token:
        raise WebSocketException(
            code=status.WS_1008_POLICY_VIOLATION,
            reason="No se pudieron validar las credenciales.",
        )

    try:
        email = _decode_access_token(token)
    except JWTError:
        raise WebSocketException(
            code=status.WS_1008_POLICY_VIOLATION,
            reason="Token inválido o expirado.",
        )

    with Session(engine) as session:
        usuario = UsuarioRepository(session).get_by_email(email)
        if usuario is None or usuario.deleted_at is not None:
            raise WebSocketException(
                code=status.WS_1008_POLICY_VIOLATION,
                reason="Usuario inválido.",
            )

    if allowed_roles is not None and not set(allowed_roles).intersection(usuario.roles):
        raise WebSocketException(
            code=status.WS_1008_POLICY_VIOLATION,
            reason="Permisos insuficientes para esta operación.",
        )

    return usuario
