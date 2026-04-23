from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.database import create_db_and_tables
from app.modules.categoria.router import router as categoria_router
from app.modules.ingrediente.router import router as ingrediente_router
from app.modules.producto.router import router as producto_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield


app = FastAPI(
    title="Parcial Integrador API",
    description="API para gestión de Categorías, Ingredientes y Productos.",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS: acepta cualquier puerto de localhost en desarrollo (5173, 5174, etc.)
# para no tener que hardcodear el puerto cuando Vite lo cambia si está ocupado.
app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=r"http://localhost:\d+",
    allow_methods=["*"],
    allow_headers=["*"],
)

#Cada módulo expone su router y acá los monto en la app.
app.include_router(categoria_router)
app.include_router(ingrediente_router)
app.include_router(producto_router)


@app.get("/", tags=["health"])
def health():
    return {"status": "ok"}
