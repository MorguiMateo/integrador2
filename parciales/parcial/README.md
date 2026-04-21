# Parcial Integrador — Fullstack

Proyecto fullstack para la gestión de **Categorías**, **Ingredientes** y
**Productos**, con relaciones **1:N** y **N:N**, persistencia en PostgreSQL y un
frontend en React + TanStack Query.

> **Estado**: backend CRUD funcional con soft-delete, validaciones con
> `Annotated`/`Query`/`Path`, `response_model` dedicados y UoW por request.
> Frontend con setup completo (router con ruta dinámica, TanStack Query,
> Tailwind 4, hooks de `useQuery`/`useMutation`/`invalidateQueries`) y las
> páginas/modales en implementación.

## Stack

- **Backend**: FastAPI + SQLModel + PostgreSQL, organizado por módulos
  (`router`, `schema`, `service`, `model`) + `core` (database, uow).
- **Frontend**: React 19 + TypeScript + Vite + Tailwind CSS 4 + TanStack Query
  v5 + React Router v7. Estructurado por features.

## Modelo de datos

- `Categoria` (1:N auto-referencial vía `parent_id` → `children`) con
  soft-delete (`deleted_at`).
- `Ingrediente` con soft-delete (`deleted_at`).
- `Producto` con soft-delete (`deleted_at`).
- `ProductoCategoria` → **N:N** entre `Producto` y `Categoria` con payload
  (`es_principal`).
- `ProductoIngrediente` → **N:N** entre `Producto` e `Ingrediente` con payload
  (`es_removible`).

## Cómo levantarlo

### Requisitos

- Python 3.11+
- Node 18+ con `pnpm`
- PostgreSQL 14+ (crear la DB: `CREATE DATABASE parcial;`)

### Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # ajustar DATABASE_URL si hace falta
fastapi dev app/main.py
```

- API: <http://localhost:8000>
- Docs: <http://localhost:8000/docs>

### Frontend

```bash
cd frontend
pnpm install
pnpm dev
```

- App: <http://localhost:5173>
- Variable opcional: `VITE_API_URL` (default `http://localhost:8000`).

## Estructura

```
parcial/
├── backend/
│   ├── requirements.txt
│   ├── .env.example
│   └── app/
│       ├── main.py
│       ├── core/         # database.py, uow.py
│       ├── categoria/    # model, schema, service, router
│       ├── ingrediente/  # idem
│       └── producto/     # idem + link_models.py
└── frontend/
    └── src/
        ├── main.tsx, App.tsx, index.css
        ├── app/          # router.tsx, queryClient.ts
        ├── lib/          # apiClient.ts
        ├── shared/components/
        ├── categorias/
        ├── ingredientes/
        └── productos/
```

## Video

> TODO: agregar link al video (YouTube unlisted o Drive).
