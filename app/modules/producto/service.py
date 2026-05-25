from __future__ import annotations

from typing import Optional

from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError

from app.core.uow import UnitOfWork
from app.modules.producto.link_models import ProductoCategoria, ProductoIngrediente
from app.modules.producto.model import Producto
from app.modules.producto.schema import (
    ProductoCategoriaCreate,
    ProductoCategoriaRead,
    ProductoCreate,
    ProductoIngredienteCreate,
    ProductoIngredienteRead,
    ProductoRead,
    ProductoUpdate,
)
from app.modules.unidad_medida.schema import UnidadMedidaRead


def _to_read(producto: Producto) -> ProductoRead:
    return ProductoRead(
        id=producto.id,
        nombre=producto.nombre,
        descripcion=producto.descripcion,
        precio_base=producto.precio_base,
        imagenes_url=producto.imagenes_url,
        stock_cantidad=producto.stock_cantidad,
        disponible=producto.disponible,
        created_at=producto.created_at,
        updated_at=producto.updated_at,
        deleted_at=producto.deleted_at,
        unidad_venta_id=producto.unidad_venta_id,
        unidad_venta=(
            UnidadMedidaRead.model_validate(producto.unidad_venta)
            if producto.unidad_venta is not None
            else None
        ),
        categorias=[ProductoCategoriaRead.model_validate(l) for l in producto.categoria_links],
        ingredientes=[ProductoIngredienteRead.model_validate(l) for l in producto.ingrediente_links],
    )


def list_productos(
    *,
    skip: int = 0,
    limit: int = 50,
) -> list[ProductoRead]:
    with UnitOfWork() as uow:
        productos = uow.productos.list_with_relations(skip=skip, limit=limit)
        return [_to_read(p) for p in productos]


def set_disponibilidad(producto_id: int, disponible: bool) -> ProductoRead:
    with UnitOfWork() as uow:
        producto = uow.productos.get(producto_id)
        if producto is None:
            raise HTTPException(status_code=404, detail="Producto no encontrado")
        producto.disponible = disponible
        uow.productos.save(producto)
        return _to_read(uow.productos.get_with_relations(producto_id))


def set_stock(producto_id: int, stock_cantidad: int) -> ProductoRead:
    with UnitOfWork() as uow:
        producto = uow.productos.get(producto_id)
        if producto is None:
            raise HTTPException(status_code=404, detail="Producto no encontrado")
        producto.stock_cantidad = stock_cantidad
        uow.productos.save(producto)
        return _to_read(uow.productos.get_with_relations(producto_id))


def get_producto(producto_id: int) -> ProductoRead:
    with UnitOfWork() as uow:
        producto = uow.productos.get_with_relations(producto_id)
        if producto is None:
            raise HTTPException(status_code=404, detail="Producto no encontrado")
        return _to_read(producto)


def _validate_categorias(uow, items, *, producto_id: Optional[int] = None) -> None:
    if not items:
        return
    ids = [i.categoria_id for i in items]
    if len(ids) != len(set(ids)):
        raise ValueError("Categorias duplicadas en el payload")
    if sum(1 for i in items if i.es_principal) > 1:
        raise ValueError("Solo una categoria puede ser principal por producto")
    allowed = set(uow.categorias.active_ids(ids))
    if producto_id is not None:
        existing = {l.categoria_id for l in uow.productos.categoria_links(producto_id)}
        allowed |= existing.intersection(set(ids))
    missing = set(ids) - allowed
    if missing:
        raise ValueError(f"Categorias no encontradas o inactivas: {sorted(missing)}")


def _validate_ingredientes(uow, items, *, producto_id: Optional[int] = None) -> None:
    if not items:
        return
    ids = [i.ingrediente_id for i in items]
    if len(ids) != len(set(ids)):
        raise ValueError("Ingredientes duplicados en el payload")
    allowed = set(uow.ingredientes.active_ids(ids))
    if producto_id is not None:
        existing = {l.ingrediente_id for l in uow.productos.ingrediente_links(producto_id)}
        allowed |= existing.intersection(set(ids))
    missing = set(ids) - allowed
    if missing:
        raise ValueError(f"Ingredientes no encontrados o inactivos: {sorted(missing)}")


