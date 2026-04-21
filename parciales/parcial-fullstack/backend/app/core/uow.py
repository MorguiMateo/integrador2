from __future__ import annotations

from sqlmodel import Session

from .database import engine


class UnitOfWork:
    """Envuelve una sesión SQLModel en un contexto transaccional.

    Permite que los servicios ejecuten varias operaciones atómicas
    con un único commit/rollback.
    """

    def __init__(self) -> None:
        self.session: Session | None = None

    def __enter__(self) -> "UnitOfWork":
        self.session = Session(engine)
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        if self.session is None:
            return
        try:
            if exc_type is not None:
                self.session.rollback()
            else:
                self.session.commit()
        finally:
            self.session.close()
            self.session = None

    def commit(self) -> None:
        if self.session is not None:
            self.session.commit()

    def rollback(self) -> None:
        if self.session is not None:
            self.session.rollback()
