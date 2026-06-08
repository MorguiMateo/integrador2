from __future__ import annotations
from typing import Optional
from sqlmodel import select, delete as sql_delete
from app.core.repository import BaseRepository
from app.modules.ingrediente.model import Ingrediente

##hereda de BaseRepository y sobreescribe lo que necesita ingrediente en particular
class IngredienteRepository(BaseRepository[Ingrediente]):
    model = Ingrediente

    ##ingrediente no tiene deleted_at entonces hace un select simple
    ##sobreescrive el del base repository
    def base_stmt(self, *, include_deleted: bool = False):
        return select(self.model) #sin filtro deleted_at#

    ##mismo motivo que base_stmt
    def active_ids(self, ids: list[int]) -> set[int]:
        if not ids:
            return set()
        stmt = select(self.model.id).where(self.model.id.in_(ids))
        return set(self.session.exec(stmt).all())

    ##construye una query con filtros opcionales de nombre y es_alergeno + paginacion.
    ##Metodo que trae muchos ingredientes de la base de datos con filtros opcionales y paginacion.
    ## retorna lista de objetos ingrediente.
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

    ## hace join entre la tabla ProductoIngrediente y Producto para ver si el ingrediente esta en uso en algun producto que no este eliminado.
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

    #reemplaza el soft_delete con un hard delete. primero borra los registros de la tabla ProductoIngrediente y despues borra el ingrediente en si. 
    def delete(self, ingrediente_id: int) -> bool:
        from app.modules.producto.link_models import ProductoIngrediente

        obj = self.session.get(self.model, ingrediente_id)
        if obj is None:
            return False

        self.session.exec(
            sql_delete(ProductoIngrediente).where(ProductoIngrediente.ingrediente_id == ingrediente_id)
        )
        self.session.expire(obj)

        self.session.delete(obj)
        self.session.flush()
        return True
