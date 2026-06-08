# Parcial Integrador — Backend

API REST para la gestión de **Categorías**, **Ingredientes** y **Productos**,
con relaciones **1:N** y **N:N**, persistencia en PostgreSQL y soft-delete.

> **Estado**: CRUD funcional con soft-delete, validaciones con
> `Annotated`/`Query`/`Path`, `response_model` dedicados y UoW por request.

## Stack

- **FastAPI** + **SQLModel** + **PostgreSQL**, organizado por módulos
  (`router`, `schema`, `service`, `model`) + `core` (database, uow).

## Modelo de datos

- `Categoria` (1:N auto-referencial vía `parent_id` → `children`) con soft-delete (`deleted_at`).
- `Ingrediente` con soft-delete (`deleted_at`).
- `Producto` con soft-delete (`deleted_at`).
- `ProductoCategoria` → **N:N** entre `Producto` y `Categoria` con payload (`es_principal`).
- `ProductoIngrediente` → **N:N** entre `Producto` e `Ingrediente` con payload (`es_removible`).

## Cómo levantarlo

### Requisitos

- Python 3.11+
- PostgreSQL 14+ (crear la DB: `CREATE DATABASE parcial;`)

### Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
# ajustar DATABASE_URL en .env si hace falta
fastapi dev app/main.py
```

- API: <http://localhost:8000>
- Docs: <http://localhost:8000/docs>

## Estructura

```
integrador2/
├── app/
│   ├── main.py
│   ├── core/         # database.py, uow.py, repository.py
│   ├── modules/
│   │   ├── categoria/    # model, schema, service, router
│   │   ├── ingrediente/  # idem
│   │   └── producto/     # idem + link_models.py
├── requirements.txt
└── .env
```




DRIVE: https://drive.google.com/drive/u/0/folders/1rD6m_CmaMqE0NhEshcEeYeRTF7zvpcle
