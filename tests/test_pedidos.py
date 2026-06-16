def _crear_pedido(client, cookies, producto_id, cantidad):
    return client.post(
        "/api/v1/pedidos",
        cookies=cookies,
        json={
            "items": [{"producto_id": producto_id, "cantidad": cantidad, "personalizacion": None}],
            "forma_pago_codigo": "EFECTIVO",
            "direccion_id": None,
            "notas": None,
        },
    )


def test_crear_pedido_ok(client, client_headers, producto_factory):
    pid = producto_factory(stock=10)
    r = _crear_pedido(client, client_headers, pid, 2)
    assert r.status_code == 201
    assert r.json()["estado_codigo"] == "PENDIENTE"


def test_stock_insuficiente(client, client_headers, producto_factory):
    pid = producto_factory(stock=1)
    r = _crear_pedido(client, client_headers, pid, 5)
    assert r.status_code == 400


def test_avanzar_estado_valido(client, admin_headers, cliente_id, producto_factory, pedido_factory):
    pid = producto_factory()
    pedido_id = pedido_factory(cliente_id, pid, estado="PENDIENTE")
    r = client.post(
        f"/api/v1/pedidos/{pedido_id}/avanzar",
        cookies=admin_headers,
        json={"estado_hacia": "CONFIRMADO", "motivo": None},
    )
    assert r.status_code == 200
    assert r.json()["estado_codigo"] == "CONFIRMADO"


def test_avanzar_estado_terminal_invalido(client, admin_headers, cliente_id, producto_factory, pedido_factory):
    pid = producto_factory()
    pedido_id = pedido_factory(cliente_id, pid, estado="ENTREGADO")
    r = client.post(
        f"/api/v1/pedidos/{pedido_id}/avanzar",
        cookies=admin_headers,
        json={"estado_hacia": "EN_PREP", "motivo": None},
    )
    assert r.status_code == 422


def test_historial_append_only(client, admin_headers, cliente_id, producto_factory, pedido_factory):
    pid = producto_factory()
    pedido_id = pedido_factory(cliente_id, pid, estado="PENDIENTE")
    client.post(
        f"/api/v1/pedidos/{pedido_id}/avanzar",
        cookies=admin_headers,
        json={"estado_hacia": "CONFIRMADO", "motivo": None},
    )
    r = client.get(f"/api/v1/pedidos/{pedido_id}/historial", cookies=admin_headers)
    assert r.status_code == 200
    assert len(r.json()) >= 2


def test_cancelar_pedido_propio(client, client_headers, cliente_id, producto_factory, pedido_factory):
    pid = producto_factory()
    pedido_id = pedido_factory(cliente_id, pid, estado="PENDIENTE")
    r = client.post(
        f"/api/v1/pedidos/{pedido_id}/cancelar",
        cookies=client_headers,
        json={"motivo": "Ya no lo quiero"},
    )
    assert r.status_code == 200
    assert r.json()["estado_codigo"] == "CANCELADO"
