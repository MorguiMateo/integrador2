import pytest
from starlette.websockets import WebSocketDisconnect


def test_ws_sin_token_rechazado(client):
    with pytest.raises(WebSocketDisconnect):
        with client.websocket_connect("/api/v1/pedidos/ws") as ws:
            ws.receive_text()


def test_ws_con_token_admin(client, admin_headers):
    token = admin_headers["access_token"]
    with client.websocket_connect(f"/api/v1/pedidos/ws?token={token}") as ws:
        assert ws is not None
