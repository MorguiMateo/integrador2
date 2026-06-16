import app.modules.upload.service as upload_service


def _fake_upload(contenido, **kwargs):
    return {
        "secure_url": "https://res.cloudinary.com/demo/image/upload/test.jpg",
        "public_id": "foodstore/test",
        "width": 100,
        "height": 100,
        "format": "jpg",
        "resource_type": "image",
    }


def test_upload_imagen_ok(client, admin_headers, monkeypatch):
    monkeypatch.setattr(upload_service.cloudinary.uploader, "upload", _fake_upload)
    r = client.post(
        "/api/v1/uploads/imagen",
        cookies=admin_headers,
        files={"file": ("test.jpg", b"contenido-falso", "image/jpeg")},
    )
    assert r.status_code == 201
    body = r.json()
    assert body["secure_url"].endswith(".jpg")
    assert body["public_id"] == "foodstore/test"


def test_upload_mime_invalido(client, admin_headers):
    r = client.post(
        "/api/v1/uploads/imagen",
        cookies=admin_headers,
        files={"file": ("test.txt", b"texto", "text/plain")},
    )
    assert r.status_code == 400


def test_upload_requiere_admin(client, client_headers):
    r = client.post(
        "/api/v1/uploads/imagen",
        cookies=client_headers,
        files={"file": ("test.jpg", b"x", "image/jpeg")},
    )
    assert r.status_code == 403


def test_eliminar_imagen_ok(client, admin_headers, monkeypatch):
    monkeypatch.setattr(upload_service.cloudinary.uploader, "destroy", lambda public_id, **kwargs: {"result": "ok"})
    r = client.delete("/api/v1/uploads/imagen/foodstore/test", cookies=admin_headers)
    assert r.status_code == 204
