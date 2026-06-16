def _registrar(client, email="nuevo@test.com", password="secreto123"):
    return client.post(
        "/api/v1/auth/register",
        json={"nombre": "Nuevo", "apellido": "Usuario", "email": email, "password": password},
    )


def test_register_ok(client):
    r = _registrar(client)
    assert r.status_code == 201
    body = r.json()
    assert body["email"] == "nuevo@test.com"
    assert "password_hash" not in body


def test_login_ok(client):
    _registrar(client, email="login@test.com")
    r = client.post("/api/v1/auth/login", json={"email": "login@test.com", "password": "secreto123"})
    assert r.status_code == 200
    assert "access_token" in r.cookies


def test_login_credenciales_invalidas(client):
    _registrar(client, email="malpass@test.com")
    r = client.post("/api/v1/auth/login", json={"email": "malpass@test.com", "password": "incorrecta"})
    assert r.status_code == 401


def test_me_requiere_autenticacion(client):
    assert client.get("/api/v1/auth/me").status_code == 401


def test_me_autenticado(client):
    _registrar(client, email="me@test.com")
    client.post("/api/v1/auth/login", json={"email": "me@test.com", "password": "secreto123"})
    r = client.get("/api/v1/auth/me")
    assert r.status_code == 200
    assert r.json()["email"] == "me@test.com"
