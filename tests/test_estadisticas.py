from decimal import Decimal
from uuid import uuid4

from sqlmodel import Session

from app.core.database import engine
from app.modules.pago.model import Pago


def _insertar_pago(pedido_id: int, mp_status: str) -> None:
    with Session(engine) as session:
        session.add(
            Pago(
                pedido_id=pedido_id,
                mp_status=mp_status,
                idempotency_key=str(uuid4()),
                transaction_amount=Decimal("1050.00"),
                external_reference=str(uuid4()),
            )
        )
        session.commit()


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


def test_ventas_por_periodo(client, admin_headers, cliente_id, producto_factory, pedido_factory):
    pid = producto_factory()
    pedido_factory(cliente_id, pid, estado="ENTREGADO")
    r = client.get("/api/v1/estadisticas/ventas?agrupacion=day", cookies=admin_headers)
    assert r.status_code == 200
    data = r.json()
    assert len(data) == 1
    assert data[0]["cantidad_pedidos"] == 1
    assert float(data[0]["total_ventas"]) == 1050.0


def test_productos_top(client, admin_headers, cliente_id, producto_factory, pedido_factory):
    pid = producto_factory()
    pedido_factory(cliente_id, pid, estado="ENTREGADO")
    pedido_factory(cliente_id, pid, estado="CANCELADO")  ##el cancelado no tiene que sumar
    r = client.get("/api/v1/estadisticas/productos-top", cookies=admin_headers)
    assert r.status_code == 200
    data = r.json()
    assert len(data) == 1
    assert data[0]["nombre"] == "Producto Test"
    assert data[0]["cantidad_vendida"] == 1


def test_ingresos_solo_approved(client, admin_headers, cliente_id, producto_factory, pedido_factory):
    pid = producto_factory()
    pedido_ok = pedido_factory(cliente_id, pid, estado="CONFIRMADO")
    pedido_rechazado = pedido_factory(cliente_id, pid, estado="PENDIENTE")
    _insertar_pago(pedido_ok, "approved")
    _insertar_pago(pedido_rechazado, "rejected")  ##solo los approved cuentan

    r = client.get("/api/v1/estadisticas/ingresos", cookies=admin_headers)
    assert r.status_code == 200
    data = r.json()
    assert len(data) == 1
    assert data[0]["forma_pago_codigo"] == "EFECTIVO"
    assert data[0]["cantidad"] == 1
