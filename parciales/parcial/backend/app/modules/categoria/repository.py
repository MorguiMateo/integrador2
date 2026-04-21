from __future__ import annotations

from app.core.repository import BaseRepository
from app.modules.categoria.model import Categoria


class CategoriaRepository(BaseRepository[Categoria]):
    model = Categoria

    def list(
        self,
        *,
        skip: int = 0,
        limit: int = 50,
        nombre: str | None = None,
    ) -> list[Categoria]:
        stmt = self.base_stmt()
        if nombre:
            stmt = stmt.where(Categoria.nombre.ilike(f"%{nombre}%"))
        stmt = stmt.offset(skip).limit(limit).order_by(Categoria.id)
        return list(self.session.exec(stmt).all())
