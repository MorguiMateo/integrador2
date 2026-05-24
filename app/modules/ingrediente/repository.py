from __future__ import annotations
from typing import Optional
from sqlmodel import select
from app.core.repository import BaseRepository
from app.modules.ingrediente.model import Ingrediente


class IngredienteRepository(BaseRepository[Ingrediente]):
    model = Ingrediente

    def base_stmt(self, *, include_deleted: bool = False):
        return select(self.model)

    def list(self, *, skip: int = 0, limit: int = 50, nombre: Optional[str] = None, es_alergeno: Optional[bool] = None) -> list[Ingrediente]:
        stmt = self.base_stmt()
        if nombre:
            stmt = stmt.where(Ingrediente.nombre.ilike(f"%{nombre}%"))
        if es_alergeno is not None:
            stmt = stmt.where(Ingrediente.es_alergeno == es_alergeno)
        stmt = stmt.offset(skip).limit(limit).order_by(Ingrediente.id)
        return list(self.session.exec(stmt).all())

    def delete(self, ingrediente_id: int) -> bool:
        obj = self.session.get(self.model, ingrediente_id)
        if obj is None:
            return False
        self.session.delete(obj)
        self.session.flush()
        return True
