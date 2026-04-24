from __future__ import annotations

from decimal import Decimal

from app.core.uow import UnitOfWork
from app.modules.producto.link_models import ProductoCategoria, ProductoIngrediente
from app.modules.producto.model import Producto
from app.modules.producto.schema import (
    ProductoCategoriaCreate,
    ProductoCreate,
    ProductoIngredienteCreate,
    ProductoUpdate,
)


def _to_read_dict(producto: Producto) -> dict:
    categorias = [
        {"categoria": link.categoria, "es_principal": link.es_principal}
        for link in producto.categoria_links
    ]
    ingredientes = [
        {"ingrediente": link.ingrediente, "es_removible": link.es_removible}
        for link in producto.ingrediente_links
    ]
    return {
        "id": producto.id,
        "nombre": producto.nombre,
        "descripcion": producto.descripcion,
        "precio_base": producto.precio_base,
        "imagenes_url": producto.imagenes_url,
        "stock_cantidad": producto.stock_cantidad,
        "disponible": producto.disponible,
        "created_at": producto.created_at,
        "updated_at": producto.updated_at,
        "deleted_at": producto.deleted_at,
        "categorias": categorias,
        "ingredientes": ingredientes,
    }


def list_productos(
    uow: UnitOfWork,
    *,
    skip: int = 0,
    limit: int = 50,
    q: str | None = None,
    disponible: bool | None = None,
    precio_min: Decimal | None = None,
    precio_max: Decimal | None = None,
    incluir_eliminados: bool = False,
) -> list[dict]:
    productos = uow.productos.list_with_relations(
        skip=skip,
        limit=limit,
        q=q,
        disponible=disponible,
        precio_min=precio_min,
        precio_max=precio_max,
        incluir_eliminados=incluir_eliminados,
    )
    return [_to_read_dict(p) for p in productos]


def get_producto(uow: UnitOfWork, producto_id: int) -> dict | None:
    producto = uow.productos.get_with_relations(producto_id)
    if producto is None:
        return None
    return _to_read_dict(producto)


def _validate_categorias(
    uow: UnitOfWork,
    items: list[ProductoCategoriaCreate],
    *,
    producto_id: int | None = None,
) -> None:
    if not items:
        return
    ids = [i.categoria_id for i in items]
    if len(ids) != len(set(ids)):
        raise ValueError("Categorias duplicadas en el payload")
    principales = sum(1 for i in items if i.es_principal)
    if principales > 1:
        raise ValueError("Solo una categoria puede ser principal por producto")
    found = uow.categorias.active_ids(ids)
    allowed = set(found)
    if producto_id is not None:
        existing = {
            link.categoria_id for link in uow.productos.categoria_links(producto_id)
        }
        allowed |= existing.intersection(set(ids))
    missing = set(ids) - allowed
    if missing:
        raise ValueError(f"Categorias no encontradas o inactivas: {sorted(missing)}")


def _validate_ingredientes(
    uow: UnitOfWork,
    items: list[ProductoIngredienteCreate],
    *,
    producto_id: int | None = None,
) -> None:
    if not items:
        return
    ids = [i.ingrediente_id for i in items]
    if len(ids) != len(set(ids)):
        raise ValueError("Ingredientes duplicados en el payload")
    found = uow.ingredientes.active_ids(ids)
    allowed = set(found)
    if producto_id is not None:
        existing = {
            link.ingrediente_id for link in uow.productos.ingrediente_links(producto_id)
        }
        allowed |= existing.intersection(set(ids))
    missing = set(ids) - allowed
    if missing:
        raise ValueError(f"Ingredientes no encontrados o inactivos: {sorted(missing)}")


def _sync_categoria_links(
    uow: UnitOfWork, producto_id: int, desired: list[ProductoCategoriaCreate]
) -> None:
    _validate_categorias(uow, desired, producto_id=producto_id)
    desired_by_cat: dict[int, ProductoCategoriaCreate] = {
        item.categoria_id: item for item in desired
    }

    existing_by_cat: dict[int, ProductoCategoria] = {
        link.categoria_id: link for link in uow.productos.categoria_links(producto_id)
    }

    for cat_id, item in desired_by_cat.items():
        link = existing_by_cat.get(cat_id)
        if link is None:
            uow.productos.add_categoria_link(
                ProductoCategoria(
                    producto_id=producto_id,
                    categoria_id=cat_id,
                    es_principal=item.es_principal,
                )
            )
        else:
            link.es_principal = item.es_principal
            uow.productos.add_categoria_link(link)

    for cat_id, link in existing_by_cat.items():
        if cat_id not in desired_by_cat:
            uow.productos.remove_link(link)


def _sync_ingrediente_links(
    uow: UnitOfWork, producto_id: int, desired: list[ProductoIngredienteCreate]
) -> None:
    _validate_ingredientes(uow, desired, producto_id=producto_id)
    desired_by_ing: dict[int, ProductoIngredienteCreate] = {
        item.ingrediente_id: item for item in desired
    }

    existing_by_ing: dict[int, ProductoIngrediente] = {
        link.ingrediente_id: link
        for link in uow.productos.ingrediente_links(producto_id)
    }

    for ing_id, item in desired_by_ing.items():
        link = existing_by_ing.get(ing_id)
        if link is None:
            uow.productos.add_ingrediente_link(
                ProductoIngrediente(
                    producto_id=producto_id,
                    ingrediente_id=ing_id,
                    es_removible=item.es_removible,
                )
            )
        else:
            link.es_removible = item.es_removible
            uow.productos.add_ingrediente_link(link)

    for ing_id, link in existing_by_ing.items():
        if ing_id not in desired_by_ing:
            uow.productos.remove_link(link)


def create_producto(uow: UnitOfWork, data: ProductoCreate) -> dict:
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
        )
    )

    for item in data.categorias:
        uow.productos.add_categoria_link(
            ProductoCategoria(
                producto_id=producto.id,
                categoria_id=item.categoria_id,
                es_principal=item.es_principal,
            )
        )

    for item in data.ingredientes:
        uow.productos.add_ingrediente_link(
            ProductoIngrediente(
                producto_id=producto.id,
                ingrediente_id=item.ingrediente_id,
                es_removible=item.es_removible,
            )
        )

    uow.productos.flush()
    reloaded = get_producto(uow, producto.id)
    assert reloaded is not None
    return reloaded


def update_producto(
    uow: UnitOfWork, producto_id: int, data: ProductoUpdate
) -> dict | None:
    producto = uow.productos.get(producto_id)
    if producto is None:
        return None

    scalar_fields = data.model_dump(
        exclude_unset=True, exclude={"categorias", "ingredientes"}
    )
    for field, value in scalar_fields.items():
        setattr(producto, field, value)

    if data.categorias is not None:
        _sync_categoria_links(uow, producto_id, data.categorias)

    if data.ingredientes is not None:
        _sync_ingrediente_links(uow, producto_id, data.ingredientes)

    uow.productos.save(producto)
    return get_producto(uow, producto_id)


def delete_producto(uow: UnitOfWork, producto_id: int) -> bool:
    return uow.productos.soft_delete(producto_id)
