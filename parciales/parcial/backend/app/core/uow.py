"""Unit of Work mínimo sobre SQLModel Session.

Un UoW agrupa cambios en una transacción y decide si hacer commit o rollback
al salir del contexto. Los services reciben el UoW en lugar de la session cruda.
"""
from __future__ import annotations

from types import TracebackType
from typing import Optional, Type

from sqlmodel import Session

from app.core.database import engine


class UnitOfWork:
    session: Session

    def __enter__(self) -> "UnitOfWork":
        # expire_on_commit=False evita que SQLAlchemy "expire" los atributos
        # al commitear. Sin esto, al cerrar la session del UoW los objetos
        # devueltos al router quedan detached y FastAPI falla al serializarlos
        # con response_model (DetachedInstanceError).
        self.session = Session(engine, expire_on_commit=False)
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
