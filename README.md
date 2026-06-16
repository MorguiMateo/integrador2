# Food Store — Backend (API)

API REST + WebSocket para la gestión integral de una tienda de comida: catálogo,
carrito, pedidos con máquina de estados, pagos vía **MercadoPago**, imágenes en
**Cloudinary** y seguimiento de pedidos en **tiempo real**.

Forma parte de un sistema de 3 repos:

| Repo | Rol | Puerto |
| :--- | :--- | :--- |
| **integrador2** (este) | Backend FastAPI | `8000` |
| **Repo-Store** | Storefront del cliente (React) | `5173` |
| **Repo-Admin** | Panel de administración (React) | `5174` |

## Stack

- **FastAPI** + **SQLModel** + **PostgreSQL**
- Arquitectura por capas: `router → service → uow → repository → model`, con `core/`
  (database, uow, repository, websocket, config, rate_limit).
- **JWT** en cookies httpOnly (access + refresh) · **RBAC** 4 roles · rate limiting.
- **MercadoPago** Checkout PRO (SDK Python) · **Cloudinary** (upload/destroy) · **WebSocket** nativo.

## Requisitos

- **Python 3.11+**
- **PostgreSQL 15+** corriendo en `localhost:5432`

## Cómo levantarlo (máquina limpia)

```bash
# 1) Crear la base de datos
createdb parcial            # o:  psql -c "CREATE DATABASE parcial;"

# 2) Entorno virtual + dependencias
python -m venv .venv
source .venv/bin/activate            # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# 3) Variables de entorno
cp .env.example .env
#   editar .env y completar SECRET_KEY, DATABASE_URL, CLOUDINARY_* y MP_*

# 4) Arrancar el servidor
uvicorn app.main:app --reload --port 8000
```

Al arrancar, la app **crea todas las tablas y corre el seed automáticamente**
(lifespan de `app/main.py`). No hace falta un paso de migración manual.

- API: <http://localhost:8000>
- **Swagger UI**: <http://localhost:8000/docs>
- ReDoc: <http://localhost:8000/redoc>
- Prefijo de todos los endpoints: `/api/v1`

> **Re-sembrar manualmente:** `python -m app.db.seed`
> (requiere que las tablas ya existan, es decir, haber arrancado la app al menos una vez).

## Variables de entorno

Ver `.env.example` para la lista completa y comentada.

| Variable | Descripción |
| :--- | :--- |
| `DATABASE_URL` | Conexión a PostgreSQL (`postgresql+psycopg2://...`) |
| `SECRET_KEY` | Clave para firmar JWT (mín. 32 chars) |
| `ALGORITHM` / `ACCESS_TOKEN_EXPIRE_MINUTES` / `REFRESH_TOKEN_EXPIRE_DAYS` | Config JWT |
| `CLOUDINARY_CLOUD_NAME` / `CLOUDINARY_API_KEY` / `CLOUDINARY_API_SECRET` | Cloudinary |
| `MP_ACCESS_TOKEN` / `MP_PUBLIC_KEY` | Credenciales MercadoPago |
| `MP_WEBHOOK_SECRET` / `MP_NOTIFICATION_URL` | Webhook IPN (opcional; requiere exponer el backend) |
| `FRONTEND_URL` | URL del storefront para las back_urls del checkout |

> El WebSocket (`/api/v1/pedidos/ws`) se autentica con la **misma cookie httpOnly**
> del login; no necesita variables aparte. El CORS está preconfigurado en `app/main.py`
> para aceptar cualquier puerto de `localhost`/`127.0.0.1` con credenciales.

## Seed inicial (datos obligatorios)

Se cargan automáticamente: roles (`ADMIN`, `STOCK`, `PEDIDOS`, `CLIENT`), estados de
pedido (5), formas de pago (`MERCADOPAGO`, `EFECTIVO`, `TRANSFERENCIA`), unidades de
medida y un usuario administrador:

```
email:    admin@foodstore.com
password: admin123
```

## Módulos (feature-first)

```
app/
├── main.py                 # app, CORS, routers, lifespan (crea tablas + seed)
├── core/                   # database · uow · repository · websocket · config · rate_limit
├── db/seed.py              # seed de catálogos + usuario admin
└── modules/
    ├── auth/               # login/register/refresh/logout · JWT cookies · rate limit
    ├── usuario/  usuario_rol/  direccion_entrega/
    ├── categoria/  ingrediente/  unidad_medida/  producto/
    ├── pedido/             # FSM 5 estados · audit trail append-only · WebSocket
    ├── pago/               # MercadoPago: /crear, /preferencia, /webhook, /{pedido_id}
    ├── upload/             # Cloudinary upload/destroy
    ├── estadisticas/       # KPIs y métricas (solo ADMIN)
    └── admin/              # catálogos y gestión desde el panel
```

## Endpoints destacados

- `POST /api/v1/auth/login` · `POST /api/v1/auth/register` · `POST /api/v1/auth/refresh` · `POST /api/v1/auth/logout`
- `GET/POST /api/v1/productos` · `GET /api/v1/pedidos` · `POST /api/v1/pedidos`
- `POST /api/v1/pedidos/{id}/avanzar` · `POST /api/v1/pedidos/{id}/cancelar`
- `POST /api/v1/pagos/preferencia` · `POST /api/v1/pagos/webhook`
- `POST /api/v1/uploads/imagen` · `GET /api/v1/estadisticas/*`
- **WebSocket**: `ws://localhost:8000/api/v1/pedidos/ws` (feed de pedidos, auth por cookie)

## Tests

Suite de integración con **pytest** sobre una base PostgreSQL de test (`parcial_test`),
que el `conftest.py` **crea automáticamente** (necesita un Postgres accesible):

```bash
pytest                 # corre toda la suite
pytest --cov=app       # con cobertura
```

## Entrega

- Carpeta del proyecto (Drive): <https://drive.google.com/drive/u/0/folders/1rD6m_CmaMqE0NhEshcEeYeRTF7zvpcle>
- 🎥 Video demo (10–15 min): _pendiente de subir — pegar el link acá_
