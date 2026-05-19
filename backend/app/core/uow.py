# UnitOfWork envuelve cada request en una sola transacción de DB.
# Al entrar al `with` abre la session y crea los repos.
# Al salir hace commit si todo salió bien, o rollback si hubo cualquier error.
# Los services usan uow.categorias / uow.ingredientes / uow.productos
# sin tocar la session directamente.
from __future__ import annotations

from types import TracebackType
from typing import Optional, Type

from sqlmodel import Session

from app.core.database import engine
from app.modules.categoria.repository import CategoriaRepository
from app.modules.ingrediente.repository import IngredienteRepository
from app.modules.producto.repository import ProductoRepository


class UnitOfWork:
    session: Session
    categorias: CategoriaRepository
    ingredientes: IngredienteRepository
    productos: ProductoRepository

    def __enter__(self) -> "UnitOfWork":
        # expire_on_commit=False evita que SQLAlchemy "expire" los atributos
        # al commitear. Sin esto, al cerrar la session del UoW los objetos
        # devueltos al router quedan detached y FastAPI falla al serializarlos
        # con response_model (DetachedInstanceError).
        self.session = Session(engine, expire_on_commit=False)
        self.categorias = CategoriaRepository(self.session)
        self.ingredientes = IngredienteRepository(self.session)
        self.productos = ProductoRepository(self.session)
        return self

    def __exit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc: Optional[BaseException],
        tb: Optional[TracebackType],
    ) -> None:
        # Si no hubo excepción -> commit; si hubo cualquier error -> rollback.
        # La session siempre se cierra en el finally, sin importar qué pasó.
        try:
            if exc_type is None:
                self.session.commit()
            else:
                self.session.rollback()
        finally:
            self.session.close()
