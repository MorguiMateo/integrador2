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

    def base_stmt(self, *, include_deleted: bool = False) -> SelectOfScalar[ModelT]:
        # Por defecto filtra deleted_at IS NULL. Con include_deleted=True el backoffice
        # puede listar también filas desactivadas (soft delete) para mostrarlas en gris.
        stmt = select(self.model)
        if not include_deleted:
            stmt = stmt.where(self.model.deleted_at == None)  # noqa: E711
        return stmt

    def get(self, id: int) -> ModelT | None:
        obj = self.session.get(self.model, id)
        if obj is None or getattr(obj, "deleted_at", None) is not None:
            return None
        return obj

    def save(self, obj: ModelT) -> ModelT:
        #Persistir cambios de una instancia (create o update)
        self.session.add(obj)
        self.session.flush()
        self.session.refresh(obj)
        return obj

    def soft_delete(self, id: int) -> bool:
        # No elimina la fila; pone deleted_at = now(). La fila sigue en la DB,
        # esto evita romper FKs que apuntan a este registro.
        obj = self.session.get(self.model, id)
        if obj is None or getattr(obj, "deleted_at", None) is not None:
            return False
        obj.deleted_at = datetime.now(timezone.utc)
        self.session.add(obj)
        self.session.flush()
        return True

    def active_ids(self, ids: list[int]) -> set[int]:
        #Devuelve el subconjunto de `ids` que existe y no está borrado
        if not ids:
            return set()
        stmt = select(self.model.id).where(
            self.model.id.in_(ids),
            self.model.deleted_at == None,  # noqa: E711
        )
        return set(self.session.exec(stmt).all())
