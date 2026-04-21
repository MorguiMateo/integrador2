"""Base Repository genérico.

Un Repository encapsula el acceso a datos de UNA entidad. Los services reciben
el repo desde el UoW y no tocan `session` directamente.

Asunciones del Base:
- La entidad tiene columna `deleted_at` (soft-delete). `get`, `soft_delete` y
  `base_stmt` filtran por `deleted_at IS NULL`.
- Si una entidad no tiene `deleted_at`, el subtipo puede sobreescribir estos
  métodos o simplemente no usarlos.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Generic, TypeVar

from sqlmodel import Session, SQLModel, select
from sqlmodel.sql.expression import SelectOfScalar

ModelT = TypeVar("ModelT", bound=SQLModel)


class BaseRepository(Generic[ModelT]):
    model: type[ModelT]

    def __init__(self, session: Session) -> None:
        self.session = session

    def base_stmt(self) -> SelectOfScalar[ModelT]:
        return select(self.model).where(self.model.deleted_at == None)  # noqa: E711

    def get(self, id: int) -> ModelT | None:
        obj = self.session.get(self.model, id)
        if obj is None or getattr(obj, "deleted_at", None) is not None:
            return None
        return obj

    def save(self, obj: ModelT) -> ModelT:
        """Persistir cambios de una instancia (create o update)."""
        self.session.add(obj)
        self.session.flush()
        self.session.refresh(obj)
        return obj

    def soft_delete(self, id: int) -> bool:
        obj = self.session.get(self.model, id)
        if obj is None or getattr(obj, "deleted_at", None) is not None:
            return False
        obj.deleted_at = datetime.now(timezone.utc)
        self.session.add(obj)
        self.session.flush()
        return True

    def active_ids(self, ids: list[int]) -> set[int]:
        """Devuelve el subconjunto de `ids` que existe y está activo."""
        if not ids:
            return set()
        stmt = select(self.model.id).where(
            self.model.id.in_(ids),
            self.model.deleted_at == None,  # noqa: E711
        )
        return set(self.session.exec(stmt).all())
