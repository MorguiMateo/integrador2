from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.categoria.router import router as categoria_router
from app.core.database import create_db_and_tables
from app.ingrediente.router import router as ingrediente_router
from app.producto.router import router as producto_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield


app = FastAPI(
    title="Parcial Fullstack - API",
    description=(
        "Gestor de productos con categorías (N:N) e ingredientes (1:N via "
        "ProductoIngrediente). Persistencia en PostgreSQL con SQLModel."
    ),
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(categoria_router)
app.include_router(ingrediente_router)
app.include_router(producto_router)


@app.get("/")
def root():
    return {
        "ok": True,
        "service": "Parcial Fullstack API",
        "docs": "/docs",
    }
