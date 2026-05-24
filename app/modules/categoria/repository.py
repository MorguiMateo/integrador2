from __future__ import annotations

from typing import Optional

from sqlmodel import select

from app.core.repository import BaseRepository
from app.modules.categoria.model import Categoria
from app.modules.producto.link_models import ProductoCategoria
from app.modules.producto.model import Producto


class CategoriaRepository(BaseRepository[Categoria]):
    model = Categoria

    def list(
        self,
        *,
        skip: int = 0,
        limit: int = 50,
        nombre: Optional[str] = None,
        parent_id: Optional[int] = None,
        solo_raices: bool = False,
        incluir_eliminados: bool = False,
    ) -> list[Categoria]:
        stmt = self.base_stmt(include_deleted=incluir_eliminados)
        if nombre:
            stmt = stmt.where(Categoria.nombre.ilike(f"%{nombre}%"))
        if solo_raices:
            stmt = stmt.where(Categoria.parent_id.is_(None))
        elif parent_id is not None:
            stmt = stmt.where(Categoria.parent_id == parent_id)
        stmt = stmt.offset(skip).limit(limit).order_by(Categoria.id)
        return list(self.session.exec(stmt).all())

    def tiene_productos_activos(self, categoria_id: int) -> bool:
        stmt = (
            select(ProductoCategoria.producto_id)
            .join(Producto, Producto.id == ProductoCategoria.producto_id)
            .where(ProductoCategoria.categoria_id == categoria_id)
            .where(Producto.deleted_at.is_(None))
            .limit(1)
        )
        return self.session.exec(stmt).first() is not None
