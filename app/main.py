from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import Session

from app.core.database import create_db_and_tables, engine
from app.db.seed import run_seed
from app.modules.auth.router import router as auth_router
from app.modules.categoria.router import router as categoria_router
from app.modules.direccion_entrega.router import router as direccion_router
from app.modules.ingrediente.router import router as ingrediente_router
from app.modules.producto.router import router as producto_router
from app.modules.usuario.router import router as usuario_router
from app.modules.pedido.router import router as pedido_router
from app.modules.unidad_medida.router import router as unidad_medida_router
from app.modules.pago.router import router as pago_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()

    with Session(engine) as session:
        run_seed(session)

    yield


app = FastAPI(
    title="Parcial Integrador API",
    description="API para gestión de Categorías, Ingredientes y Productos.",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS: localhost o 127.0.0.1 y cualquier puerto en desarrollo (Vite puede servir en ambos).
app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=r"http://(localhost|127\.0\.0\.1):\d+",
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)


# Cada módulo expone su router y acá los monto en la app.
app.include_router(auth_router,  prefix="/api/v1")
app.include_router(categoria_router,  prefix="/api/v1")
app.include_router(direccion_router,  prefix="/api/v1")
app.include_router(ingrediente_router, prefix="/api/v1")
app.include_router(producto_router,  prefix="/api/v1")
app.include_router(usuario_router,  prefix="/api/v1")
app.include_router(pedido_router,  prefix="/api/v1")
app.include_router(unidad_medida_router,  prefix="/api/v1")
app.include_router(pago_router,  prefix="/api/v1")
