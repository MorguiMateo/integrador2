# BaseRepository es la única pieza que habla con la base de datos.
# Los services le piden datos a él; nunca tocan la session directamente.
# Está diseñado para una sola entidad (ModelT) y aplica soft delete en todas
# las consultas: los registros borrados no desaparecen de la DB, solo tienen
# deleted_at poblado, lo que preserva la integridad de las relaciones.
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
        # Punto de partida de todas las queries: filtra deleted_at IS NULL
        # para que los registros con soft delete nunca aparezcan en resultados.
        return select(self.model).where(self.model.deleted_at == None)  # noqa: E711

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
