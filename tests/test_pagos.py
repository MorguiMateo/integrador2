import app.modules.pago.service as pago_service


class _FakePayment:
    def __init__(self, status: str) -> None:
        self._status = status

    def create(self, data, request_options=None):
        return {
            "response": {
                "id": 111222,
                "status": self._status,
                "status_detail": "accredited" if self._status == "approved" else "cc_rejected",
                "payment_method_id": "visa",
                "external_reference": data.get("external_reference"),
            }
        }

    def get(self, payment_id):
        return {
            "response": {
                "id": 111222,
                "status": "approved",
                "status_detail": "accredited",
            }
        }


class _FakeSDK:
    def __init__(self, status: str) -> None:
        self._payment = _FakePayment(status)

    def payment(self):
        return self._payment


def _crear_pago(client, cookies, pedido_id):
    return client.post(
        "/api/v1/pagos/crear",
        cookies=cookies,
        json={"pedido_id": pedido_id, "token": "tok-test", "payment_method_id": "visa", "installments": 1},
    )


def test_pago_approved_confirma_pedido(client, client_headers, cliente_id, producto_factory, pedido_factory, monkeypatch):
    monkeypatch.setattr(pago_service, "_get_sdk", lambda: _FakeSDK("approved"))
    pid = producto_factory()
    pedido_id = pedido_factory(cliente_id, pid, estado="PENDIENTE")

    r = _crear_pago(client, client_headers, pedido_id)
    assert r.status_code == 201
    assert r.json()["mp_status"] == "approved"

    detalle = client.get(f"/api/v1/pedidos/{pedido_id}", cookies=client_headers)
    assert detalle.json()["estado_codigo"] == "CONFIRMADO"


def test_pago_rejected_deja_pedido_pendiente(client, client_headers, cliente_id, producto_factory, pedido_factory, monkeypatch):
    monkeypatch.setattr(pago_service, "_get_sdk", lambda: _FakeSDK("rejected"))
    pid = producto_factory()
    pedido_id = pedido_factory(cliente_id, pid, estado="PENDIENTE")

    r = _crear_pago(client, client_headers, pedido_id)
    assert r.status_code == 201
    assert r.json()["mp_status"] == "rejected"

    detalle = client.get(f"/api/v1/pedidos/{pedido_id}", cookies=client_headers)
    assert detalle.json()["estado_codigo"] == "PENDIENTE"


def test_consultar_pago_por_pedido(client, client_headers, cliente_id, producto_factory, pedido_factory, monkeypatch):
    monkeypatch.setattr(pago_service, "_get_sdk", lambda: _FakeSDK("approved"))
    pid = producto_factory()
    pedido_id = pedido_factory(cliente_id, pid, estado="PENDIENTE")
    _crear_pago(client, client_headers, pedido_id)

    r = client.get(f"/api/v1/pagos/{pedido_id}", cookies=client_headers)
    assert r.status_code == 200
    assert r.json()["pedido_id"] == pedido_id
