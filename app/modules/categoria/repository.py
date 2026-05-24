from __future__ import annotations
from typing import Optional
from app.core.repository import BaseRepository
from app.modules.categoria.model import Categoria


class CategoriaRepository(BaseRepository[Categoria]):
    model = Categoria

    def list(
        self,
        *,
        skip: int = 0,
        limit: int = 50,
        nombre: Optional[str] = None,
        incluir_eliminados: bool = False,
    ) -> list[Categoria]:
        stmt = self.base_stmt(include_deleted=incluir_eliminados)
        if nombre:
            stmt = stmt.where(Categoria.nombre.ilike(f"%{nombre}%"))
        stmt = stmt.offset(skip).limit(limit).order_by(Categoria.id)
        return list(self.session.exec(stmt).all())
