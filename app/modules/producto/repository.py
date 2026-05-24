from __future__ import annotations

from decimal import Decimal
from typing import Optional, Union

from sqlalchemy.orm import selectinload
from sqlmodel import select

from app.core.repository import BaseRepository
from app.modules.producto.link_models import ProductoCategoria, ProductoIngrediente
from app.modules.producto.model import Producto


class ProductoRepository(BaseRepository[Producto]):
    model = Producto

    def _with_relations(self, *, include_deleted: bool = False):
        return self.base_stmt(include_deleted=include_deleted).options(
            selectinload(Producto.categoria_links).selectinload(ProductoCategoria.categoria),
            selectinload(Producto.ingrediente_links).selectinload(ProductoIngrediente.ingrediente),
        )

    def get_with_relations(self, producto_id: int) -> Optional[Producto]:
        stmt = self._with_relations(include_deleted=True).where(Producto.id == producto_id)
        return self.session.exec(stmt).first()

    def list_with_relations(
        self,
        *,
        skip: int = 0,
        limit: int = 50,
        q: Optional[str] = None,
        disponible: Optional[bool] = None,
        precio_min: Optional[Decimal] = None,
        precio_max: Optional[Decimal] = None,
        incluir_eliminados: bool = False,
    ) -> list[Producto]:
        stmt = self._with_relations(include_deleted=incluir_eliminados)
        if q:
            stmt = stmt.where(Producto.nombre.ilike(f"%{q}%"))
        if disponible is not None:
            stmt = stmt.where(Producto.disponible == disponible)
        if precio_min is not None:
            stmt = stmt.where(Producto.precio_base >= precio_min)
        if precio_max is not None:
            stmt = stmt.where(Producto.precio_base <= precio_max)
        stmt = stmt.offset(skip).limit(limit).order_by(Producto.id)
        return list(self.session.exec(stmt).all())

    def categoria_links(self, producto_id: int) -> list[ProductoCategoria]:
        stmt = select(ProductoCategoria).where(ProductoCategoria.producto_id == producto_id)
        return list(self.session.exec(stmt).all())

    def ingrediente_links(self, producto_id: int) -> list[ProductoIngrediente]:
        stmt = select(ProductoIngrediente).where(ProductoIngrediente.producto_id == producto_id)
        return list(self.session.exec(stmt).all())

    def add_categoria_link(self, link: ProductoCategoria) -> None:
        self.session.add(link)

    def add_ingrediente_link(self, link: ProductoIngrediente) -> None:
        self.session.add(link)

    def remove_link(self, link: Union[ProductoCategoria, ProductoIngrediente]) -> None:
        self.session.delete(link)

    def flush(self) -> None:
        self.session.flush()
