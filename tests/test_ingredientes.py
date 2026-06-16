def test_crear_ingrediente_con_stock(client, admin_headers):
    body = {"nombre": "Cebolla", "stock_cantidad": 25, "es_alergeno": False}

    r = client.post("/api/v1/ingredientes", json=body, cookies=admin_headers)

    assert r.status_code == 201
    assert r.json()["stock_cantidad"] == 25


def test_editar_ingrediente_actualiza_stock(client, admin_headers):
    creado = client.post(
        "/api/v1/ingredientes",
        json={"nombre": "Panceta", "stock_cantidad": 10, "es_alergeno": False},
        cookies=admin_headers,
    ).json()

    r = client.put(
        f"/api/v1/ingredientes/{creado['id']}",
        json={"stock_cantidad": 40},
        cookies=admin_headers,
    )

    assert r.status_code == 200
    assert r.json()["stock_cantidad"] == 40


def test_stock_puede_editar_ingrediente(client, admin_headers, stock_headers):
    creado = client.post(
        "/api/v1/ingredientes",
        json={"nombre": "Bacon", "stock_cantidad": 5, "es_alergeno": False},
        cookies=admin_headers,
    ).json()

    r = client.put(
        f"/api/v1/ingredientes/{creado['id']}",
        json={"stock_cantidad": 12},
        cookies=stock_headers,
    )

    assert r.status_code == 200
    assert r.json()["stock_cantidad"] == 12


def test_stock_no_puede_crear_ni_eliminar_ingrediente(client, admin_headers, stock_headers):
    crear = client.post(
        "/api/v1/ingredientes",
        json={"nombre": "Huevo", "stock_cantidad": 3, "es_alergeno": False},
        cookies=stock_headers,
    )
    assert crear.status_code == 403

    creado = client.post(
        "/api/v1/ingredientes",
        json={"nombre": "Pepino", "stock_cantidad": 3, "es_alergeno": False},
        cookies=admin_headers,
    ).json()
    eliminar = client.delete(f"/api/v1/ingredientes/{creado['id']}", cookies=stock_headers)
    assert eliminar.status_code == 403
