# Parcial Fullstack — FastAPI + React

Aplicación fullstack para la gestión de **productos**, **categorías** e
**ingredientes**, con relaciones N:N y 1:N, persistencia en PostgreSQL y un
frontend en React + TanStack Query.

## Descripción

- **Backend**: FastAPI + SQLModel + PostgreSQL, organizado por módulos
  (`routers`, `schemas`, `services`, `models`, `uow`).
- **Frontend**: React + TypeScript + Vite + Tailwind CSS 4 + TanStack Query +
  React Router. Estructurado por features (`categorias/`, `ingredientes/`,
  `productos/`, `shared/`).

## Modelo de datos

- `Categoria` (tabla `categorias`)
- `Ingrediente` (tabla `ingredientes`)
- `Producto` (tabla `productos`)
- `ProductoCategoria` (tabla `producto_categoria`) → **N:N** entre Producto y
  Categoría (`link_model` + `back_populates`).
- `ProductoIngrediente` (tabla `producto_ingrediente`) → objeto de asociación
  con campos `cantidad` y `unidad`. Genera **1:N** desde `Producto` y desde
  `Ingrediente`.

## Requisitos previos

- Python 3.11+
- Node 18+
- PostgreSQL 14+

Crear la base de datos (ejemplo):

```sql
CREATE DATABASE parcial_fullstack;
```

## Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate       # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env             # ajustar DATABASE_URL si hace falta
fastapi dev app/main.py          # levanta el server en http://localhost:8000
```

Docs interactivas: <http://localhost:8000/docs>

## Frontend

```bash
cd frontend
npm install
npm run dev                      # http://localhost:5173
```

Variable opcional: `VITE_API_URL` (por defecto apunta a
`http://localhost:8000`).

## Endpoints principales

- `GET/POST/PUT/DELETE /categorias`
- `GET/POST/PUT/DELETE /ingredientes`
- `GET/POST/PUT/DELETE /productos` (acepta `categoria_ids` e `ingredientes` con
  `cantidad` y `unidad`).
- Filtros y paginación con `Annotated[..., Query(...)]` (`skip`, `limit`, `q`,
  `activo`, `precio_min`, `precio_max`).

## Estructura

```
parcial-fullstack/
├── backend/
│   ├── requirements.txt
│   ├── .env.example
│   └── app/
│       ├── main.py
│       ├── core/ (database.py, uow.py)
│       ├── categoria/ (model, schema, service, router)
│       ├── ingrediente/
│       └── producto/ (+ link_models.py)
└── frontend/
    └── src/
        ├── app/ (router, layout)
        ├── lib/ (api-client)
        ├── shared/components/
        ├── categorias/ (page, api, types, hooks, components)
        ├── ingredientes/
        └── productos/
```

## Video

> TODO: agregar link al video (YouTube oculto o Drive).