def _sync_categoria_links(uow, producto_id, desired) -> None:
    _validate_categorias(uow, desired, producto_id=producto_id)
    desired_by_cat = {item.categoria_id: item for item in desired}
    existing_by_cat = {l.categoria_id: l for l in uow.productos.categoria_links(producto_id)}
    for cat_id, item in desired_by_cat.items():
        link = existing_by_cat.get(cat_id)
        if link is None:
            uow.productos.add_categoria_link(
                ProductoCategoria(producto_id=producto_id, categoria_id=cat_id, es_principal=item.es_principal)
            )
        else:
            link.es_principal = item.es_principal
            uow.productos.add_categoria_link(link)
    for cat_id, link in existing_by_cat.items():
        if cat_id not in desired_by_cat:
            uow.productos.remove_link(link)


def _sync_ingrediente_links(uow, producto_id, desired) -> None:
    _validate_ingredientes(uow, desired, producto_id=producto_id)
    desired_by_ing = {item.ingrediente_id: item for item in desired}
    existing_by_ing = {l.ingrediente_id: l for l in uow.productos.ingrediente_links(producto_id)}
    for ing_id, item in desired_by_ing.items():
        link = existing_by_ing.get(ing_id)
        if link is None:
            uow.productos.add_ingrediente_link(
                ProductoIngrediente(
                    producto_id=producto_id,
                    ingrediente_id=ing_id,
                    es_removible=item.es_removible,
                    cantidad=item.cantidad,
                    unidad_medida_id=item.unidad_medida_id,
                )
            )
        else:
            link.es_removible = item.es_removible
            link.cantidad = item.cantidad
            link.unidad_medida_id = item.unidad_medida_id
            uow.productos.add_ingrediente_link(link)
    for ing_id, link in existing_by_ing.items():
        if ing_id not in desired_by_ing:
            uow.productos.remove_link(link)


def create_producto(data: ProductoCreate) -> ProductoRead:
    try:
        with UnitOfWork() as uow:
            _validate_categorias(uow, data.categorias)
            _validate_ingredientes(uow, data.ingredientes)
            producto = uow.productos.save(
                Producto(
                    nombre=data.nombre,
                    descripcion=data.descripcion,
                    precio_base=data.precio_base,
                    imagenes_url=list(data.imagenes_url),
                    stock_cantidad=data.stock_cantidad,
                    disponible=data.disponible,
                    unidad_venta_id=data.unidad_venta_id, 
                )
            )
            for item in data.categorias:
                uow.productos.add_categoria_link(
                    ProductoCategoria(producto_id=producto.id, categoria_id=item.categoria_id, es_principal=item.es_principal)
                )
            for item in data.ingredientes:
                uow.productos.add_ingrediente_link(
                    ProductoIngrediente(
                        producto_id=producto.id,
                        ingrediente_id=item.ingrediente_id,
                        es_removible=item.es_removible,
                        cantidad=item.cantidad,
                        unidad_medida_id=item.unidad_medida_id,
                    )
                )
            uow.productos.flush()
            return _to_read(uow.productos.get_with_relations(producto.id))
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except IntegrityError:
        raise HTTPException(status_code=409, detail="Conflicto de datos del producto")


def update_producto(producto_id: int, data: ProductoUpdate) -> ProductoRead:
    try:
        with UnitOfWork() as uow:
            producto = uow.productos.get(producto_id)
            if producto is None:
                raise HTTPException(status_code=404, detail="Producto no encontrado")
            scalar_fields = data.model_dump(exclude_unset=True, exclude={"categorias", "ingredientes"})
            for field, value in scalar_fields.items():
                setattr(producto, field, value)
            if data.categorias is not None:
                _sync_categoria_links(uow, producto_id, data.categorias)
            if data.ingredientes is not None:
                _sync_ingrediente_links(uow, producto_id, data.ingredientes)
            uow.productos.save(producto)
            return _to_read(uow.productos.get_with_relations(producto_id))
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except IntegrityError:
        raise HTTPException(status_code=409, detail="Conflicto de datos del producto")


def delete_producto(producto_id: int) -> None:
    with UnitOfWork() as uow:
        if not uow.productos.soft_delete(producto_id):
            raise HTTPException(status_code=404, detail="Producto no encontrado")
