def test_resumen_ok(client, admin_headers):
    r = client.get("/api/v1/estadisticas/resumen", cookies=admin_headers)
    assert r.status_code == 200
    body = r.json()
    assert "ventas_hoy" in body
    assert "ticket_promedio" in body
    assert "pedidos_activos" in body
    assert "ventas_mes" in body


def test_estadisticas_requiere_admin(client, client_headers):
    r = client.get("/api/v1/estadisticas/resumen", cookies=client_headers)
    assert r.status_code == 403


def test_pedidos_por_estado(client, admin_headers, cliente_id, producto_factory, pedido_factory):
    pid = producto_factory()
    pedido_factory(cliente_id, pid, estado="ENTREGADO")
    pedido_factory(cliente_id, pid, estado="CANCELADO")
    r = client.get("/api/v1/estadisticas/pedidos-por-estado", cookies=admin_headers)
    assert r.status_code == 200
    data = {x["estado_codigo"]: x["cantidad"] for x in r.json()}
    assert data.get("ENTREGADO") == 1
    assert data.get("CANCELADO") == 1


def test_cancelado_no_suma_en_ventas(client, admin_headers, cliente_id, producto_factory, pedido_factory):
    pid = producto_factory()
    pedido_factory(cliente_id, pid, estado="ENTREGADO")
    pedido_factory(cliente_id, pid, estado="CANCELADO")
    r = client.get("/api/v1/estadisticas/ventas", cookies=admin_headers)
    assert r.status_code == 200
    total_pedidos = sum(x["cantidad_pedidos"] for x in r.json())
    assert total_pedidos == 1
