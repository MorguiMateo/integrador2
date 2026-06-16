import os
from decimal import Decimal
from urllib.parse import urlsplit, urlunsplit

import psycopg2
from psycopg2 import sql


def _resolver_url_base() -> str:
    base = os.getenv("DATABASE_URL")
    if not base:
        from dotenv import dotenv_values

        env_path = os.path.join(os.path.dirname(__file__), "..", ".env")
        base = dotenv_values(env_path).get("DATABASE_URL")
    return base or "postgresql+psycopg2://postgres@localhost:5432/parcial"


_PARTS = urlsplit(_resolver_url_base())
_TEST_DB = (_PARTS.path.lstrip("/") or "parcial") + "_test"
_TEST_URL = urlunsplit((_PARTS.scheme, _PARTS.netloc, "/" + _TEST_DB, _PARTS.query, _PARTS.fragment))


def _crear_base_de_test() -> None:
    dsn = {
        "host": _PARTS.hostname or "localhost",
        "port": _PARTS.port or 5432,
        "user": _PARTS.username or "postgres",
        "dbname": "postgres",
    }
    if _PARTS.password:
        dsn["password"] = _PARTS.password
    conn = psycopg2.connect(**dsn)
    conn.autocommit = True
    cur = conn.cursor()
    cur.execute("SELECT 1 FROM pg_database WHERE datname = %s", (_TEST_DB,))
    if not cur.fetchone():
        cur.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier(_TEST_DB)))
    cur.close()
    conn.close()


_crear_base_de_test()
os.environ["DATABASE_URL"] = _TEST_URL

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import text
from sqlmodel import Session, SQLModel, select

from app.core.database import engine
from app.core.rate_limit import login_rate_limiter
from app.core.security import get_password_hash
from app.db.seed import run_seed
from app.main import app
from app.modules.pedido.model import DetallePedido, HistorialEstadoPedido, Pedido
from app.modules.producto.model import Producto
from app.modules.usuario.model import Usuario
from app.modules.usuario_rol.model import UsuarioRol


@pytest.fixture(scope="session", autouse=True)
def _crear_schema():
    SQLModel.metadata.drop_all(engine)
    SQLModel.metadata.create_all(engine)
    yield
    SQLModel.metadata.drop_all(engine)


@pytest.fixture(autouse=True)
def db_session():
    login_rate_limiter.reset()
    with engine.begin() as conn:
        for tabla in reversed(SQLModel.metadata.sorted_tables):
            conn.execute(text(f'TRUNCATE TABLE "{tabla.name}" RESTART IDENTITY CASCADE'))
    with Session(engine) as session:
        run_seed(session)
        session.commit()
    with Session(engine) as session:
        yield session


@pytest.fixture
def client():
    return TestClient(app)


def _login(email: str, password: str) -> dict:
    with TestClient(app) as c:
        r = c.post("/api/v1/auth/login", json={"email": email, "password": password})
        return dict(r.cookies)


@pytest.fixture
def admin_headers() -> dict:
    return _login("admin@foodstore.com", "admin123")


@pytest.fixture
def client_headers(client) -> dict:
    client.post(
        "/api/v1/auth/register",
        json={"nombre": "Cli", "apellido": "Ente", "email": "cli@test.com", "password": "cliente123"},
    )
    return _login("cli@test.com", "cliente123")


@pytest.fixture
def pedidos_headers() -> dict:
    with Session(engine) as session:
        usuario = Usuario(
            nombre="Ped",
            apellido="Idos",
            email="ped@test.com",
            password_hash=get_password_hash("pedidos123"),
        )
        session.add(usuario)
        session.flush()
        session.add(UsuarioRol(usuario_id=usuario.id, rol_codigo="PEDIDOS"))
        session.commit()
    return _login("ped@test.com", "pedidos123")


@pytest.fixture
def cliente_id(client_headers) -> int:
    with Session(engine) as session:
        usuario = session.exec(select(Usuario).where(Usuario.email == "cli@test.com")).first()
        return usuario.id


@pytest.fixture
def producto_factory():
    def _make(nombre: str = "Producto Test", precio: float = 1000.0, stock: int = 10, disponible: bool = True) -> int:
        with Session(engine) as session:
            producto = Producto(
                nombre=nombre,
                precio_base=precio,
                stock_cantidad=stock,
                disponible=disponible,
                imagenes_url=[],
            )
            session.add(producto)
            session.commit()
            session.refresh(producto)
            return producto.id

    return _make


@pytest.fixture
def pedido_factory():
    def _make(usuario_id: int, producto_id: int, cantidad: int = 1, estado: str = "PENDIENTE") -> int:
        with Session(engine) as session:
            pedido = Pedido(
                usuario_id=usuario_id,
                forma_pago_codigo="EFECTIVO",
                estado_codigo=estado,
                subtotal=Decimal("1000.00"),
                descuento=Decimal("0.00"),
                costo_envio=Decimal("50.00"),
                total=Decimal("1050.00"),
            )
            session.add(pedido)
            session.flush()
            session.add(
                DetallePedido(
                    pedido_id=pedido.id,
                    producto_id=producto_id,
                    cantidad=cantidad,
                    nombre_snapshot="Producto Test",
                    precio_snapshot=Decimal("1000.00"),
                    subtotal_snap=Decimal("1000.00"),
                    personalizacion=[],
                )
            )
            session.add(
                HistorialEstadoPedido(
                    pedido_id=pedido.id,
                    estado_desde=None,
                    estado_hacia=estado,
                    usuario_id=usuario_id,
                )
            )
            session.commit()
            session.refresh(pedido)
            return pedido.id

    return _make
