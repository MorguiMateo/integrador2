from __future__ import annotations
from typing import Optional
from sqlmodel import select, delete as sql_delete
from app.core.repository import BaseRepository
from app.modules.ingrediente.model import Ingrediente


class IngredienteRepository(BaseRepository[Ingrediente]):
    model = Ingrediente

    def base_stmt(self, *, include_deleted: bool = False):
        return select(self.model)

    def active_ids(self, ids: list[int]) -> set[int]:
        # Ingrediente no tiene soft-delete (deleted_at): no se filtra por él.
        if not ids:
            return set()
        stmt = select(self.model.id).where(self.model.id.in_(ids))
        return set(self.session.exec(stmt).all())

    def list(
        self,
        *,
        skip: int = 0,
        limit: int = 50,
        nombre: Optional[str] = None,
        es_alergeno: Optional[bool] = None,
    ) -> list[Ingrediente]:
        stmt = self.base_stmt()
        if nombre:
            stmt = stmt.where(Ingrediente.nombre.ilike(f"%{nombre}%"))
        if es_alergeno is not None:
            stmt = stmt.where(Ingrediente.es_alergeno == es_alergeno)
        stmt = stmt.offset(skip).limit(limit).order_by(Ingrediente.id)
        return list(self.session.exec(stmt).all())

    def tiene_productos_activos(self, ingrediente_id: int) -> bool:
        from app.modules.producto.link_models import ProductoIngrediente
        from app.modules.producto.model import Producto
        stmt = (
            select(ProductoIngrediente)
            .join(Producto, ProductoIngrediente.producto_id == Producto.id)
            .where(
                ProductoIngrediente.ingrediente_id == ingrediente_id,
                Producto.deleted_at.is_(None),
            )
            .limit(1)
        )
        return self.session.exec(stmt).first() is not None

    def delete(self, ingrediente_id: int) -> bool:
        from app.modules.producto.link_models import ProductoIngrediente

        obj = self.session.get(self.model, ingrediente_id)
        if obj is None:
            return False

        # Elimina los registros de la tabla link primero usando SQL directo.
        # Si se usa session.delete(obj) sin esto, SQLAlchemy intenta hacer SET NULL
        # en producto_ingrediente.ingrediente_id que es PK, lo que lanza AssertionError.
        self.session.exec(
            sql_delete(ProductoIngrediente).where(ProductoIngrediente.ingrediente_id == ingrediente_id)
        )
        # Expira el estado cacheado del objeto para que SQLAlchemy no vea
        # producto_links en memoria al procesar el delete.
        self.session.expire(obj)

        self.session.delete(obj)
        self.session.flush()
        return True
