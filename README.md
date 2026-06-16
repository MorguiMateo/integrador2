# Food Store — Back

#INTEGRANTES:

MORGUI MATEO - DIAZ MANUEL

## Requisitos

- **Python 3.11+**
- **PostgreSQL 15+** corriendo en `localhost:5432`

#PASO 1:

```bash
createdb parcial           

python -m venv .venv
source .venv/bin/activate            
pip install -r requirements.txt

cp .env.example .env

uvicorn app.main:app --reload --port 8000
```

- **Puerto Swagger**: <http://localhost:8000/docs>

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

#Credenciales del ADMIN:

```
email:    admin@foodstore.com
password: admin123
```

## Tests

```bash
pytest                 
pytest --cov=app       
```

## Entrega

-Drive: <https://docs.google.com/spreadsheets/d/1plNcvdJT7733y3KcPK-2RKfbEN0qjQ9UljizbHL_bxo/edit?gid=183617050#gid=183617050>
-Video: _pendiente de subir — pegar el link acá_
