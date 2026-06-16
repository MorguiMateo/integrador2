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


def test_logout_ok(client):
    _registrar(client, email="logout@test.com")
    client.post("/api/v1/auth/login", json={"email": "logout@test.com", "password": "secreto123"})

    r = client.post("/api/v1/auth/logout")
    assert r.status_code == 204
    # tras el logout se borran las cookies de sesión → /me vuelve a quedar sin autenticar
    assert client.get("/api/v1/auth/me").status_code == 401


def test_login_rate_limit_429(client):
    # spec §4.3: 5 intentos fallidos por IP en 15 min → el 6º responde 429 + Retry-After
    _registrar(client, email="rl@test.com")
    respuesta = None
    for _ in range(6):
        respuesta = client.post("/api/v1/auth/login", json={"email": "rl@test.com", "password": "incorrecta"})
    assert respuesta.status_code == 429
    assert "retry-after" in {k.lower() for k in respuesta.headers}


def test_login_correcto_no_bloquea(client):
    # los logins exitosos no cuentan como intentos fallidos
    _registrar(client, email="ok@test.com", password="secreto123")
    for _ in range(8):
        r = client.post("/api/v1/auth/login", json={"email": "ok@test.com", "password": "secreto123"})
        assert r.status_code == 200
