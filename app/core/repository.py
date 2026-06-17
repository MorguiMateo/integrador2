from __future__ import annotations
from datetime import datetime, timezone
from typing import Generic, Optional, TypeVar
from sqlmodel import Session, SQLModel, select
from sqlmodel.sql.expression import SelectOfScalar

ModelT = TypeVar("ModelT", bound=SQLModel)

##que sea generica permite que funcione con cualquier modelo sql.
class BaseRepository(Generic[ModelT]):
    model: type[ModelT]

    ##Recibe y guarda la session de SQLAlchemy
    def __init__(self, session: Session) -> None:
        self.session = session

    ##query base que ya filtra los borrados (soft delete)
    def base_stmt(self, *, include_deleted: bool = False) -> SelectOfScalar[ModelT]:
        stmt = select(self.model)
        if not include_deleted:

            stmt = stmt.where(self.model.deleted_at == None) 
            stmt = stmt.where(self.model.deleted_at == None)

        return stmt

    #busca por pk y devuelve none si no existe o fue borrada con borradologico 
    def get(self, id: int) -> Optional[ModelT]:
        obj = self.session.get(self.model, id)
        if obj is None or getattr(obj, "deleted_at", None) is not None:
            return None
        return obj

    #guarda identidad, impacta y guarda id en memoria y refresh actualiza el dato.
    def save(self, obj: ModelT) -> ModelT:
        self.session.add(obj)
        self.session.flush()
        self.session.refresh(obj)
        return obj

    #borrado logico por fecha 
    def soft_delete(self, id: int) -> bool:
        obj = self.session.get(self.model, id)
        if obj is None or getattr(obj, "deleted_at", None) is not None:
            return False
        obj.deleted_at = datetime.now(timezone.utc)
        self.session.add(obj)
        self.session.flush()
        return True

    #filtra una lisde ids y devuelve solo los que existen y no estan "eliminados"
    def active_ids(self, ids: list[int]) -> set[int]:
        if not ids:
            return set()
        stmt = select(self.model.id).where(
            self.model.id.in_(ids),

            self.model.deleted_at == None,  
            self.model.deleted_at == None,
        )
        return set(self.session.exec(stmt).all())
