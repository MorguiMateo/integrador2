"""Unit of Work sobre SQLModel Session.

El UoW agrupa cambios en una transacción y decide si hacer commit o rollback
al salir del contexto. Además expone los repositorios por módulo, de modo
que los services no toquen `session` directamente:

    with UnitOfWork() as uow:
        categoria = uow.categorias.get(1)
        ...
"""
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
        try:
            if exc_type is None:
                self.session.commit()
            else:
                self.session.rollback()
        finally:
            self.session.close()
