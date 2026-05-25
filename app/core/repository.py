from __future__ import annotations
from datetime import datetime, timezone
from typing import Generic, Optional, TypeVar
from sqlmodel import Session, SQLModel, select
from sqlmodel.sql.expression import SelectOfScalar

ModelT = TypeVar("ModelT", bound=SQLModel)


class BaseRepository(Generic[ModelT]):
    model: type[ModelT]

    def __init__(self, session: Session) -> None:
        self.session = session

    def base_stmt(self, *, include_deleted: bool = False) -> SelectOfScalar[ModelT]:
        stmt = select(self.model)
        if not include_deleted:
            stmt = stmt.where(self.model.deleted_at == None)
        return stmt

    def get(self, id: int) -> Optional[ModelT]:
        obj = self.session.get(self.model, id)
        if obj is None or getattr(obj, "deleted_at", None) is not None:
            return None
        return obj

    def save(self, obj: ModelT) -> ModelT:
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
        if not ids:
            return set()
        stmt = select(self.model.id).where(
            self.model.id.in_(ids),
            self.model.deleted_at == None,
        )
        return set(self.session.exec(stmt).all())
