##los ingredientes NO se descuentan al crear el producto, sino al hacer el pedido (receta x cantidad)
from sqlmodel import Session, select

from app.core.database import engine
from app.modules.ingrediente.model import Ingrediente
from app.modules.unidad_medida.model import UnidadMedida


def _unidad_id() -> int:
    with Session(engine) as session:
        return session.exec(select(UnidadMedida)).first().id


def _crear_ingrediente(nombre: str, stock: int) -> int:
    with Session(engine) as session:
        ing = Ingrediente(nombre=nombre, stock_cantidad=stock)
        session.add(ing)
        session.commit()
        session.refresh(ing)
        return ing.id


def _stock(ing_id: int) -> int:
    with Session(engine) as session:
        return session.get(Ingrediente, ing_id).stock_cantidad


def _crear_producto_con_ingrediente(
    client, admin_headers, ing_id: int, unidad_id: int, *, cantidad: float = 1.0, stock_producto: int = 100
) -> int:
    body = {
        "nombre": "Burger Test",
        "precio_base": 1500.00,
        "imagenes_url": [],
        "stock_cantidad": stock_producto,
        "disponible": True,
        "categorias": [],
        "ingredientes": [
            {
                "ingrediente_id": ing_id,
                "es_removible": False,
                "cantidad": cantidad,
                "unidad_medida_id": unidad_id,
            }
        ],
    }
    r = client.post("/api/v1/productos", json=body, cookies=admin_headers)
    assert r.status_code == 201, r.text
    return r.json()["id"]


def _pedir(client, client_headers, producto_id: int, cantidad: int):
    return client.post(
        "/api/v1/pedidos",
        json={
            "items": [{"producto_id": producto_id, "cantidad": cantidad}],
            "forma_pago_codigo": "EFECTIVO",
            "direccion_id": None,
            "notas": None,
        },
        cookies=client_headers,
    )


def test_crear_producto_no_descuenta_ingrediente(client, admin_headers):
    ing_id = _crear_ingrediente("Cheddar A", 5)
    _crear_producto_con_ingrediente(client, admin_headers, ing_id, _unidad_id(), cantidad=1.0)
    assert _stock(ing_id) == 5  ##crear el producto no toca el stock del ingrediente


def test_pedido_descuenta_ingrediente_por_cantidad(client, admin_headers, client_headers):
    ing_id = _crear_ingrediente("Cheddar B", 5)
    prod_id = _crear_producto_con_ingrediente(client, admin_headers, ing_id, _unidad_id(), cantidad=1.0)

    r = _pedir(client, client_headers, prod_id, cantidad=3)

    assert r.status_code == 201, r.text
    assert _stock(ing_id) == 2  ##5 - 3*1


def test_pedido_que_excede_ingrediente_se_bloquea(client, admin_headers, client_headers):
    ing_id = _crear_ingrediente("Cheddar C", 5)
    prod_id = _crear_producto_con_ingrediente(client, admin_headers, ing_id, _unidad_id(), cantidad=1.0)

    ##5 fetas, 1 por burger, pide 6 -> no alcanza para la 6ta
    r = _pedir(client, client_headers, prod_id, cantidad=6)

    assert r.status_code == 400, r.text
    assert _stock(ing_id) == 5  ##rollback del UoW: no se consumio nada
